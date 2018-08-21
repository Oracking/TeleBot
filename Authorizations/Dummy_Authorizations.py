'''
    Module containing sensitive data for accessing bot.
    This module should not be commited to the git repository or displayed
    on any public platform.
'''
from telegram import Bot

class Credentials:
    '''
        Data class to hold sensitive bot information
    '''
    BOT_SIGNATURE = 'bot_signature' # Can be any string that appears at the end of messages sent to admin
    BOT_TOKEN = 'bot_token' # Token for accessing bot, which can be obtained from BotFather
    MY_CHAT_ID = 'chat_id' # The chat id of the bot's conversation with admin
    ADMIN_PASSWORD = 'admin_password'

class Message:
    '''
        Dummy Message class to mimic python-telegram-bot Message class
    '''
    def __init__(self, chat_id):
        self.chat_id = chat_id

class Update:
    '''
        Dummy Update class to mimic python-telegram-bot Update class
    '''
    def __init__(self, chat_id):
        self.message = Message(chat_id)

MY_BOT = Bot(token=Credentials.BOT_TOKEN)
MY_UPDATE = Update(Credentials.MY_CHAT_ID)