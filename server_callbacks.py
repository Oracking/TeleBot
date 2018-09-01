'''
    Special callbacks to perform server tasks
'''
import os
import time
import socket
import functools
from telegram import (ParseMode, InlineKeyboardButton,
                      InlineKeyboardMarkup)
from telegram.ext import ConversationHandler
import db_utils
from run_tests import run_my_unittests

RUNNING_MODE = os.environ.get('RUNNING_MODE')
if RUNNING_MODE == 'dev':
    from Authorizations.Test_Authorizations import Credentials
if RUNNING_MODE == 'prod':
    from Authorizations.Authorizations import Credentials


def private(original_function):

    @functools.wraps(original_function)
    def private_func(bot, update, *args, **kwargs):
        if str(update.message.chat_id) == Credentials.MY_CHAT_ID:
            output = original_function(bot, update, *args, **kwargs)
            return output
        update.message.reply_text("You are unauthorized to make this "
                                  "request")
        return ConversationHandler.END

    return private_func


def get_ip_address():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.connect(("8.8.8.8", 80))
    return sock.getsockname()[0]


# route: /hostip
# Conversational Handler Path: get_host_ip -> deliver_host_ip -> end
@private
def get_host_ip(bot, update):
    update.message.reply_text("That's a strong request. I am going to have "
                              "to ask you who you are")
    return 1


# Conversational Route
# Conversational Handler Path: get_host_ip -> deliver_host_ip -> end
@private
def deliver_host_ip(bot, update):
    if update.message.text == Credentials.ADMIN_PASSWORD:
        chat_id = update.message.chat_id
        ip = get_ip_address()
        bot_message = "The back-end of this bot is running on: {0}".format(ip)
        bot_message += Credentials.BOT_SIGNATURE
        bot.send_message(chat_id=chat_id, text=bot_message,
                         parse_mode=ParseMode.MARKDOWN)
    else:
        update.message.reply_text("Sorry, I cannot give you what you are "
                                  "asking for.")
    return ConversationHandler.END


# route: /shutdownserver
@private
def shutdown_declaration(bot, update):
    update.message.reply_text("That's a very strong request. Who are you?")
    return 1


# Conversational Route
# Conversational Handler Path: shutdown_declaration -> shutdown_server -> end
@private
def shutdown_server(bot, update):
    if update.message.text == Credentials.ADMIN_PASSWORD:
        chat_id = update.message.chat_id
        try:
            bot_message = "Server is shutting down :(\n Bye-bye"
            signature = "\n\n ~$ Microchip Out"
            bot_message += signature
            bot.send_message(chat_id=chat_id, text=bot_message,
                             parse_mode=ParseMode.MARKDOWN)
            os.system('init 0')
        except Exception as e:
            print("The following exception occured when shutdown command "
                  "was invoked")
            bot.send_message(chat_id=chat_id,
                             text="Something happened and server may not "
                                  "shutdown as expected")
            print(e)

    else:
        update.message.reply_text("Sorry, you are not permitted to perform "
                                  "this action")


# route: /rebootserver
@private
def reboot_declaration(bot, update):
    update.message.reply_text("That's a very strong request. Who are you?")
    return 1


# Conversational Route
# Conversational Handler Path: reboot_declaration -> reboot_server -> end
@private
def reboot_server(bot, update):
    if update.message.text == Credentials.ADMIN_PASSWORD:
        chat_id = update.message.chat_id
        try:
            bot_message = "Server is rebooting. Will be back in a bit :)"
            signature = "\n\n ~$ Microchip Out"
            bot_message += signature
            bot.send_message(chat_id=chat_id, text=bot_message,
                             parse_mode=ParseMode.MARKDOWN)
            os.system('reboot')
        except Exception as e:
            print("The following exception occured when reboot command was "
                  "invoked")
            bot.send_message(chat_id=chat_id,
                             text="Something happened and server may not "
                                  "reboot as expected")
            print(e)

    else:
        update.message.reply_text(
            "Sorry, you are not permitted to perform this action"
        )


# Has no route
def startup_ip_address(bot, update):
    chat_id = update.message.chat_id
    ip = get_ip_address()
    bot_message = "An instance of the back-end of this bot has been" \
                  " started on a device with IP: {0}".format(ip)
    bot_message += Credentials.BOT_SIGNATURE
    bot.send_message(chat_id=chat_id, text=bot_message,
                     parse_mode=ParseMode.MARKDOWN)


# Has no route
def startup_failed(bot, update):
    try:
        chat_id = update.message.chat_id
        ip = get_ip_address()
        bot_message = ("Attempted to start an instance of the back-end of this "
                       "bot on a device with IP: {0} but failed. Another "
                       "attempt will be made in the next 20 "
                       "seconds".format(ip))
        bot_message += Credentials.BOT_SIGNATURE
        bot.send_message(chat_id=chat_id, text=bot_message,
                         parse_mode=ParseMode.MARKDOWN)
    except:
        pass


def log_my_chatid(bot, update):
    print("\nLogging requested id: ", update.message.chat_id, "\n")
    update.message.reply_text(
        'Your chat id has been logged' + Credentials.BOT_SIGNATURE
    )


def auto_run_tests(bot, job):
    num_passed, num_failed, errors = run_my_unittests()
    if num_failed != 0:
        bot.send_message(chat_id=Credentials.MY_CHAT_ID,
                         text='Finished running scheduled tests\n\n'
                              'Encountered Failures:\n'
                              '{} passed and {} failed'.format(num_passed,
                                                               num_failed))
    elif errors:
        bot.send_message(chat_id=Credentials.MY_CHAT_ID,
                         text='Finished running scheduled tests\n\n'
                              'Encountered errors:\n[[{}]]'.format(errors))
    print("\n\nDone running tests\n\n")

@private
def sendnews_declaration(bot, update):
    update.message.reply_text("That is a strong request. Who are you?")
    return "get_message"

@private
def get_message(bot, update):
    if update.message.text == Credentials.ADMIN_PASSWORD:
        update.message.reply_text("Access Granted. What message would you "
                                  "like to send?")
        return "confirm_message"
    update.message.reply_text("Sorry, you are not authorized.")
    return ConversationHandler.END

@private
def confirm_message(bot, update):
    update.message.reply_text("Do you wish to send the following message "
                              "to all users:")
    buttons = [
        [InlineKeyboardButton(text="Yes", callback_data="Yes")],
        [InlineKeyboardButton(text="No", callback_data="No")]
    ]
    keyboard_markup = InlineKeyboardMarkup(buttons)
    bot.send_message(chat_id=update.message.chat_id,
                     text=update.message.text,
                     reply_markup=keyboard_markup)
    return "distribute_message"

# @private
# Private decorator is not dynamic enough to work on callback query handlers
def distribute_message(bot, update):
    mass_message = update.callback_query.message.text
    if update.callback_query.data == 'Yes':
        update.callback_query.message.reply_text("Alright. Distributing your "
                                                 "message")
        for user in db_utils.get_all_users():
            bot.send_message(chat_id=user.chat_id, text=mass_message)
            time.sleep(0.2) # To avoid telegram's 30 messages per second limit
    else:
        update.callback_query.message.reply_text("Your message has been "
                                                 "cancelled")
    return ConversationHandler.END


@private
def manually_run_tests_declaration(bot, update):
    update.message.reply_text("That is a strong request. Who are you?")
    return 1

@private
def manually_run_tests(bot, update):
    if update.message.text == Credentials.ADMIN_PASSWORD:
        bot.send_message(chat_id=update.message.chat_id,
                         text="Approved. Beginning to run tests")
        num_passed, num_failed, errors = run_my_unittests()
        if num_failed != 0:
            bot.send_message(chat_id=Credentials.MY_CHAT_ID,
                             text='Finished running tests\n\n'
                                  'Encountered Failures:\n'
                                  '{} passed and {} failed'.format(num_passed,
                                                                   num_failed))
        elif errors:
            bot.send_message(chat_id=Credentials.MY_CHAT_ID,
                             text='Finished running tests\n\n'
                                  'Encountered errors:\n[[{}]]'.format(errors))

        else:
            bot.send_message(chat_id=Credentials.MY_CHAT_ID,
                             text='Finished running tests\n\n'
                                  'Run with no failures:\n'
                                  '{} passed and {} failed'.format(num_passed,
                                                                   num_failed))

    else:
        update.message.reply_text("Sorry, you are not permitted to perform "
                                  "this action")
    return ConversationHandler.END
