from telegram.ext import (Updater, CommandHandler,ConversationHandler,
                          CallbackQueryHandler, MessageHandler, Filters)
import callbacks
import server_callbacks
from Authorizations import BOT_TOKEN, MY_BOT, MY_UPDATE
import time


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
                    1: [MessageHandler(Filters.text, callbacks.search_anime)],
                },
                fallbacks=[CommandHandler('cancel', callbacks.cancel)]
            ),

            CallbackQueryHandler(callbacks.callback_query_handler),

            CommandHandler('updateanime', callbacks.update_anime),
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
            ]


for handler in handlers:
    dispatcher.add_handler(handler)

dispatcher.add_error_handler(callbacks.error)

# Add automatic updating of users after every 3 hours
INTERVAL =  3 * 3600
job_queue = updater.job_queue
job_queue.run_repeating(callbacks.auto_update_user, interval=INTERVAL, first=0)

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
