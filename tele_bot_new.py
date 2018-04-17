from telegram.ext import Updater, CommandHandler

BOT_TOKEN = "585202235:AAExMUAhLZllUHiIAqke8e71Bxr-pzEY5Kg"

updater = Updater(token=BOT_TOKEN)
dispatcher = updater.dispatcher


def start(bot, update):
    bot.send_message(chat_id=update.message.chat_id,
                     text='Hello, Microchip can now talk!')

def anime_list(bot, update):
    bot.send_message(chat_id=update.message.chat_id,
                     text='Getting your anime list')


start_handler = CommandHandler('start', start)
anime_list_handler = CommandHandler('animelist', anime_list)

dispatcher.add_handler(start_handler)
dispatcher.add_handler(anime_list_handler)


if __name__ == '__main__':
    updater.start_polling()
