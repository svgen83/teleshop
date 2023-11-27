import os
import requests


def get_products(access_token):
    url = ''.join([os.getenv("CMS_SCHEME"), '/api/products'])
    headers = {'Authorization': access_token}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()['data']


def get_product(access_token, product_id):
    url = ''.join([os.getenv("CMS_SCHEME"), '/api/products', f'/{product_id}'])
    headers = {'Authorization': access_token}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()['data']


def get_image_url(access_token, product_id):
    url = ''.join([os.getenv("CMS_SCHEME"),
                   '/api/products', f'/{product_id}'])
    headers = {'Authorization': access_token}
    data = {'populate': 'picture'}
    response = requests.get(url, headers=headers, params=data)
    response.raise_for_status()
    img_url = response.json()[
        'data']['attributes']['picture'][
            'data'][0]['attributes']['url']
    return ''.join([os.getenv("CMS_SCHEME"), img_url])


def load_image(image_url, access_token, product_id):
    response = requests.get(image_url,
                            headers={'Authorization': access_token})
    response.raise_for_status()
    image_path = f'{product_id}.jpg'
    with open(image_path, 'wb') as file:
        file.write(response.content)
    return image_path


def get_carts(access_token):
    url = ''.join([os.getenv("CMS_SCHEME"), '/api/carts'])
    headers = {'Authorization': access_token}
    data = {'populate': '*'}
    response = requests.get(url, headers=headers, params=data)
    response.raise_for_status()
    return response.json()['data']


def create_cart(access_token, chat_id):
    url = ''.join([os.getenv("CMS_SCHEME"), '/api/carts'])
    headers = {'Authorization': access_token}
    data = {'data': {'tg_id': chat_id}}
    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()
    return response.json()['data']


def get_cart_product_details(access_token, cart_product_id):
    url = ''.join([os.getenv("CMS_SCHEME"),
                   f'/api/cart-products/{cart_product_id}'])
    headers = {'Authorization': access_token}
    data = {'populate': '*'}
    response = requests.get(url, headers=headers, params=data)
    response.raise_for_status()
    return response.json()['data']['attributes']['product'][
        'data']['attributes']


def get_cart_details(user_cart, access_token):
    cart_details = []
    cart_products = user_cart['attributes']['cart_products']['data']
    if cart_products:
        for cart_product in cart_products:
            cart_product_id = cart_product['id']
            cart_product_details = get_cart_product_details(
                access_token, cart_product_id)
            title = cart_product_details['title']
            price = cart_product_details['price']
            quantity = cart_product['attributes']['quantity']
            total_price = price*quantity
            cart_details.append({'product_id': cart_product['id'],
                                 'title': title,
                                 'price': price,
                                 'quantity': quantity,
                                 'total_price': total_price})
    return cart_details


def get_or_create_user_cart(access_token, chat_id):
    carts = get_carts(access_token)
    for cart in carts:
        if cart['attributes']['tg_id'] == chat_id:
            user_cart = cart
    if not user_cart:
        user_cart = create_cart(access_token, chat_id)
    return user_cart


def add_to_cart(access_token, cart_id, product_id, quantity):
    url = ''.join([os.getenv("CMS_SCHEME"), '/api/cart-products'])
    headers = {'Authorization': access_token}
    data = {'data': {'quantity': quantity,
                     'populate': '*',
                     'product': product_id,
                     'cart': cart_id
                     }}
    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()
    print(response.json())
    return response.ok


def delete_from_cart(access_token, cart_product_id):
    url = ''.join([os.getenv("CMS_SCHEME"),
                   f'/api/cart-products/{cart_product_id}'])
    headers = {'Authorization': access_token}
    response = requests.delete(url, headers=headers)
    response.raise_for_status()
    return response.ok


def get_or_create_customer(access_token, client_name, email):
    url = ''.join([os.getenv("CMS_SCHEME"), '/api/users'])
    headers = {'Authorization': access_token}
    data = {'username': client_name,
            'password': 'password',
            'email': email}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    users = response.json()
    customer = [
        user for user in users if user['username'] == client_name]
    if customer:
        return '''Пользователь таким именем уже зарегистирован'''
    else:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        return f'''Пользователь {client_name} зарегистрирован.
        Адрес электронной почты для обратной связи {email}'''
