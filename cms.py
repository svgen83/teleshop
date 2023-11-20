import io
import os
import requests
from dotenv import load_dotenv
from pprint import pprint
import json


load_dotenv()
cms_token = os.getenv("CMS_TOKEN")


def get_products(access_token):
    url = ''.join([os.getenv("CMS_SCHEME"), '/api/products'])
    headers = {'Authorization': access_token}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()['data']
    

def get_product(access_token, product_id):
    #url_template = os.getenv("CMS_SCHEME")
    url = ''.join([os.getenv("CMS_SCHEME"), '/api/products', f'/{product_id}'])
    headers = {'Authorization': access_token}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()['data']


def get_image_url(access_token, product_id):
    #url_template = os.getenv("CMS_URL")
    url = ''.join([os.getenv("CMS_SCHEME"), '/api/products', f'/{product_id}'])
    headers = {'Authorization': access_token}
    data = {'populate': 'picture'}
    response = requests.get(url, headers=headers, params = data)
    response.raise_for_status()
    img_url = response.json()[
        'data']['attributes']['picture'][
            'data'][0]['attributes']['url']
    return ''.join([os.getenv("CMS_SCHEME"), img_url])


def load_image(image_url, access_token, product_id):
    response =  requests.get(image_url, headers = {'Authorization': access_token})
    response.raise_for_status()
    image_path = f'{product_id}.jpg'
    with open(image_path, 'wb') as file:
      file.write(response.content)
    return image_path
    
def get_carts(access_token):
    url = ''.join([os.getenv("CMS_SCHEME"), '/api/carts'])
    headers = {'Authorization': access_token}
    data = {'populate': '*'}
    response = requests.get(url, headers=headers, params = data)
    response.raise_for_status()
    return response.json()['data']

def create_cart(access_token, chat_id):
    url = ''.join([os.getenv("CMS_SCHEME"), '/api/carts'])
    headers = {'Authorization': access_token}
    data = {'data':{'tg_id': chat_id}}
    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()
    return response.json()['data']


def get_cart_product(access_token, cart_product_id):
    url = ''.join([os.getenv("CMS_SCHEME"), f'/api/cart-products/{cart_product_id}'])
    headers = {'Authorization': access_token}
    data = {'populate': '*'}
    response = requests.get(url, headers=headers, params=data)
    response.raise_for_status()
    return response.json()['data']['attributes']['product']['data']['attributes']

def add_product_to_cart_products(access_token, product_id, quantity, cart_id):
    url = ''.join([os.getenv("CMS_SCHEME"), '/api/cart-products'])
    headers = {'Authorization': access_token}
    data = {'data': {'quantity': quantity,
                     'populate': '*',
                     'product' : product_id,
                     'cart': cart_id
                     #[{ 'id': product_id}]
                     }}
    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()
    return response.ok
    
def get_cart_content(user_cart, access_token):
    cart_content = []
    cart_products = user_cart['attributes']['cart_products']['data']
    if cart_products:
        for cart_product in cart_products:
            cart_product_id = cart_product['id']
            cart_product_details = get_cart_product(access_token, cart_product_id)
            title = cart_product_details['title']
            price = cart_product_details['price']
            quantity = cart_product['attributes']['quantity']
            total_price = price*quantity
            cart_content.append({'title': title,
                                 'price': price,
                                 'quantity':quantity,
                                 'total_price': total_price})
    return cart_content



def add_item_to_cart(access_token, client_name, product_id, quantity):
    url = ''.join([os.getenv("CMS_SCHEME"), '/api/carts'])
    headers = {'Authorization': access_token}
    data = {
        'data': {
            'cart_product': product_id,
            'quantity': quantity,
            'tg-id': '507107638',
            'quantity': quantity
            }
        }
    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()
    return response.json()


def choose_cart_items_details(cart_items):
    return [
        {'name': cart_item['name'],
         'product_id':cart_item['product_id'],
         'quantity': cart_item['quantity'],
         'value_amount': cart_item['meta']['display_price'][
             'with_tax']['value']['formatted'],
         'value_currency': cart_item['value']['currency']
         } for cart_item in cart_items
        ]



def create_customer(access_token, name, email):
    url = 'https://api.moltin.com/v2/customers'
    headers = {'Authorization': access_token,
               'Content-Type': 'application/json'}
    json_data = {'data': {'type': 'customer',
                          'name': name,
                          'email': email,
                          'password': 'password'}}
    response = requests.post(url, headers=headers, json=json_data)
    response.raise_for_status()
    response.json()



def get_price(access_token, client_name):
    url = f'https://api.moltin.com/v2/carts/{client_name}'
    headers = {'Authorization': access_token}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()['data']['meta'][
        'display_price']['with_tax']['formatted']



def delete_from_cart(access_token, client_name, product_id):
    url = f'https://api.moltin.com/v2/carts/{client_name}/items/{product_id}'
    headers = {'Authorization': access_token}
    response = requests.delete(url, headers=headers)
    response.raise_for_status()


def validate_customer_data(access_token, client_name):
    url = 'https://api.moltin.com/v2/customers/'
    headers = {'Authorization': access_token}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    customers = response.json()['data']
    for customer in customers:
        if customer['name'] == client_name:
            msg = f'''Пользователь {customer['name']}
                    зарегистрирован.
                    Адрес электронной почты
                    для обратной связи {customer['email']}'''
            return msg

#create_cart(cms_token, 507107638)
#pprint(get_cart_content(cms_token, 507107638))


