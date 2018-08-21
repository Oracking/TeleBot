import os
import time
import argparse
import logging
from telegram.ext import (Updater, CommandHandler,ConversationHandler,
                          CallbackQueryHandler, MessageHandler, Filters)


parser = argparse.ArgumentParser(description='Simple cli app to run the bot')
parser.add_argument('mode', type=str, 
                    help='Mode to run bot in. Options are "dev" for development mode and ' 
                         '"prod" for production. The difference is in the bot that is ' 
                         'used.', 
                    choices=['prod', 'dev'])
parser.add_argument('method', type=str, 
                    help='Method to use to run bot. Options are "poll" and "hook", which '
                         'use polling and a webhook, respectively.', 
                    choices=['poll', 'hook'])
args = parser.parse_args()

if args.mode == 'dev':
    from Authorizations.Test_Authorizations import Credentials, MY_BOT, MY_UPDATE
elif args.mode == 'prod':
    from Authorizations.Authorizations import Credentials, MY_BOT, MY_UPDATE

os.environ.setdefault('RUNNING_MODE', args.mode)

import callbacks
import server_callbacks


# To allow logging of errors
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

updater = Updater(token=Credentials.BOT_TOKEN)
dispatcher = updater.dispatcher


# Application Handlers
handlers = [
            ConversationHandler(
                entry_points=[CommandHandler('start', callbacks.start)],
                states={
                    1: [MessageHandler(Filters.text, callbacks.nickname_user)]
                },
                fallbacks=[CommandHandler('cancel', callbacks.cancel)]
            ),

            ConversationHandler(
                entry_points=[CommandHandler('addanime', callbacks.add_anime),
                              CommandHandler('research', callbacks.research)],
                states={
                    1: [MessageHandler(Filters.text, callbacks.search_anime),
                        CommandHandler('research', callbacks.research)],
                    2: [CallbackQueryHandler(callbacks.add_anime_callback)]
                },
                fallbacks=[CommandHandler('cancel', callbacks.cancel)],
                allow_reentry = True,
            ),

            ConversationHandler(
                entry_points=[CommandHandler('updateanime', callbacks.update_anime)],
                states={
                    1: [CallbackQueryHandler(callbacks.update_anime_callback)]
                },
                fallbacks=[CommandHandler('cancel', callbacks.cancel)]
            ),

            ConversationHandler(
                entry_points=[CommandHandler('removeanime', callbacks.remove_anime)],
                states={
                    1: [CallbackQueryHandler(callbacks.confirm_removal_callback)],
                    2: [CallbackQueryHandler(callbacks.finally_remove_anime_callback)]
                },
                fallbacks=[CommandHandler('cancel', callbacks.cancel)],
            ),
            CommandHandler('myanime', callbacks.get_anime_list),
            CommandHandler('updateallanime', callbacks.update_all_anime),
            CommandHandler('cancel', callbacks.cancel),
            ]


# Special server callback handlers
handlers += [
            ConversationHandler(
                entry_points=[CommandHandler('hostip', server_callbacks.get_host_ip)],
                states={
                    1: [MessageHandler(Filters.text, server_callbacks.deliver_host_ip)]
                },
                fallbacks=[CommandHandler('cancel', callbacks.cancel)]
            ),

            ConversationHandler(
                entry_points=[CommandHandler('shutdownserver', server_callbacks.shutdown_declaration)],
                states = {
                    1: [MessageHandler(Filters.text, server_callbacks.shutdown_server)]
                },
                fallbacks = [CommandHandler('cancel', callbacks.cancel)]
            ),

            ConversationHandler(
                entry_points=[CommandHandler('rebootserver', server_callbacks.reboot_declaration)],
                states = {
                    1: [MessageHandler(Filters.text, server_callbacks.reboot_server)]
                },
                fallbacks = [CommandHandler('cancel', callbacks.cancel)]
            ),
            CommandHandler('logmyid', server_callbacks.log_my_chatid)
            ]


for handler in handlers:
    dispatcher.add_handler(handler)

dispatcher.add_error_handler(callbacks.error)

# Add automatic updating of users after every 1 hour
INTERVAL =  3600
job_queue = updater.job_queue
job_queue.run_repeating(callbacks.auto_update_users, interval=INTERVAL, first=0)

if __name__ == '__main__':
    initiated = False
    if args.method == 'poll':
        while not initiated:
            try:
                updater.start_polling()
                server_callbacks.startup_ip_address(MY_BOT, MY_UPDATE)
                initiated = True
            except:
                initiated = False
                server_callbacks.startup_failed(MY_BOT, MY_UPDATE)
                time.sleep(20)

    elif args.method == 'hook':
        print("Webhook not developed yet")
