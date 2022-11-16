from dotenv import load_dotenv

import os
import logging
import redis
import textwrap

from pprint import pprint

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Filters, Updater
from telegram.ext import CallbackQueryHandler, CommandHandler, MessageHandler
from teleshop import get_access_token, get_products, get_product_details
from teleshop import get_img_link, create_cart, add_to_cart, get_cart, get_cart_items
from teleshop import choose_cart_items_details, delete_from_cart, create_customer, get_customers

_database = None

logger = logging.getLogger(__name__)


def start(update, context):
    access_token = get_access_token()
    products = get_products(access_token)
    keyboard = []
    for product in products:
        button = [
          InlineKeyboardButton(product['name'], callback_data=product['id'])
                 ]
        keyboard.append(button)
    keyboard.append([InlineKeyboardButton('Корзина', callback_data='Корзина')])
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
        watch_cart(update, context)
        #query.message.delete()
        return 'HANDLE_CART'
    product_details = get_product_details(access_token, query.data)
    message = create_message(product_details)
    img_lnk = get_img_link(access_token, product_details['img_id'])
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
        watch_cart(update, context)
        query.message.delete()
        return 'HANDLE_CART'
    else:
        quantity = int(query.data.split(',')[0])
        product_id = query.data.split(',')[-1]
        add_to_cart(access_token, str(chat_id), product_id, quantity)
        context.bot.send_message(text='добавлено в корзину', chat_id=chat_id)
        return 'HANDLE_DESCRIPTION'


def watch_cart(update,context):
    access_token = get_access_token()
    query = update.callback_query
    query.answer()
    chat_id = update.effective_user.id
    keyboard = [[InlineKeyboardButton('Оплатить', callback_data='Оплатить')],
              [InlineKeyboardButton('В меню', callback_data='В меню')]]
    print(get_cart(access_token, str(chat_id)))
    cart_items = get_cart_items(access_token, str(chat_id))
    cart_details = choose_cart_items_details(cart_items)
    for cart_detail in cart_details:
        button = [InlineKeyboardButton(
                 f'''Удалить {cart_detail['name']}''',
                 callback_data=f'''Удалить,{cart_detail['product_id']}'''
                                      )]
        keyboard.append(button)
    reply_markup = InlineKeyboardMarkup(keyboard)
    msgs = create_msgs_for_cart(cart_details)
    msg = " ".join(msgs)
    context.bot.send_message(text=msg, chat_id=chat_id,
                             reply_markup=reply_markup)


def handle_cart(update, context):
    access_token = get_access_token()
    query = update.callback_query
    query.answer()
    chat_id = query.message.chat_id
    if query.data == 'Оплатить':
        query.message.delete()
        message = "Пришлите свою электронную почту"      
        context.bot.send_message(text=message,
                             chat_id=chat_id)
        return 'WAITING_EMAIL'
    elif query.data == 'В меню':
        start(update, context)
        query.message.delete()
        return 'START'
    elif query.data.split(',')[0] == 'Удалить':
        delete_from_cart(access_token, str(chat_id))
        context.bot.send_message(text='удалено из корзины', chat_id=chat_id)
        #query.message.delete()
        return 'HANDLE_CART'


def waiting_email(update, context):
    msg = update.message
    e_mail = msg.text
    chat_id = msg.chat.id
    access_token = get_access_token()
    #customers = get_customers(access_token)
    #for customer in customers:
     #   if customer[str(chat_id)]:
      #      message = "Пользователь с таким именем уже зарегистирован"
       # else:   
    try:
      create_customer(access_token, str(chat_id), e_mail)
      message = "Вы успешно зарегистрированы. свяжемся с вами по e-mail"
    except:
      message = "Вы ранее регистрировались"    
    finally:
      context.bot.send_message(text=message,
                             chat_id=chat_id)
      return 'HANDLE_DESCRIPTION'
    
                      

def create_msgs_for_cart(cart_items_details):
    msgs = []
    for cart_items_detail in cart_items_details:
        name = cart_items_detail['name']
        quantity = cart_items_detail['quantity']
        value_amount = cart_items_detail['value_amount']
        value_currency = cart_items_detail['value_currency']
        msg = textwrap.dedent(f"""
                               Вы покупате {name}
                               {quantity} кг
                               Стоимость {value_amount} {value_currency}
                               """)
        msgs.append(msg)
    return msgs


def create_message(product_details):
    msg = (f'''\
        {product_details['name']}
        {product_details['description']}
        {product_details['price']} за 1 кг
        {product_details['weight']} кг в 1 шт.
        ''')
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
        user_state = db.get(chat_id).decode("utf-8")
    
    states_functions = {
        'START': start,
        'HANDLE_MENU': handle_menu,
        'HANDLE_DESCRIPTION': handle_description,
        'HANDLE_CART': handle_cart,
        'WAITING_EMAIL': waiting_email}
    state_handler = states_functions[user_state]
  # Если вы вдруг не заметите, что python-telegram-bot перехватывает ошибки.
  # Оставляю этот try...except, чтобы код не падал молча.
  # Этот фрагмент можно переписать.
    try:
        next_state = state_handler(update, context)
        db.set(chat_id, next_state)
    except Exception as err:
        print(err)


def get_database_connection():
    global _database
    if _database is None:
        database_password = os.getenv("REDIS_PASSWORD")
        database_host = os.getenv("REDIS_ENDPOINT")
        database_port = os.getenv("REDIS_PORT")
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
    dispatcher.add_handler(MessageHandler(Filters.text, handle_users_reply))
    dispatcher.add_handler(CommandHandler('start', handle_users_reply))
    updater.start_polling()
    updater.idle()
