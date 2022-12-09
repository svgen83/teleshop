import os
import requests


def add_to_cart(access_token, client_name, product_id, quantity):
    url = f'https://api.moltin.com/v2/carts/{client_name}/items'
    headers = {'Authorization': access_token,
               'Content-Type': 'application/json'
               }
    data = {
        'data': {
            'id': product_id,
            'type': 'cart_item',
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


def create_cart(access_token, client_name):
    response = requests.post(
        'https://api.moltin.com/v2/carts/',
        headers={
            'Authorization': access_token,
            'Content-Type': 'application/json'
            },
        json={
            'data': {'name': client_name}
            }
        )
    response.raise_for_status()
    return response.json()


def create_customer(access_token, name, email):
    url = 'https://api.moltin.com/v2/customers'
    headers = {'Authorization': access_token,
               'Content-Type': 'application/json'}
    json_data = {
        'data': {
            'type': 'customer',
            'name': name,
            'email': email,
            'password': 'password'
            }}
    response = requests.post(url, headers=headers, json=json_data)
    response.raise_for_status()
    response.json()


def get_access_token(redis_call):
    if redis_call.get('access_token'):
        access_token = redis_call.get('access_token').decode('utf-8')
    else:
        url = 'https://api.moltin.com/oauth/access_token'
        params = {'client_id': os.getenv('CLIENT_ID'),
                  'client_secret': os.getenv('CLIENT_SECRET'),
                  'grant_type': 'client_credentials'
                  }
        response = requests.post(url, data=params)
        response.raise_for_status()
        token_info = response.json()
        access_token = f'''Bearer {token_info['access_token']}'''
        expires = token_info['expires_in']
        redis_call.set('access_token',
                       access_token,
                       ex=expires)
    return access_token


def get_cart_items(access_token, client_name):
    url = f'https://api.moltin.com/v2/carts/{client_name}/items'
    headers = {'Authorization': access_token}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()['data']


def get_img_link(access_token, img_id):
    url = f'https://api.moltin.com/v2/files/{img_id}'
    headers = {'Authorization': access_token}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()['data']['link']['href']


def get_price(access_token, client_name):
    url = f'https://api.moltin.com/v2/carts/{client_name}'
    headers = {'Authorization': access_token}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()['data']['meta'][
        'display_price']['with_tax']['formatted']


def get_products(access_token):
    headers = {'Authorization': access_token}
    response = requests.get('https://api.moltin.com/v2/products',
                            headers=headers)
    response.raise_for_status()
    return response.json()['data']


def get_product_details(access_token, product_id):
    url = f'https://api.moltin.com/v2/products/{product_id}'
    headers = {'Authorization': access_token}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    all_product_details = response.json()['data']
    product_details = {
        'name': all_product_details['name'],
        'description': all_product_details['description'],
        'price': all_product_details['meta']['display_price'][
            'with_tax']['formatted'],
        'weight': all_product_details['weight']['kg'],
        'img_id': all_product_details['relationships'][
            'main_image']['data']['id']}
    return product_details


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
