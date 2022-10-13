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

def get_customer_token(access_token, email, password):
   headers = {'Authorization': access_token,
              'Content-Type': 'application/json'}
   json_data = {
       'data': {
           'type': 'token',
           'email': email,
           'password': password,
           'authentication_mechanism': 'password'
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
    #name, price, description, weight, 
    
    
def get_img_link(access_token, img_id):
    url = f'https://api.moltin.com/v2/files/{img_id}'
    headers = {'Authorization': access_token}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()['data']['link']['href']
    
    
def add_to_cart(access_token,customer_token, client_name, products, quantity):
    headers = {'Authorization': access_token,
               'Content-Type': 'application/json',
               'X-Moltin-Customer-Token': customer_token,
               'EP-Channel': '',
               'EP-Context-Tag': ''
               }
    
    data = {
        "data": {
          "id": products["data"][0]["id"],
          "type": "cart_item",
          "quantity": quantity
          }
        }
##    print(products["data"][0]["id"])
    response = requests.post(f'https://api.moltin.com/v2/carts/{client_name}/items',
                             headers=headers, json=data)
    response.raise_for_status()     
    return response.json()

    

if __name__ == "__main__":
    load_dotenv()

    access_token = get_access_token()
    #create_product(access_token)

####    pprint(create_customer(access_token, "svg_2", "s@g.ru", "1111"))
    goods = get_product_details(access_token, "47eb211d-89f2-4217-80d1-f66bf9314b56")
    pprint(goods)
    img_link = get_img_link(access_token, goods['img_id'])
    print(img_link)
    #customer_token = get_customer_token(access_token, "s@g.ru", "1111")
##    pprint(create_cart(access_token, "svg_2"))
##    print(customer_token)
    #pprint(add_to_cart(access_token,customer_token, "svg_2", products, 2))
       
