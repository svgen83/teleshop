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
from teleshop import get_img_link


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
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('Привет!Мы продаём рыбов, а не только показываем!',
    reply_markup=reply_markup)
    return 'HANDLE_MENU'
    
    
def handle_menu(update, context):
    query = update.callback_query
    query.answer()
    query.message.delete()
    #pprint(query.data)
    access_token = get_access_token()
    product_details = get_product_details(access_token, query.data)
    message = create_message(product_details)
    img_lnk = get_img_link(access_token, product_details['img_id'])
    logger.info(message)
    #query.edit_message_text(text=message)
    context.bot.send_photo(chat_id=query.message.chat_id, photo=img_lnk,
                           caption=message)
                            #chat_id=query.message.chat_id,
                           # message_id=query.message.message_id)
    return 'HANDLE_MENU'


def create_message(product_details):
    msg = (
        f'''\
        {product_details['name']}
        {product_details['description']}
        {product_details['price']} за 1 кг
        {product_details['weight']} кг в 1 шт.
        ''')
    return textwrap.dedent(msg)



def echo(update, context):
    """
    Хэндлер для состояния ECHO.
    
    Бот отвечает пользователю тем же, что пользователь ему написал.
    Оставляет пользователя в состоянии ECHO.
    """
    users_reply = update.message.text
    update.message.reply_text(users_reply)
    return "ECHO"


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
        'ECHO': echo,
        'HANDLE_MENU': handle_menu
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
    token = os.getenv("TG_TOKEN")
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
