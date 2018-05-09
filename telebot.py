from telegram.ext import (Updater, CommandHandler,ConversationHandler,
                          CallbackQueryHandler, MessageHandler, Filters)
import callbacks
import server_callbacks
from Authorizations import BOT_TOKEN, MY_BOT, MY_UPDATE
import time
import logging

# To allow logging of errors
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

updater = Updater(token=BOT_TOKEN)
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
            )

             ConversationHandler(
                entry_points=[CommandHandler('rebootserver', server_callbacks.reboot_declaration)],
                states = {
                    1: [MessageHandler(Filters.text, server_callbacks.reboot_server)]
                },
                fallbacks = [CommandHandler('cancel', callbacks.cancel)]
            )
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
    while not initiated:
        try:
            updater.start_polling()
            server_callbacks.startup_ip_address(MY_BOT, MY_UPDATE)
            initiated = True
        except:
            initiated = False
            server_callbacks.startup_failed(MY_BOT, MY_UPDATE)
            time.sleep(20)
