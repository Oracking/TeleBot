from telegram.ext import Updater, CommandHandler
import callbacks

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


if __name__ == '__main__':
    updater.start_polling()
