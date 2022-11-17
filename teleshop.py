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


def get_customers(access_token):
    url = 'https://api.moltin.com/v2/customers/'
    headers = {'Authorization': access_token}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()['data']
  

def get_customer_token(access_token, _email, _password):
   headers = {'Authorization': access_token,
              'Content-Type': 'application/json'}
   json_data = {
       'data': {
           'type': 'token',
           'email': _email,
           'password': _password
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
    return response.json()


                                
def get_products(access_token):
    headers = {'Authorization': access_token}
    response = requests.get('https://api.moltin.com/v2/products', headers=headers)
    response.raise_for_status()
    return response.json()['data']
  
    
def update_inventory(access_token, product_id):
    url = f'https://api.moltin.com/v2/inventories/{product_id}/transactions'
    headers = {'Authorization': access_token,
               'Content-Type': 'application/json'}
    action = 'allocate'
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
    return response.json()
    
    
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
    return response.json()


def get_price(access_token, client_name):
    url = f'https://api.moltin.com/v2/carts/{client_name}'
    headers = {'Authorization': access_token}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()['data']['meta']['display_price']['with_tax']['formatted']
    

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
                  'value_amount': cart_item['meta']['display_price']['with_tax']['value']['formatted'],
                  'value_currency': cart_item['value']['currency']
        }
        details.append(detail)  
    return details
  

def delete_from_cart(access_token, client_name, product_id):
    url = f'https://api.moltin.com/v2/carts/{client_name}/items/{product_id}'
    headers = {'Authorization': access_token}
    response = requests.delete(url, headers=headers)
    response.raise_for_status()


def load_main_image(access_token, product_id, image_id):
  url = f'https://api.moltin.com/v2/products/{product_id}/relationships/main-image'
  headers = {
      'Authorization': access_token,
      'Content-Type': 'application/json'
          }
  json_data = {
    'data': {
        'type': 'main_image',
        'id': image_id
    }}
  response = requests.post(url, headers=headers, json=json_data)
  response.raise_for_status()


def load_image(access_token, file_name):
  files = {'file_location': (None,file_name)}
  url = 'https://api.moltin.com/v2/files'
  headers = {
      'Authorization': access_token
          }
  response = requests.post(url, headers=headers, files=files)
  response.raise_for_status()
  pprint(response.json())
