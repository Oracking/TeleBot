from telegram.ext import ConversationHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
import gogo_scraper
import db_utils


# route: /start
def start(bot, update):
    chat_id = update.message.chat_id
    db_utils.create_user(chat_id=chat_id)
    update.message.reply_text("Hi, I'm microchip. What should I call you?")
    return 1


# Conversational Route
# Conversational Handler Path: start -> nickname_user -> end
def nickname_user(bot, update):
    chat_id = update.message.chat_id
    nickname = update.message.text
    success, _ = db_utils.nickname_user(chat_id, nickname)
    if success:
        update.message.reply_text("Nice meeting you, {0}".format(nickname))
        update.message.reply_text("I'm guessing you watch anime. I can help you keep updated on the anime"
                                  " you watch.")
        update.message.reply_text("Use the command /addanime to search for an anime to add to my database.")
        return ConversationHandler.END
    else:
        update.message.reply_text("I'm having trouble remembering that. Please choose something shorter")
        return 1


# route: /cancel
def cancel(bot, update):
    update.message.reply_text("Your operation has been cancelled")
    return ConversationHandler.END


# Routed by dispatcher error message
def error(bot, udpate, error):
    print(error)


# route: /addanime
# Conversational Handler Path: add_anime -> search_anime -> end
def add_anime(bot, update):
    update.message.reply_text("Great! What anime would you like to add?")
    return 1


def research(bot, update):
    update.message.reply_text("Cool. What is the name of the anime?")
    return 1


# Conversational Route
# Conversational Handler Path: add_anime -> search_anime -> end
def search_anime(bot, update):
    anime_name = update.message.text
    chat_id = update.message.chat_id
    update.message.reply_text("Let me check the books 📖")
    matches = gogo_scraper.search_for_anime(anime_name=anime_name)
    buttons = []

    if len(matches) == 0:
        bot.send_message(chat_id=chat_id, text="Hmm 🤔, I didn't seem to find any anime like that." 
                                               " You can try searching with a different name",
        )
        return 1

    for index, match in enumerate(matches):
        name, _ = match
        button = InlineKeyboardButton(text=name, callback_data='addanimetodb|||{0}'.format(index))
        buttons.append([button])

    reply_markup = InlineKeyboardMarkup(buttons)
    bot.send_message(chat_id=chat_id, text='Here is a list of anime that match: *{0}*'.format(anime_name),
                     reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)
    update.message.reply_text("Tap on the one that matches what you were looking for. Use /research if your"
                              " anime did not show up.")
    return ConversationHandler.END


# route: /removeanime
def remove_anime(bot, update):
    update.message.reply_text("Hold on. Let me get your anime list")
    chat_id = update.message.chat_id
    anime_set = db_utils.get_all_anime(chat_id)
    buttons = []
    for anime_info in anime_set:
        name, id, _, _ = anime_info
        button = InlineKeyboardButton(text=name, callback_data="confirmremoval|||{0}".format(id))
        buttons.append([button])
    reply_markup = InlineKeyboardMarkup(buttons)
    bot.send_message(chat_id=chat_id, text="Here are the anime you are following", reply_markup=reply_markup)
    bot.send_message(chat_id=chat_id, text="Tap on the one that you want to remove.")


# route: /updateanime
def update_anime(bot, update):
    chat_id = update.message.chat_id
    #update.message.reply_text('Let me pull up your anime list')
    bot.send_message(chat_id=chat_id, text='Let me pull up your anime list')
    anime_set = db_utils.get_all_anime(chat_id)
    buttons = []
    for anime_info in anime_set:
        name, id, _, _ = anime_info
        button = InlineKeyboardButton(text=name, callback_data="updateanime|||{0}".format(id))
        buttons.append([button])
    reply_markup = InlineKeyboardMarkup(buttons)
    bot.send_message(chat_id=chat_id, text="Here are the anime you are following", reply_markup=reply_markup)
    #update.message.reply_text('Tap the one you want to update')
    bot.send_message(chat_id=chat_id, text='Tap the one you want to update')


# route: /myanime
def get_anime_list(bot, update):
    chat_id = update.message.chat_id
    anime_list = db_utils.get_all_anime(chat_id)
    bot_message = "Your Anime List\n\n"
    for index, anime_info in enumerate(anime_list):

        # anime_info = (anime_name, id, last_episode, episodes_url)
        name, _, last_episode, _ = anime_info
        bot_message += "*{0}*. {1} ({2})\n".format(index + 1, name, last_episode)
    bot.send_message(chat_id=chat_id, text=bot_message, parse_mode=ParseMode.MARKDOWN)


# route: /updateallanime
def update_all_anime(bot, update):
    chat_id = update.message.chat_id
    update.message.reply_text('Updating all the anime you watch. This might take a while.')
    anime_set = db_utils.get_all_anime(chat_id)
    batch_results = []
    for anime_info in anime_set:
        # anime_info = (anime_name, id, last_episode, episodes_url)
        episode_updates = gogo_scraper.get_episode_updates(anime_info[3], anime_info[2])
        new_eps, recent_ep, last_ep = episode_updates
        batch_results.append((anime_info[0], new_eps, recent_ep, last_ep))

    send_batch_update_messages(bot, chat_id, batch_results, send_changes_only=True)
    update.message.reply_text("Done updating. If nothing showed then you are up to date.")


def auto_update_user(bot, job):
    bundle = db_utils.get_anime_subscriber_bundle()
    batch_results = []
    for anime in bundle.keys():
        anime, related_chat_ids = tuple(bundle[anime])
        results = gogo_scraper.get_episode_updates(anime.episodes_url, anime.last_episode)
        new_eps, recent_ep, last_ep = results
        anime.last_episode = recent_ep
        anime.save()
        for chat_id in related_chat_ids:
            send_batch_update_messages(bot, chat_id, [(anime.name, new_eps, recent_ep, last_ep)], send_changes_only=True)


# Main CallBack Route
def callback_query_handler(bot, update):
    #General variables used by all routes
    chat_id = update.callback_query.message.chat.id
    callback_data = update.callback_query.data
    redirect_route, user_choice = tuple(callback_data.split('|||'))
    user_choice = int(user_choice)

    # These variables are only used for addanimetodb route
    prev_message = update.callback_query.message.text
    start_of_user_query = len("Here is a list of anime that match: ")
    user_query = prev_message[start_of_user_query:]

    # Handle the addition of an anime to a user's watch list
    if redirect_route == 'addanimetodb':
        matches = gogo_scraper.search_for_anime(user_query)
        anime_name, main_page_link = matches[user_choice]

        if db_utils.user_is_subscribed(chat_id, anime_name):
            bot.send_message(chat_id=chat_id, text="Great news. Looks like *{0}* is already part of the "
                                                   "list of animes you are following".format(anime_name),
                             parse_mode=ParseMode.MARKDOWN)

        elif db_utils.anime_in_db(chat_id, anime_name):
            db_utils.subscribe_user_to_anime(chat_id, anime_name)

        else:
            episodes_list_url = gogo_scraper.get_episode_list_url(main_page_link)
            _, last_episode, _ = gogo_scraper.get_episode_updates(episodes_list_url)
            db_utils.add_new_anime(chat_id=chat_id, anime_name=anime_name, episodes_list_url=episodes_list_url,
                                   last_episode=last_episode)

            bot.send_message(chat_id=chat_id, text="Alright! *{0}* has been successfully added to my database."
                             " I will notify you when new episodes are released.".format(anime_name),
                             parse_mode=ParseMode.MARKDOWN)
            bot.send_message(chat_id=chat_id, text="Note: You can use /updateanime to manually check for"
                             " updates or the current episode that's out.")


    # Handle the manual updating of one of the user's animes
    if redirect_route == "updateanime":
        anime_id = user_choice
        anime = db_utils.get_anime_by_id(chat_id, anime_id)

        if anime:
            bot.send_message(chat_id=chat_id, text='Alright, updating *{0}*'.format(anime.name),
                             parse_mode=ParseMode.MARKDOWN)
            episodes_list_url, last_episode = (anime.episodes_url, anime.last_episode)
            episode_updates = gogo_scraper.get_episode_updates(episodes_list_url, last_episode)
            new_eps, recent_ep, last_ep = episode_updates
            anime.last_episode = recent_ep
            anime.save()
            send_batch_update_messages(bot, chat_id, [(anime.name, new_eps, recent_ep, last_ep)])


    #Handle the confirmation of the removal of an anime from user database
    if redirect_route == 'confirmremoval':
        anime = db_utils.get_anime_by_id(chat_id, user_choice)
        buttons = [[InlineKeyboardButton(text="Yes", callback_data="removeanime|||{0}".format(user_choice)),
                   InlineKeyboardButton(text="No", callback_data="cancel|||{0}".format(user_choice))]]
        reply_markup = InlineKeyboardMarkup(buttons)
        bot.send_message(chat_id=chat_id, text="Are you sure you want to remove *{0}* from your"
                                               " anime list?".format(anime.name),
                         reply_markup=reply_markup, parse_mode = ParseMode.MARKDOWN)


    # Handle the removal of the anime from a user's anime list
    if redirect_route == 'removeanime':
        anime = db_utils.get_anime_by_id(chat_id, user_choice)
        db_utils.unsubscribe_user_from_anime(chat_id, anime.name)
        bot.send_message(chat_id=chat_id, text="Done")


    # Handle the cancellation of a callback query
    if redirect_route == 'cancel':
        bot.send_message(chat_id=chat_id, text="Your operation has been cancelled")


    return ConversationHandler.END


def send_batch_update_messages(bot, chat_id, scraping_results_batch, send_changes_only=False):
    for scraping_results in scraping_results_batch:
        # scraping_results = (anime_name, num_new_eps, recent_episode, last_ep)
        if scraping_results[1] == 0:
            bot_message = "The most recent episode of *{0}* is Episode {1}. There have been no new episodes" \
                          " since I last checked".format(scraping_results[0], scraping_results[2])
        else:
            if scraping_results[1] == 1:
                episode = 'episode'
            else:
                episode = 'episodes'
            bot_message = "Good news! There have been updates to *{0}*.\n\n Since I last checked, there have been" \
                          " {1} more {2}. The most recent episode is Episode {3}".format(scraping_results[0],
                                                                                         scraping_results[1],
                                                                                         episode,
                                                                                         scraping_results[2])

        if send_changes_only and scraping_results[1] == 0:
            pass
        else:
            bot.send_message(chat_id=chat_id, text=bot_message, parse_mode=ParseMode.MARKDOWN)
