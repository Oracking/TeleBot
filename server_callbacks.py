import socket
import os
from telegram import ParseMode
from telegram.ext import ConversationHandler
from Authorizations import BOT_SIGNATURE, AUTHORIZATION_TOKEN


def get_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    return s.getsockname()[0]


# route: /hostip
def get_host_ip(bot, update):
    chat_id = update.message.chat_id
    update.message.reply_text("That's a strong request. I am going to have to ask you who you are")
    return 1


# Conversational Route
# Conversational Handler Path: get_host_ip -> deliver_host_ip -> end
def deliver_host_ip(bot, update):
    if update.message.text == AUTHORIZATION_TOKEN:
        chat_id = update.message.chat_id
        ip = get_ip_address()
        bot_message = "The back-end of this bot is running on: {0}".format(ip)
        bot_message += BOT_SIGNATURE
        bot.send_message(chat_id=chat_id, text=bot_message, parse_mode=ParseMode.MARKDOWN)
    else:
        update.message.reply_text("Sorry, I cannot give you what you are asking for.")
    return ConversationHandler.END


def shutdown_declaration(bot, update):
    update.message.reply_text("That's a very strong request. Who are you?")
    return 1


#route: /shutdownserver
def shutdown_server(bot, update):
    if update.message.text == AUTHORIZATION_TOKEN:
        chat_id = update.message.chat_id
        try:
            bot_message = "Server is shutting down :(\n Bye-bye"
            signature = "\n\n ~$ Microchip Out"
            bot_message += signature
            bot.send_message(chat_id=chat_id, text=bot_message,
                             parse_mode=ParseMode.MARKDOWN)
            os.system('init 0')
        except Exception as e:
            print("The following exception occured when shutdown command was invoked")
            bot.send_message(chat_id=chat_id, text='Something happened and server may not shutdown as expected')
            print(e)

    else:
        update.message.reply_text("Sorry, you are not permitted to perform this action")


# Has no route
def startup_ip_address(bot, update):
    chat_id = update.message.chat_id
    ip = get_ip_address()
    bot_message = "An instance of the back-end of this bot has been" \
                  " started on a device with IP: {0}".format(ip)
    bot_message += BOT_SIGNATURE
    bot.send_message(chat_id=chat_id, text=bot_message,
                     parse_mode = ParseMode.MARKDOWN)


# Has no route
def startup_failed(bot, update):
    try:
        chat_id = update.message.chat_id
        ip = get_ip_address()
        bot_message = "Attempted to start an instance of the back-end of this" \
                      " bot on a device with IP: {0} but failed. Another" \
                      " attempt will be made in the next 20 seconds".format(ip)
        bot_message += BOT_SIGNATURE
        bot.send_message(chat_id=chat_id, text=bot_message,
                         parse_mode = ParseMode.MARKDOWN)
    except:
        pass