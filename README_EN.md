# teleshop

This program is an application of an online store built on the platform [elasticpath](https://euwest.cm.elasticpath.com/)

### How to install

Python3 should already be installed.
Then use `pip` (or `pip3` if there is a conflict with Python2) to install the dependencies:
```
pip install -r requirements.txt
```
#### Program settings

In order for the program to work correctly, create an .env file in the program folder containing the following data:

1) Token received upon registration of the telegram bot. You will receive a token upon registration of the bot. It says here [how to register a telegram bot] %D1%86%D0%B8%D1%8F-%D0%B1%D0%BE%D1%82%D0%B0-%D0%B2-telegram/).
Write it like this:
```
TG_TOKEN="Telegram bot token"
```
2) User identification number and password obtained during store registration. They should be written like this:
```
CLIENT_ID="User ID"
CLIENT_SECRET="User password"
```

3) To work, you need access to the Redis database. In the program settings, you should specify the database address, its port and password in the following form:

```
REDIS_ENDPOINT = "database address (something like redis-.....cloud.redislabs.com)"
REDIS_PORT = "database port (five digits)"
REDIS_PASSWORD = "database password"
```


#### How to start

The bot is launched from the command line. To run the program using the cd command, you first need to go to the folder with the program.
You should first teach the bot standard phrases. For this you need:
To start the telegram bot on the command line, write:
```
python tg_bot.py
```


To run the program from the server, you must first acquire a server. The following is an example of running on a virtual server [Heroku](https://heroku.com).
The first step is to register on the Heroku website and create an app. You can submit the code from GitHub. After linking your GitHub account to Heroku, you should find the repository with the code and connect it to Heroku. Environment variables should be registered in the Config Vars section in the Settings tab. Click the "Deploy Branch" button.

### Objective of the project

The code was written for educational purposes in an online course for web developers [dvmn.org](https://dvmn.org/).