import os
import requests
from pprint import pprint


from dotenv import load_dotenv

def get_resp():
    url = "https://api.moltin.com/v2/products"
    client_id = os.getenv("CLIENT_ID")
    client_secret = os.getenv("CLIENT_SECRET")
    store_id = os.getenv("STORE_ID")
    
    headers = {"Authorization": token}
    params = {"client_id": "client_id", "client_secret": client_secret,
              "store_id": store_id}
    response = requests.get(clicks_endpoint, params=params)
    response.raise_for_status()
    r = response.json()
    print(response)

if __name__ == "__main__":
    load_dotenv()
    url = "https://api.moltin.com/pcm/products"
    client_id = os.getenv("CLIENT_ID")
    client_secret = os.getenv("CLIENT_SECRET")
    
    params = {"client_id": client_id,
              "client_secret": client_secret,
              "grant_type": "client_credentials"}
    params2 = {"client_id": client_id,
              "grant_type": "implicit"}
    

    client_credentials_response = requests.post('https://api.moltin.com/oauth/access_token',data=params)
    client_credentials_response.raise_for_status()
    client_credentials_token = f'Bearer {client_credentials_response.json()["access_token"]}'
    print(client_credentials_token)

##    implicit_response = requests.post('https://api.moltin.com/oauth/access_token',data=params2)
##    implicit_response.raise_for_status()
##    implicit_token = f'Bearer {implicit_response.json()["access_token"]}'
##    print(implicit_token)
    
    products_response = requests.get(url,headers={'Authorization': client_credentials_token})
    products_response.raise_for_status()
    products = products_response.json()



    catalog_rule_response = requests.post('https://api.moltin.com/pcm/catalogs/rules',
                             headers={'Authorization': client_credentials_token,
                                      "Content-Type": "application/json"},
                             json={'data': {
                                 'type': 'catalog_rule',
                                 'attributes': {
                                     'name': 'Preferred customers',
                                     'catalog_id': 'legacy'},
                                 }})
    catalog_rule_response.raise_for_status()
    catalog_rule = catalog_rule_response.json()
    pprint(catalog_rule)
    

##    catalog_rule_response = requests.get("https://api.moltin.com/pcm/catalogs/rules",headers={'Authorization': client_credentials_token})
##    catalog_rule_response.raise_for_status()
##    catalog_rule = catalog_rule_response.json()
##    pprint(catalog_rule)
        
    products_for_sale = {
        "data": {
          "id": products["data"][0]["id"],
          "type": "cart_item",
          "quantity": 1
          }
        }
##    pprint(products_for_sale)

    
    into_cart_response = requests.post('https://api.moltin.com/v2/carts/abc/items',
                         headers={'Authorization': client_credentials_token,
                                  'Content-Type': 'application/json',
                                  "X-Moltin-Customer-Token":"5000000",
                                  "EP-Channel":"555555",
                                  "EP-Context-Tag":"11111111"
                                  },
                         json={"data": products_for_sale} )
    into_cart_response.raise_for_status()
    print(into_response.json())

    
    carts_response = requests.get("https://api.moltin.com/v2/carts/abc",headers={'Authorization': client_credentials_token})
    carts_response.raise_for_status()
    pprint(carts_response.json())


##
##    items_response = requests.get('https://api.moltin.com/v2/carts/abc/items', headers={'Authorization': client_credentials_token})
##    items_response.raise_for_status()
##    pprint(items_response.json())     
