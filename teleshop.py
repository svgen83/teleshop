import json
import os
import requests
from pprint import pprint
from dotenv import load_dotenv


def get_access_token():
    url = "https://api.moltin.com/oauth/access_token"
    params = {"client_id": os.getenv("CLIENT_ID"),
              "client_secret": os.getenv("CLIENT_SECRET"),
              "grant_type": "client_credentials"
              }
    response = requests.post(url,data=params)
    response.raise_for_status()
    return f'Bearer {response.json()["access_token"]}'
    

def create_customer(access_token, name, email, password):
    headers = {'Authorization': access_token,
               'Content-Type': 'application/json'}
    json_data = {
        'data': {
            'type': 'customer',
            'name': name,
            'email': email,
            'password': password}}
    response = requests.post('https://api.moltin.com/v2/customers', headers=headers, json=json_data)
    response.raise_for_status()
    return response.json()

def get_customer_token(access_token, _email, _password):
   headers = {'Authorization': access_token,
              'Content-Type': 'application/json'}
   json_data = {
       'data': {
           'type': 'token',
           'email': _email,
           'password': _password
           #'authentication_mechanism': 'password'
           }
       }
   response = requests.post('https://api.moltin.com/v2/customers/tokens',
                            headers=headers, json=json_data)
   response.raise_for_status()
   return response.json()["data"]["token"]


def create_cart(access_token, client_name):
    response = requests.post('https://api.moltin.com/v2/carts/',
                            headers={'Authorization': access_token,
                            "Content-Type": 'application/json'},
                            json = {"data":{"name":client_name}})
                                          
    response.raise_for_status()
    return response.json()


def create_product(access_token):
    headers = {'Authorization': access_token,
               'Content-Type': 'application/json'
               }
    params = {'data': {
        'type': 'product',
        'name': 'blue_fish',
        'slug': 'blue_fish',
        'sku': '3',
        'manage_stock': True,
        'description': 'no description',
        'price': [{'amount': 1000,
                   'currency': 'USD',
                   "includes_tax": True}],
        "status": 'live',
        'commodity_type': 'physical'
    }}
    response = requests.post('https://api.moltin.com/v2/products',
                             headers=headers,
                             json=params)
    response.raise_for_status()
    print(response.json())


                                
def get_products(access_token):
    headers = {'Authorization': access_token}
    response = requests.get('https://api.moltin.com/v2/products', headers=headers)
    response.raise_for_status()
    return response.json()['data']
  
    
def update_inventory(access_token, product_id):
    url = f'https://api.moltin.com/v2/inventories/{product_id}/transactions'
    headers = {'Authorization': access_token,
               'Content-Type': 'application/json'}
    action = 'allocate' #'increment'
    #action = 'increment'
    json_data = {
    'data': {
        'type': 'stock-transaction',
        'action': action,
        'quantity': 20000}}
    
    response = requests.post(url, headers=headers, json=json_data)
    response.raise_for_status()
    return response.json()

   
def get_inventory(access_token):
    url = 'https://api.moltin.com/v2/inventories'
    headers = {'Authorization': access_token}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    pprint(response.json())
    
    
def get_product_details(access_token, product_id):
    url = f'https://api.moltin.com/v2/products/{product_id}'
    headers = {'Authorization': access_token}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    all_product_details = response.json()['data']
    product_details = {
                              'name': all_product_details['name'],
                              'description': all_product_details['description'],
    'price': all_product_details['meta']['display_price']['with_tax']['formatted'],
    'weight': all_product_details['weight']['kg'],
    'img_id': all_product_details['relationships']['main_image']['data']['id']}
    return product_details
    
    
def get_img_link(access_token, img_id):
    url = f'https://api.moltin.com/v2/files/{img_id}'
    headers = {'Authorization': access_token}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()['data']['link']['href']
    
    
def add_to_cart(access_token, client_name, product_id, quantity):
    url = f'https://api.moltin.com/v2/carts/{client_name}/items'
    headers = {'Authorization': access_token,
               'Content-Type': 'application/json'
               #'X-Moltin-Customer-Token': customer_token,
               #'EP-Channel': '',
               #'EP-Context-Tag': ''
               }
    
    data = {
        "data": {
          "id": product_id,
          "type": "cart_item",
          "quantity": quantity
          }
        }
    response = requests.post(url,headers=headers, json=data)
    response.raise_for_status()
    pprint(response.json())     
    return response.json()


def get_cart(access_token, client_name):
    url = f'https://api.moltin.com/v2/carts/{client_name}'
    headers = {'Authorization': access_token}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()
    

def get_cart_items(access_token, client_name):
    url = f'https://api.moltin.com/v2/carts/{client_name}/items'
    headers = {'Authorization': access_token}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()['data']  


def choose_cart_items_details(cart_items):
    details = []
    for cart_item in cart_items:
        detail = {'name': cart_item['name'],
                  'product_id':cart_item['product_id'],
                  'quantity': cart_item['quantity'],
                  'value_amount': cart_item['value']['amount'],
                  'value_currency': cart_item['value']['currency']
        }
        details.append(detail)  
    return details


def create_msgs_for_cart(cart_items):
    msgs = []
    for cart_item in cart_items:
        name = cart_item['name']
        quantity = cart_item['quantity']
        value_amount = cart_item['value']['amount']
        value_currency = cart_item['value']['currency']
        msg = f"""
              {name}
              {quantity}
              {value_amount} {value_currency}
              """
        msgs.append(msg)
    pprint(msgs)
    return msgs
    

def delete_from_cart(access_token, client_name, product_id):
    url = f'https://api.moltin.com/v2/carts/{client_name}/items/{product_id}'
    headers = {'Authorization': access_token}
    response = requests.delete(url, headers=headers)
    response.raise_for_status()
    return response.json()
    
    

if __name__ == "__main__":
    load_dotenv()

    access_token = get_access_token()
    
    #p_id = "47eb211d-89f2-4217-80d1-f66bf9314b56"
    p_id = '2d783b46-a428-4fdd-ab30-88b5c415d847'
    #p_id = "52c56b6e-243a-47a7-ae47-ee652791953e"
####    pprint(create_customer(access_token, "svg_2", "s@g.ru", "1111"))
  #  goods = get_product_details(access_token, p_id)
    #pprint(goods)
    pprint(get_products(access_token))
    #customer_token = get_customer_token(access_token, "s@g.ru", "1111")
    #print(customer_token)
    #pprint(create_cart(access_token, "svg_2"))
    #pprint(get_cart(access_token, "svg_2"))
    add_to_cart(access_token, "svg_2", p_id, 2)
    cart_items=get_cart_items(access_token, "svg_2")
    cart_items_details = get_cart_items_details(cart_items)
    pprint(cart_items_details)
    #delete_from_cart(access_token, "svg_2", p_id)
    
    
    
    
    
    
       
