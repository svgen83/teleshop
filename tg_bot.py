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
from teleshop import get_img_link, create_cart, add_to_cart, get_cart_items
from teleshop import choose_cart_items_details, delete_from_cart


_database = None

logger = logging.getLogger(__name__)


def start(update, context):
    access_token = get_access_token()
    products = get_products(access_token)
    keyboard = []
    for product in products:
        button = [InlineKeyboardButton(product['name'],
                                       callback_data=product['id'])]
        keyboard.append(button)
    keyboard.append([InlineKeyboardButton('Корзина',
                                          callback_data='Корзина')])
    reply_markup = InlineKeyboardMarkup(keyboard)
    context.bot.send_message(text='Привет!Мы продаём рыбов. Смотрите. Красивое',
                             chat_id=update.effective_user.id,
                             reply_markup=reply_markup)
    return 'HANDLE_MENU'
    
    
def handle_menu(update, context):
    query = update.callback_query
    query.answer()
    query.message.delete()
    keyboard = []
    button_names = ['1','5', '10', 'Корзина', 'Назад']
    for button_name in button_names:
        button = [InlineKeyboardButton(
                                       button_name,
                                       callback_data= f'{button_name},{query.data}'
                                       )]
        keyboard.append(button)
    reply_markup = InlineKeyboardMarkup(keyboard)
    access_token = get_access_token()
    product_details = get_product_details(access_token, query.data)
    message = create_message(product_details)
    img_lnk = get_img_link(access_token, product_details['img_id'])
    logger.info(message)
    #query.edit_message_text(text=message)
    context.bot.send_photo(chat_id=query.message.chat_id, photo=img_lnk,
                           caption=message, reply_markup=reply_markup)
                            #chat_id=query.message.chat_id,
                           # message_id=query.message.message_id)
    return 'HANDLE_DESCRIPTION'
    
    
def handle_description(update, context):
    access_token = get_access_token()
    query = update.callback_query
    query.answer()
    chat_id = query.message.chat_id
    if query.data.split(',')[0] == 'Назад':
        start(update, context)
        query.message.delete()
        return 'HANDLE_MENU'
    elif query.data.split(',')[0] == 'Корзина':
         query.message.delete()
         keyboard = [[InlineKeyboardButton('Оплатить', callback_data='Оплатить')],
                     [InlineKeyboardButton('В меню', callback_data='В меню')]]
      
         cart_items = get_cart_items(access_token, str(chat_id))
         cart_details = choose_cart_items_details(cart_items)
         print(cart_details)
         for cart_detail in cart_details:
            button = [InlineKeyboardButton(
                                       f'''Удалить {cart_detail['name']}''',
                                       callback_data= f'''{cart_detail['name']},
                                                       {cart_detail['product_id']}'''
                                       )]
            keyboard.append(button)   
         msgs = create_msgs_for_cart(cart_details)
         reply_markup = InlineKeyboardMarkup(keyboard)
         for msg in msgs:
            context.bot.send_message(text=msg,
                                     chat_id=chat_id,
                                     reply_markup=reply_markup)
         return 'HANDLE_DESCRIPTION'
    elif query.data == 'Оплатить': 
        context.bot.send_message(text='В разработке',
                                     chat_id=chat_id)
        return 'HANDLE_DESCRIPTION'
    else:
        quantity = int(query.data.split(',')[0])
        product_id = query.data.split(',')[1]
        print(product_id)
        add_to_cart(access_token, str(chat_id), product_id, quantity)
        context.bot.send_message(text='добавлено в корзину',
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
    msg = (
        f'''\
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
        'HANDLE_DESCRIPTION': handle_description
    }
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
    """
    Возвращает конекшн с базой данных Redis, либо создаёт новый, если он ещё не создан.
    """
    global _database
    if _database is None:
        database_password = os.getenv("REDIS_PASSWORD")
        database_host = os.getenv("REDIS_ENDPOINT")
        database_port = os.getenv("REDIS_PORT")
        _database = redis.Redis(host=database_host, port=database_port, password=database_password)
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
