import telegram
import anime_scraper as scraper
from utils import fetch_anime_db, update_anime_db

# Imports for getting device IP address
import socket


# You can use bot.get_me() to verify bot.
# To get the chat_id send a message to your bot and use the code below:
# chat_id = bot.get_updates()[-1].message.chat_id

BOT_SIGNATURE = "\n\n ~$ _Microchip at your service_"


## Callback Functions and Utils Functions for Bot


# route: /commands
def list_commands(bot, update):
    chat_id = update.message.chat_id
    bot_message = "/start \n/updateallanime \n/updateanime anime_no \n/myanimelist \n/hostip \n/commands"
    bot.send_message(chat_id=chat_id, text=bot_message)


# route: /start
def start(bot, update):
    chat_id = update.message.chat_id
    bot_message = "Hi, I'm Microchip\nI bring you your live anime updates :)"
    bot.send_message(chat_id=chat_id, text=bot_message, parse_mode=telegram.ParseMode.MARKDOWN)


# route: /updateallanime
def update_all_anime(bot, update):
    chat_id = update.message.chat_id
    bot.send_message(chat_id=chat_id, text='Updating your Database', parse_mode=telegram.ParseMode.MARKDOWN)
    anime_list = fetch_anime_db()
    updated_list = []
    results_set = []
    # Use -1 so code actually breaks
    default_id = -1
    for anime_info in anime_list:
        name, _ = tuple(anime_info)
        results = update_anime(bot, update, default_id, anime_info=anime_info, auto_reply=False)
        recent_episode = results['body'][1]
        updated_list.append([name, recent_episode])
        results_set.append(results)

    update_anime_db(updated_list)
    send_batch_anime_results(bot, chat_id, results_set)
    bot.send_message(chat_id=chat_id, text='Your anime database is up to date :)',
                     parse_mode=telegram.ParseMode.MARKDOWN)


# route: /updateanime
def update_anime(bot, update, args, anime_info=None, auto_reply=True):
    chat_id = update.message.chat_id
    if anime_info:
        name, last_episode = tuple(anime_info)
    else:
        anime_id = int(args[0])
        all_anime = fetch_anime_db()
        try:
            anime_info = all_anime[anime_id-1]
        except Exception as e:
            print(e)
            bot.send_message(chat_id=chat_id, text='You entered an invalid option. Type: \n\n/myanimelist' \
            '\n\nto see a list of anime and their numbers. Then use: \n\n/updateanime <the_anime_number>')
            return None
        name, last_episode = tuple(anime_info)
    if auto_reply:
        update_message = 'Updating *{0}*'.format(name)
    bot.send_message(chat_id=chat_id, text=update_message,
                     parse_mode = telegram.ParseMode.MARKDOWN)
    results = scraper.get_episode_updates(name, last_episode)
    if auto_reply:
        results_set = [results]
        send_batch_anime_results(bot, chat_id, results_set, send_updates_only=False)
    return results


# route: /myanimelist
def get_anime_list(bot, update):
    chat_id = update.message.chat_id
    anime_list = fetch_anime_db()
    bot_message = "Your Anime List\n\n"
    for index, anime_info in enumerate(anime_list):
        name, last_episode = tuple(anime_info)
        bot_message += "*{0}*. {1} ({2})\n".format(index+1, name, last_episode)
    bot_message += BOT_SIGNATURE
    bot.send_message(chat_id=chat_id, text=bot_message, parse_mode=telegram.ParseMode.MARKDOWN)


# route: /hostip
def get_host_ip(bot, update):
    chat_id = update.message.chat_id
    ip = get_ip_address()
    bot_message = "The back-end of this bot is running on: {0}".format(ip)
    bot_message += BOT_SIGNATURE
    bot.send_message(chat_id=chat_id, text=bot_message, parse_mode=telegram.ParseMode.MARKDOWN)


def send_batch_anime_results(bot, chat_id, results_set, send_updates_only=True):
    for results in results_set:
       if results['success']:
            # If it should send updates only and there are no new episodes
            # then it should pass
           if send_updates_only and results['body'][0] == 0:
               pass
           else:
               bot_message = construct_anime_update_message(results)
               bot.send_message(chat_id = chat_id, text=bot_message,
                                parse_mode = telegram.ParseMode.MARKDOWN)
       else:
           bot_message = construct_anime_update_message(results)
           bot.send_message(chat_id = chat_id, text=bot_message,
                            parse_mode = telegram.ParseMode.MARKDOWN)


def construct_anime_update_message(scraping_results):
    name = scraping_results['anime_name']
    results = scraping_results
    bot_signature = "\n\n ~$ _Microchip at your service_"
    if results['success']:
        new_eps, recent_ep, last_ep = tuple(results['body'])
        if new_eps == 0:
            bot_message = "Hi there,\n\n There have been no new updates to" \
                          " the anime: *{0}* \n\n The last episode you" \
                          " watched was Episode {1} and the most recent" \
                          " episode is Episode {2}".format(name, last_ep, recent_ep)
        else:
            bot_message = "Hi there,\n\nThere have been updates to an anime" \
                          " you watch:\n\n*{0}* \n\nThe last episode you watched" \
                          " was Episode {1}. There have been {2} more episode(s) since" \
                          " you last got updated and the most recent episode is" \
                          " Episode {3}".format(name, last_ep, new_eps, recent_ep)
    else:
        error_message = results['message']
        bot_message = "Error while updating anime database:\n\n" + error_message
    bot_message = bot_message + bot_signature
    return bot_message


# Function for getting IP address:
# Source: https://stackoverflow.com/questions/24196932/how-can-i-get-the-ip-address-of-eth0-in-python
# Answer by: jeremyjjbrown
def get_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    return s.getsockname()[0]


if __name__ == '__main__':
    MY_CHAT_ID = "288757601"
    BOT_TOKEN = "585202235:AAExMUAhLZllUHiIAqke8e71Bxr-pzEY5Kg"
    UPDATE = {'message':{'chat_id': MY_CHAT_ID}}
    bot = telegram.Bot(token=BOT_TOKEN)

    # Test classes for creating update object
    class Message():
        def __init__(self, chat_id):
            self.chat_id = chat_id

    class Update():
        def __init__(self, chat_id):
            self.message = Message(chat_id)

    update = Update(MY_CHAT_ID)
    update_anime(bot, update, 4)

