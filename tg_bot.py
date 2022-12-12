import os
import logging
import redis
import requests
import textwrap

from functools import partial
from dotenv import load_dotenv

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Filters, Updater
from telegram.ext import CallbackQueryHandler, CommandHandler, MessageHandler

from teleshop import add_to_cart, choose_cart_items_details
from teleshop import create_customer, get_access_token
from teleshop import delete_from_cart, get_cart_items, get_img_link, get_price
from teleshop import get_products, get_product_details, validate_customer_data


logger = logging.getLogger(__name__)


def start(redis_call, update, context):
    access_token = get_access_token(redis_call)
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
    context.bot.send_message(
        text='Привет!Мы продаём рыбов. Смотрите. Красивое',
        chat_id=update.effective_user.id,
        reply_markup=reply_markup
        )
    return 'HANDLE_MENU'


def handle_menu(redis_call, update, context):
    access_token = get_access_token(redis_call)
    query = update.callback_query
    query.answer()
    query.message.delete()
    button_names = ['1', '5', '10', 'Корзина', 'В меню']
    keyboard = [[
        InlineKeyboardButton(button_name,
                             callback_data=f'{button_name},{query.data}')
        ]for button_name in button_names]
    reply_markup = InlineKeyboardMarkup(keyboard)
    if query.data == 'Корзина':
        handle_cart(redis_call, update, context)
        return 'HANDLE_CART'
    product_details = get_product_details(access_token, query.data)
    msg = (f'''\
        {product_details['name']}
        {product_details['description']}
        {product_details['price']} за 1 кг
        {product_details['weight']} кг в 1 шт.
        ''')
    message = textwrap.dedent(msg)
    img_lnk = get_img_link(access_token, product_details['img_id'])
    context.bot.send_photo(chat_id=query.message.chat_id,
                           photo=img_lnk,
                           caption=message,
                           reply_markup=reply_markup)
    logger.info(message)
    return 'HANDLE_DESCRIPTION'


def handle_description(redis_call, update, context):
    access_token = get_access_token(redis_call)
    query = update.callback_query
    query.answer()
    chat_id = query.message.chat_id
    if 'В меню' in query.data:
        start(redis_call, update, context)
        query.message.delete()
        return 'HANDLE_MENU'
    elif query.data.split(',')[0] == 'Корзина':
        handle_cart(redis_call, update, context)
        query.message.delete()
        return 'HANDLE_CART'
    else:
        quantity = int(query.data.split(',')[0])
        product_id = query.data.split(',')[1]
        add_to_cart(access_token,
                    str(chat_id),
                    product_id,
                    quantity)
        context.bot.send_message(text='добавлено в корзину',
                                 chat_id=chat_id)
        return 'HANDLE_DESCRIPTION'


def handle_cart(redis_call, update, context):
    access_token = get_access_token(redis_call)
    query = update.callback_query
    query.answer()
    chat_id = update.effective_user.id
    keyboard = [[InlineKeyboardButton('В меню', callback_data='В меню')]]
    cart_items = get_cart_items(access_token, str(chat_id))
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
        start(redis_call, update, context)
        query.message.delete()
        return 'START'

    elif query.data.split(',')[0] == 'Удалить':
        delete_from_cart(access_token,
                         str(chat_id),
                         query.data.split(',')[1])
        context.bot.send_message(text='удалено из корзины',
                                 chat_id=chat_id)
        return 'HANDLE_DESCRIPTION'

    keyboard.append([InlineKeyboardButton('Оплатить',
                                          callback_data='Оплатить')])
    cart_details = choose_cart_items_details(cart_items)
    keyboard.append([
        InlineKeyboardButton(
            f'''Удалить {cart_detail['name']}''',
            callback_data=f'''Удалить,{cart_detail['product_id']}'''
            ) for cart_detail in cart_details
        ])
    reply_markup = InlineKeyboardMarkup(keyboard)
    msg = create_cart_message(cart_details, price)
    context.bot.send_message(text=msg,
                             chat_id=chat_id,
                             reply_markup=reply_markup)


def waiting_email(redis_call, update, context):
    msg = update.message
    e_mail = msg.text
    chat_id = msg.chat.id
    access_token = get_access_token(redis_call)
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


def create_cart_message(cart_items_details, price):
    msgs = []
    for cart_items_detail in cart_items_details:
        name = cart_items_detail['name']
        quantity = cart_items_detail['quantity']
        value_amount = cart_items_detail['value_amount']
        msg = f'''
              Вы покупаете {name}
              {quantity} кг
              Стоимость {value_amount}
              '''
        msgs.append(msg)
    msgs.append(f'Общая стоимость {price}')
    msg = ' '.join(msgs)
    return textwrap.dedent(msg)


def handle_users_reply(redis_call, update, context):

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
        user_state = redis_call.get(chat_id).decode('utf-8')

    states_functions = {
        'START': partial(start, redis_call),
        'HANDLE_MENU': partial(handle_menu, redis_call),
        'HANDLE_DESCRIPTION': partial(handle_description, redis_call),
        'HANDLE_CART': partial(handle_cart, redis_call),
        'WAITING_EMAIL': partial(waiting_email, redis_call)
        }
    state_handler = states_functions[user_state]
    try:
        next_state = state_handler(update, context)
        redis_call.set(chat_id, next_state)
    except Exception as err:
        logger.info(err)


def start_bot():
    load_dotenv()
    token = os.getenv('TG_TOKEN')
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO)

    updater = Updater(token)
    redis_call = redis.Redis(host=os.getenv('REDIS_ENDPOINT'),
                             port=os.getenv('REDIS_PORT'),
                             password=os.getenv('REDIS_PASSWORD'))

    dispatcher = updater.dispatcher
    dispatcher.add_handler(CallbackQueryHandler(
        partial(handle_users_reply, redis_call))
                           )
    dispatcher.add_handler(CallbackQueryHandler(
        partial(handle_menu, redis_call))
                           )
    dispatcher.add_handler(MessageHandler(
        Filters.text, partial(handle_users_reply, redis_call))
                           )
    dispatcher.add_handler(CommandHandler(
        'start', partial(handle_users_reply, redis_call))
                           )
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    start_bot()
