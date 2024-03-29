﻿# Teleshop

Эта программа представляет собой приложение интернет-магазина, созданного на платформе [Strapi](https://docs.strapi.io/)

### Как установить

Python3 должен быть уже установлен. Затеме необходимо создать виртуальную среду и установить зависимости после её запуска: 
```
pip install -r requirements.txt
```

### Установка и настройка Strapi
С помощью [инструкции](https://docs.strapi.io/user-docs/content-type-builder) создайте модель товара Product, модель корзины Cart, вспомогательную модель Cart_product. 
В модели Product будут поля:
* `titlе` - название товара,
* `description` - описание товара,
* `picture` - изображение товара,
* `price` -цена товара
  
В модели `Cart` создайте поле `tg_id` для идентификации пользователя в телеграмм-чате.
В модели `Cart_product` создайте поле `quantity` для хранения данных о количестве товаров.
Далее [установите связи моделей](https://docs.strapi.io/user-docs/content-type-builder/configuring-fields-content-type#-relation):
* `Cart_product` и `Product`: один к одному;
* `Cart` и `Cart_product`: один ко многим;
* `Cart` и `User`: многие ко многим.


#### Настройки программы

Для того, чтобы программа корректно работала, в папке с программой создайте файл .env, содержащий следующие данные:

*  Токен, полученный при регистрации телеграмм-бота. Токен Вы получите при регистрации бота. Здесь написано [как зарегистрирвать телеграмм-бот](https://way23.ru/%D1%80%D0%B5%D0%B3%D0%B8%D1%81%D1%82%D1%80%D0%B0%D1%86%D0%B8%D1%8F-%D0%B1%D0%BE%D1%82%D0%B0-%D0%B2-telegram/).
Пропишите его следующим образом:
```
TG_TOKEN="Токен телеграмм-бота"
```
*  Токен администратора Strapi, полученный в настройках созданного приложения:
```
CMS_TOKEN="bearer Токен администратора Strapi"
```
*  Схема адреса Strapi:
```
CMS_SCHEME = "http://localhost:1337/"
``` 
Если вы запускаете бот с удаленного сервера, то следует вместо `localhost` прописать его IP адрес.

* Для работы понадобиться доступ к базе данных Redis или её аналогу. Здесь использован [Upstash Redis](https://upstash.com/docs/redis/overall/getstarted)В настройках программы следует прописать адрес базы данных и его токен в следующем виде:

```
UPSTASH_REDIS_REST_URL = "адрес базы данных (что-то вроде ......upstash.io)"
UPSTASH_REDIS_REST_TOKEN = "токен к базе данных"
```

#### Как запустить
Предварительно следует запустить Strapi. Для этого необходимо перейти в каталог с установленной cms и запустить команду:
```
npm run develop
```

Бот запускается из командной строки. Для запуска программы с помощью команды cd сначала нужно перейти в папку с программой.
Для запуска телеграмм-бота в командной строке пишем:
```
python tg_bot.py
```

Для запуска программы с сервера, необходимо сначала обзавестить сервером. Далее рассмотрен пример запуска на виртуальном сервере.
О том, как это сделать, подробно описано [в этой инструкции](https://ramziv.com/article/38). 

### Цель проекта

Код написан в образовательных целях на онлайн-курсе для веб-разработчиков [dvmn.org](https://dvmn.org/).
