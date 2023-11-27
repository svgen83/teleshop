import os
import logging
import requests
import textwrap
import json

from upstash_redis import Redis
from dotenv import load_dotenv
from functools import partial

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, InputMediaPhoto
from telegram.ext import Filters, Updater
from telegram.ext import CallbackQueryHandler, CommandHandler, MessageHandler

from cms import get_products, get_product, get_image_url
from cms import load_image, get_cart_product_details, get_carts, get_cart_details
from cms import add_to_cart, delete_from_cart, get_or_create_user_cart
from cms import get_or_create_customer


logger = logging.getLogger(__name__)


def start(cms_token, update, context):
    products = get_products(cms_token)
    keyboard = []
    for product in products:
        button = [
            InlineKeyboardButton(product['attributes']['title'],
                                 callback_data=product['id'])
            ]
        keyboard.append(button)
    keyboard.append([InlineKeyboardButton('Корзина',
                                          callback_data='Корзина')])    
    reply_markup = InlineKeyboardMarkup(keyboard)
    context.bot.send_message(text='Пожалуйста, выбирайте:',
                             chat_id=update.effective_user.id,
                             reply_markup=reply_markup)
    return "HANDLE_MENU"


def handle_menu(cms_token, update, context):
    query = update.callback_query
    query.answer()
    query.message.delete()
    chat_id = query.message.chat_id
    button_names = ['1', '2', '3', 'Корзина', 'В меню']
    keyboard = [[
        InlineKeyboardButton(button_name,
                             callback_data=f'{button_name},{query.data}')
        ] for button_name in button_names]
    reply_markup = InlineKeyboardMarkup(keyboard)
    if query.data == 'Корзина':
        handle_cart(cms_token, update, context)
        return 'HANDLE_CART'
    
    product = get_product(cms_token, query.data)
    msg = textwrap.dedent(product['attributes']['description'])
    
    img_lnk = get_image_url(cms_token, query.data)
    product_image = load_image(img_lnk, cms_token, query.data)
    with open(product_image, 'rb') as image:
        context.bot.send_photo(
            chat_id=query.message.chat_id,
            photo=image,
            caption=msg,
            reply_markup=reply_markup)
        logger.info(msg)
    return 'HANDLE_DESCRIPTION'


def handle_description(cms_token, update, context):
    query = update.callback_query
    query.answer()
    chat_id = query.message.chat_id
    if 'В меню' in query.data:
        start(cms_token, update, context)
        query.message.delete()
        return 'HANDLE_MENU'
    elif query.data.split(',')[0] == 'Корзина':
        handle_cart(cms_token, update, context)
        query.message.delete()
        return 'HANDLE_CART'
    else:
        quantity = int(query.data.split(',')[0])
        product_id = int(query.data.split(',')[1])
        user_cart = get_or_create_user_cart(cms_token, chat_id)
        add_to_cart(cms_token, user_cart['id'], product_id, quantity)
        context.bot.send_message(text='добавлено в корзину',
                                 chat_id=chat_id)
        return 'HANDLE_DESCRIPTION'


def handle_cart(cms_token, update, context):
    query = update.callback_query
    query.answer()
    chat_id = update.effective_user.id
    keyboard = [[InlineKeyboardButton('В меню', callback_data='В меню')]]
    user_cart = get_or_create_user_cart(cms_token, chat_id)
    cart_details = get_cart_details(user_cart, cms_token)
    if not cart_details:
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
        start(cms_token, update, context)
        query.message.delete()
        return 'START'

    elif query.data.split(',')[0] == 'Удалить':
        delete_from_cart(cms_token, query.data.split(',')[1])
        context.bot.send_message(text='удалено из корзины',
                                 chat_id=chat_id)
        return 'HANDLE_DESCRIPTION'

    keyboard.append([InlineKeyboardButton(
                f'''Удалить {cart_detail['title']}''',
                callback_data=f'''Удалить,{cart_detail['product_id']}'''
            ) for cart_detail in cart_details])
    keyboard.append([InlineKeyboardButton('Оплатить',
                                          callback_data='Оплатить')])
    reply_markup = InlineKeyboardMarkup(keyboard)
    msg = create_cart_message(cart_details)
    context.bot.send_message(text=msg,
                             chat_id=chat_id,
                             reply_markup=reply_markup)
    return 'HANDLE_DESCRIPTION'



def waiting_email(cms_token, update, context):
    msg = update.message
    e_mail = msg.text
    chat_id = msg.chat.id
    keyboard = [[InlineKeyboardButton('В меню',
                                      callback_data='В меню')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    try:
        message = get_or_create_customer(cms_token, str(chat_id), e_mail)
    except requests.exceptions.HTTPError:
        message = 'Вы ранее регистрировались'
    finally:
        context.bot.send_message(text=message,
                                 chat_id=chat_id,
                                 reply_markup=reply_markup)
        return 'HANDLE_DESCRIPTION'


def create_cart_message(cart_details):
    msgs = []
    price = 0
    for item in cart_details:
        msg = f'''
              Вы покупаете {item['title']}
              {item['quantity']} кг
              Стоимость {item['total_price']} рублей
              '''
        price = price + item['total_price']
        msgs.append(msg)
    msgs.append(f'Стоимость всех товаров {price} рублей')
    msg = ' '.join(msgs)
    return textwrap.dedent(msg)


def handle_users_reply(cms_token, update, context):
    redis_call = Redis(url=os.getenv('UPSTASH_REDIS_REST_URL'),
                       token=os.getenv('UPSTASH_REDIS_REST_TOKEN'))
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
        user_state = redis_call.get(chat_id)

    states_functions = {
        'START': partial(start, cms_token),
        'HANDLE_MENU': partial(handle_menu, cms_token),
        'HANDLE_DESCRIPTION': partial(handle_description, cms_token),
        'HANDLE_CART': partial(handle_cart, cms_token),
        'WAITING_EMAIL': partial(waiting_email, cms_token)
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
    cms_token = os.getenv('CMS_TOKEN')
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO)

    updater = Updater(token)

    dispatcher = updater.dispatcher
    
    dispatcher.add_handler(CallbackQueryHandler(
        partial(handle_users_reply, cms_token))
                           )
    dispatcher.add_handler(CallbackQueryHandler(
        partial(handle_menu, cms_token))
                           )
    dispatcher.add_handler(MessageHandler(
        Filters.text, partial(handle_users_reply, cms_token))
                           )
    dispatcher.add_handler(CommandHandler(
        'start', partial(handle_users_reply, cms_token))
                           )
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    start_bot()
