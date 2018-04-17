from telegram.ext import Updater, CommandHandler
import callbacks
import time

BOT_TOKEN = "585202235:AAExMUAhLZllUHiIAqke8e71Bxr-pzEY5Kg"

updater = Updater(token=BOT_TOKEN)
dispatcher = updater.dispatcher


handlers = [
            CommandHandler('start',callbacks.start),
            CommandHandler('myanimelist', callbacks.get_anime_list),
            CommandHandler('updateallanime', callbacks.update_all_anime),
            CommandHandler('hostip', callbacks.get_host_ip),
            CommandHandler('updateanime', callbacks.update_anime, pass_args=True),
            CommandHandler('commands', callbacks.list_commands),
            CommandHandler('shutdownserver', callbacks.shutdown_server),
           ]

for handler in handlers:
    dispatcher.add_handler(handler)


def begin_polling(updater):
    try:
        updater.start_polling()
        callbacks.startup_ip_address(callbacks.MY_BOT, callbacks.MY_UPDATE)
    except:
        callbacks.startup_failed(callbacks.MY_BOT, callbacks.MY_UPDATE)
        time.sleep(20)
        begin_polling(updater)

if __name__ == '__main__':
    begin_polling(updater)
