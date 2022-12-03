from dotenv import load_dotenv

import os
import logging
import redis
import requests
import textwrap

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Filters, Updater
from telegram.ext import CallbackQueryHandler, CommandHandler, MessageHandler
from teleshop import add_to_cart, create_cart, create_customer
from teleshop import choose_cart_items_details, get_access_token, get_cart_items 
from teleshop import get_img_link, get_price, get_products, get_product_details
from teleshop import delete_from_cart, validate_customer_data

_database = None

logger = logging.getLogger(__name__)


def start(update, context):
    access_token = get_access_token()
    products = get_products(access_token)
    keyboard = []
    for product in products:
        button = [
          InlineKeyboardButton(product['name'],
                              callback_data=product['id'])
          ]
        keyboard.append(button)
    keyboard.append([InlineKeyboardButton('Корзина',
                                          callback_data='Корзина')])
    reply_markup = InlineKeyboardMarkup(keyboard)
    context.bot.send_message(text='Привет!Мы продаём рыбов. Смотрите. Красивое',
                            chat_id=update.effective_user.id,
                            reply_markup=reply_markup)
    return 'HANDLE_MENU'


def handle_menu(update, context):
    access_token = get_access_token()
    query = update.callback_query
    query.answer()
    query.message.delete()
    keyboard = []
    button_names = ['1', '5', '10', 'Корзина', 'В меню']
    for button_name in button_names:
        button = [
            InlineKeyboardButton(button_name,
                                 callback_data=f'{button_name},{query.data}')
            ]
        keyboard.append(button)
    reply_markup = InlineKeyboardMarkup(keyboard)
    if query.data == 'Корзина':
        handle_cart(update, context)
        return 'HANDLE_CART'
    product_details = get_product_details(access_token, query.data)
    msg = (f'''\
          {product_details['name']}
          {product_details['description']}
          {product_details['price']} за 1 кг
          {product_details['weight']} кг в 1 шт.
          ''')
    message = textwrap.dedent(msg)
    img_lnk = get_img_link(access_token,
                           product_details['img_id'])
    context.bot.send_photo(chat_id=query.message.chat_id,
                          photo=img_lnk,
                          caption=message,
                          reply_markup=reply_markup)
    logger.info(message)
    return 'HANDLE_DESCRIPTION'


def handle_description(update, context):
    access_token = get_access_token()
    query = update.callback_query
    query.answer()
    chat_id = query.message.chat_id
    if 'В меню' in query.data:
        start(update, context)
        query.message.delete()
        return 'HANDLE_MENU'
    elif query.data.split(',')[0] == 'Корзина':
        handle_cart(update, context)
        query.message.delete()
        return 'HANDLE_CART'
    else:
        quantity = int(query.data.split(',')[0])
        product_id = query.data.split(',')[1]
        add_to_cart(access_token, str(chat_id),
                    product_id, quantity)
        context.bot.send_message(text='добавлено в корзину',
                                 chat_id=chat_id)
        return 'HANDLE_DESCRIPTION'


def handle_cart(update, context):
    access_token = get_access_token()
    query = update.callback_query
    query.answer()
    chat_id = update.effective_user.id
    keyboard = [[InlineKeyboardButton('В меню',
                                      callback_data='В меню')]]
    cart_items = get_cart_items(access_token,
                                str(chat_id))
    price = get_price(access_token, str(chat_id))

    if not cart_items:
        query.message.delete()
        reply_markup = InlineKeyboardMarkup(keyboard)
        context.bot.send_message(text='Корзина пуста',
                              chat_id=chat_id,
                              reply_markup=reply_markup)
        return 'HANDLE_DESCRIPTION'

  if query.data == 'Оплатить':
      query.message.delete()
      message = 'Пришлите свою электронную почту'
      context.bot.send_message(text=message,
                               chat_id=chat_id)
      return 'WAITING_EMAIL'

  elif query.data == 'В меню':
      start(update, context)
      query.message.delete()
      return 'START'

  elif query.data.split(',')[0] == 'Удалить':
      delete_from_cart(access_token, str(chat_id),
                       query.data.split(',')[1])
      context.bot.send_message(text='удалено из корзины',
                               chat_id=chat_id)
      return 'HANDLE_DESCRIPTION'

    keyboard.append([InlineKeyboardButton('Оплатить', callback_data='Оплатить')])
    cart_details = choose_cart_items_details(cart_items)
    keyboard.append([InlineKeyboardButton(
              f'''Удалить {cart_detail['name']}''',
              callback_data=f'''Удалить,{cart_detail['product_id']}''')
                    ] for cart_detail in cart_details)
    reply_markup = InlineKeyboardMarkup(keyboard)
    msg = create_cart_msg(cart_details, price)
    context.bot.send_message(text=msg,
                             chat_id=chat_id,
                             reply_markup=reply_markup)


def waiting_email(update, context):
    msg = update.message
    e_mail = msg.text
    chat_id = msg.chat.id
    access_token = get_access_token()
    keyboard = [[InlineKeyboardButton('В меню',
                                      callback_data='В меню')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    try:
        create_customer(access_token,
                        str(chat_id),
                        e_mail)
        message = validate_customer_data(access_token,
                                         str(chat_id))
    except requests.exceptions.HTTPError:
        message = 'Вы ранее регистрировались'
    finally:
        context.bot.send_message(text=message,
                                chat_id=chat_id,
                                reply_markup=reply_markup)
        return 'HANDLE_DESCRIPTION'


def create_cart_msg(cart_items_details, price):
    msgs = []
    for cart_items_detail in cart_items_details:
        name = cart_items_detail['name']
        quantity = cart_items_detail['quantity']
        value_amount = cart_items_detail['value_amount']
        msg = f'
                  Вы покупаете {name}
                  {quantity} кг
                  Стоимость {value_amount}
                  '
        msgs.append(msg)
    msgs.append(f'Общая стоимость {price}')
    msg = ' '.join(msgs)
    return textwrap.dedent(msg)


def handle_users_reply(update, context):

    db = get_database_connection()
    if update.message:
        user_reply = update.message.text
        chat_id = update.message.chat_id
    elif update.callback_query:
        user_reply = update.callback_query.data
        chat_id = update.callback_query.message.chat_id
    else:
        return
    if user_reply == '/start':
        user_state = 'START'
    else:
        user_state = db.get(chat_id).decode('utf-8')

    states_functions = {
        'START': start,
        'HANDLE_MENU': handle_menu,
        'HANDLE_DESCRIPTION': handle_description,
        'HANDLE_CART': handle_cart,
        'WAITING_EMAIL': waiting_email
        }
    state_handler = states_functions[user_state]
    try:
        next_state = state_handler(update, context)
        db.set(chat_id, next_state)
    except Exception as err:
        logger.info(err)


def get_database_connection():
    global _database
    if _database is None:
        database_password = os.getenv('REDIS_PASSWORD')
        database_host = os.getenv('REDIS_ENDPOINT')
        database_port = os.getenv('REDIS_PORT')
        _database = redis.Redis(host=database_host,
                              port=database_port,
                              password=database_password)
        return _database


if __name__ == '__main__':

    load_dotenv()
    token = os.getenv('TG_TOKEN')
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO)

    updater = Updater(token)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CallbackQueryHandler(handle_users_reply))
    dispatcher.add_handler(CallbackQueryHandler(handle_menu))
    dispatcher.add_handler(MessageHandler(Filters.text,
                                          handle_users_reply))
    dispatcher.add_handler(CommandHandler('start',
                                          handle_users_reply))
    updater.start_polling()
    updater.idle()
