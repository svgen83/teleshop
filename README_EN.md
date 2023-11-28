# Teleshop

This program is an online store application created on the [Strapi](https://docs.strapi.io/) platform

### How to install

Python3 should already be installed. Then you need to create a virtual environment and install dependencies after it starts:
```
pip install -r requirements.txt
```

### Installing and configuring Strapi
Using [instructions](https://docs.strapi.io/user-docs/content-type-builder) create a product model Product, cart model Cart, auxiliary model Cart_product.
The Product model will have fields:
* `title` - product name,
* `description` - description of the product,
* `picture` - product image,
* `price` - product price
In the `Cart` model, create a `tg_id` field to identify the user in the telegram chat.
In the `Cart_product` model, create a `quantity` field to store data about the quantity of products.
Next [establish model relationships](https://docs.strapi.io/user-docs/content-type-builder/configuring-fields-content-type#-relation):
* `Cart_product` and `Product`: one to one;
* `Cart` and `Cart_product`: one to many;
* `Cart` and `User`: many to many.


#### Program settings

In order for the program to work correctly, create a .env file in the program folder containing the following data:

* Token received when registering a telegram bot. You will receive a token when registering a bot. Here it is written [how to register a telegram bot](https://way23.ru/%D1%80%D0%B5%D0%B3%D0%B8%D1%81%D1%82%D1%80%D0%B0 %D1%86%D0%B8%D1%8F-%D0%B1%D0%BE%D1%82%D0%B0-%D0%B2-telegram/).
Write it like this:
```
TG_TOKEN="Telegram bot token"
```
* Strapi administrator token obtained in the settings of the created application:
```
CMS_TOKEN="bearer Strapi admin token"
```
* Strapi address scheme:
```
CMS_SCHEME = "http://localhost:1337"
```
If you are launching a bot from a remote server, you should enter its IP address instead of `localhost`.

* To work, you will need access to a Redis database or its equivalent. Here we used [Upstash Redis](https://upstash.com/docs/redis/overall/getstarted) In the program settings, you should specify the database address and its token in the following form:

```
UPSTASH_REDIS_REST_URL = "database address (something like ......upstash.io)"
UPSTASH_REDIS_REST_TOKEN = "database token"
```

#### How to start
You must first launch Strapi. To do this, you need to go to the directory with installed cms and run the command:
```
npm run develop
```

The bot is launched from the command line. To run a program using the cd command, you first need to navigate to the folder with the program.
To launch the telegram bot on the command line we write:
```
python tg_bot.py
```

To run a program from a server, you must first acquire a server. The following is an example of launching on a virtual server.
How to do this is described in detail [in this manual](https://ramziv.com/article/38).

### Objective of the project

The code was written for educational purposes in an online course for web developers [dvmn.org](https://dvmn.org/).
