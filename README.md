﻿# Teleshop

Эта программа представляет собой приложение интернет-магазина, созданного на платформе [elasticpath](https://euwest.cm.elasticpath.com/)

### Как установить

Python3 должен быть уже установлен. 
Затем используйте `pip` (или `pip3`, если есть конфликт с Python2) для установки зависимостей:
```
pip install -r requirements.txt
```
#### Настройки программы

Для того, чтобы программа корректно работала, в папке с программой создайте файл .env, содержащий следующие данные:

1) Токен, полученный при регистрации телеграмм-бота. Токен Вы получите при регистрации бота. Здесь написано [как зарегистрирвать телеграмм-бот](https://way23.ru/%D1%80%D0%B5%D0%B3%D0%B8%D1%81%D1%82%D1%80%D0%B0%D1%86%D0%B8%D1%8F-%D0%B1%D0%BE%D1%82%D0%B0-%D0%B2-telegram/).
Пропишите его следующим образом:
```
TG_TOKEN="Токен телеграмм-бота"
```
2) Идентификационный номер пользователя и пароль, полученные при регистрации магазина. Их следует прописать так:
```
CLIENT_ID="Идентификационный номер пользователя"
CLIENT_SECRET="Пароль пользователя"
```

3) Для работы понадобиться доступ к базе данных Redis. В настройках программы следует прописать адрес базы данных, его порт и пароль в следующем виде:

```
REDIS_ENDPOINT = "адрес базы данных (что-то вроде redis-.....cloud.redislabs.com)"
REDIS_PORT = "порт базы данных (пять цифр)"
REDIS_PASSWORD = "пароль к базе данных"
```


#### Как запустить

Бот запускается из командной строки. Для запуска программы с помощью команды cd сначала нужно перейти в папку с программой.
Предварительно следует обучить бот стандартным фразам. Для этого необходимо: 
Для запуска телеграмм-бота в командной строке пишем:
```
python tg_bot.py
```


Для запуска программы с сервера, необходимо сначала обзавестить сервером. Далее рассмотрен пример запуска на виртуальном сервере [Heroku](https://heroku.com).
Сначала следует зарегистироваться на сайте Heroku и создать приложение. Передать код можно с GitHub.После привязки аккаунта GitHub к Heroku следует найти репозиторий с кодом и подключить к Heroku. Переменные окружения следует прописать в разделе Config Vars во вкладке Settings. Нажать кнопку "Deploy Branch". 

### Цель проекта

Код написан в образовательных целях на онлайн-курсе для веб-разработчиков [dvmn.org](https://dvmn.org/).