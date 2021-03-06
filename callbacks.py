'''
    User callbacks
'''
import time
from collections import namedtuple
from telegram.ext import ConversationHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
import gogo_scraper
import db_utils


Update = namedtuple(
    'Update', ('anime_obj', 'num_new_eps', 'recent_ep', 'last_ep')
)

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
        update.message.reply_text("I'm guessing you watch anime. I can help "
                                  "you keep updated on the anime you watch.")
        update.message.reply_text("Use the command /addanime to search for an "
                                  "anime to add to my database. Alternatively, "
                                  "use /help to view my list of commands")
        return ConversationHandler.END
    else:
        update.message.reply_text("I'm having trouble remembering that. "
                                  "Please choose something shorter")
        return 1


# route: /cancel
def cancel(bot, update):
    update.message.reply_text("Your operation has been cancelled")
    return ConversationHandler.END


# Routed by dispatcher error message
def error(bot, udpate, error):
    print(error)


# -----------------------------------------------------------------------------
# route: /addanime
# Conversational Handler Path: add_anime -> search_anime -> end
def add_anime(bot, update):
    update.message.reply_text("Great! What anime would you like to add?")
    return 1


def search_anime(bot, update):
    anime_name = update.message.text
    chat_id = update.message.chat_id
    update.message.reply_text("Let me check the books 📖")
    matches = gogo_scraper.search_for_anime(anime_name=anime_name)
    buttons = []

    if len(matches) == 0:
        bot.send_message(
            chat_id=chat_id,
            text="Hmm 🤔, I didn't seem to find any anime like that. You can "
                 "try searching with a different name. Or cancel search with "
                 "/cancel",
        )
        return 1

    for index, match in enumerate(matches):
        name, _ = match
        button = InlineKeyboardButton(
            text=name, callback_data='addanimetodb|||{0}'.format(index)
        )
        buttons.append([button])

    reply_markup = InlineKeyboardMarkup(buttons)
    bot.send_message(chat_id=chat_id,
                     text="Here is a list of anime that "
                          "match: *{0}*".format(anime_name),
                     reply_markup=reply_markup,
                     parse_mode=ParseMode.MARKDOWN)
    update.message.reply_text("Tap on the one that matches what you were "
                              "looking for. Use /research if your anime did "
                              "not show up.")
    return 2


def research(bot, update):
    update.message.reply_text("Cool. What is the name of the anime?")
    return 1


def add_anime_callback(bot, update):
    chat_id = update.callback_query.message.chat.id
    callback_data = update.callback_query.data
    redirect_route, user_choice = tuple(callback_data.split('|||'))
    user_choice = int(user_choice)

    # These variables are only used for addanimetodb route
    prev_message = update.callback_query.message.text
    start_of_user_query = len("Here is a list of anime that match: ")
    user_query = prev_message[start_of_user_query:]

    if redirect_route == 'addanimetodb':
        matches = gogo_scraper.search_for_anime(user_query)
        anime_name, main_page_link = matches[user_choice]

        if db_utils.user_is_subscribed(chat_id, anime_name):
            bot.send_message(chat_id=chat_id,
                             text="Great news. Looks like *{0}* is already "
                                  "part of the list of animes you are "
                                  "following".format(anime_name),
                             parse_mode=ParseMode.MARKDOWN)

            return ConversationHandler.END

        elif db_utils.anime_in_db(chat_id, anime_name):
            db_utils.subscribe_user_to_anime(chat_id, anime_name)

        else:
            episodes_list_url = gogo_scraper.get_episode_list_url(
                main_page_link
            )
            _, last_episode, _ = gogo_scraper.get_episode_updates(
                episodes_list_url
            )

            db_utils.add_new_anime(chat_id=chat_id, anime_name=anime_name,
                                   episodes_list_url=episodes_list_url,
                                   last_episode=last_episode)

        bot.send_message(chat_id=chat_id,
                         text="Alright! *{0}* has been successfully added to "
                              "my database. I will notify you when new "
                              "episodes are released.".format(anime_name),
                         parse_mode=ParseMode.MARKDOWN)
        bot.send_message(chat_id=chat_id,
                         text="Note: You can use /updateanime to manually "
                              "check for updates or the current episode that's "
                              "out.")

    return ConversationHandler.END

# -----------------------------------------------------------------------------

# route: /updateanime
def update_anime(bot, update):
    chat_id = update.message.chat_id
    update.message.reply_text('Let me pull up your anime list')
    anime_set = db_utils.get_all_anime(chat_id)
    buttons = []
    for anime_info in anime_set:
        name, anime_id, _, _ = anime_info
        button = InlineKeyboardButton(
            text=name, callback_data="updateanime|||{0}".format(anime_id)
        )
        buttons.append([button])
    reply_markup = InlineKeyboardMarkup(buttons)
    bot.send_message(chat_id=chat_id,
                     text="Here are the anime you are following",
                     reply_markup=reply_markup)
    bot.send_message(chat_id=chat_id, text='Tap the one you want to update')

    return 1


def update_anime_callback(bot, update):
    chat_id = update.callback_query.message.chat.id
    callback_data = update.callback_query.data
    redirect_route, user_choice = tuple(callback_data.split('|||'))
    user_choice = int(user_choice)

    if redirect_route == "updateanime":
        anime_id = user_choice
        anime = db_utils.get_anime_by_id(chat_id, anime_id)

        if anime:
            bot.send_message(chat_id=chat_id,
                             text='Alright, updating *{0}*'.format(anime.name),
                             parse_mode=ParseMode.MARKDOWN)
            episodes_list_url, last_episode = (anime.episodes_url,
                                               anime.last_episode)
            episode_updates = gogo_scraper.get_episode_updates(
                episodes_list_url, last_episode
            )
            new_eps, recent_ep, last_ep = episode_updates

            anime.last_episode = recent_ep
            anime.save()

            if recent_ep != last_ep:
                bundle = db_utils.get_anime_subscriber_bundle(anime.name)
                anime, related_chat_ids = tuple(bundle[anime.name])
                for chat_id in related_chat_ids:
                    send_batch_update_messages(
                        bot, chat_id,
                        [Update(anime, new_eps, recent_ep, last_ep)]
                    )
            else:
                send_batch_update_messages(
                    bot, chat_id, [Update(anime, new_eps, recent_ep, last_ep)]
                )

    return ConversationHandler.END


# -----------------------------------------------------------------------------

def update_all_anime(bot, update):
    chat_id = update.message.chat_id
    update.message.reply_text("Updating all the anime you watch. "
                              "This might take a while.")
    anime_set = db_utils.get_all_anime(chat_id)
    for anime_info in anime_set:
        # anime_info = (anime_name, anime_id, last_episode, episodes_url)
        episode_updates = gogo_scraper.get_episode_updates(anime_info[3],
                                                           anime_info[2])
        new_eps, recent_ep, last_ep = episode_updates
        bundle = db_utils.get_anime_subscriber_bundle(anime_name=anime_info[0])
        anime_name, related_chat_ids = tuple(bundle[anime_info[0]])

        anime = db_utils.get_anime_by_id(chat_id, anime_info[1])
        anime.last_episode = recent_ep
        anime.save()

        for chat_id in related_chat_ids:
            send_batch_update_messages(
                bot, chat_id, [Update(anime, new_eps, recent_ep, last_ep)],
                send_changes_only=True
            )
    update.message.reply_text("Done updating. If nothing showed then you are up"
                              " to date.")

# -----------------------------------------------------------------------------

# route: /removeanime
def remove_anime(bot, update):
    update.message.reply_text("Hold on. Let me get your anime list")
    chat_id = update.message.chat_id
    anime_set = db_utils.get_all_anime(chat_id)
    buttons = []
    for anime_info in anime_set:
        name, anime_id, _, _ = anime_info
        button = InlineKeyboardButton(
            text=name, callback_data="confirmremoval|||{0}".format(anime_id)
        )
        buttons.append([button])

    reply_markup = InlineKeyboardMarkup(buttons)
    bot.send_message(chat_id=chat_id,
                     text="Here are the anime you are following",
                     reply_markup=reply_markup)
    bot.send_message(chat_id=chat_id,
                     text="Tap on the one that you want to remove.")

    return 1


def confirm_removal_callback(bot, update):
    chat_id = update.callback_query.message.chat.id
    callback_data = update.callback_query.data
    redirect_route, user_choice = tuple(callback_data.split('|||'))
    user_choice = int(user_choice)

    if redirect_route == 'confirmremoval':
        anime = db_utils.get_anime_by_id(chat_id, user_choice)
        buttons = [[
            InlineKeyboardButton(text="Yes",
                                 callback_data="removeanime|||{0}"
                                 .format(user_choice)),
            InlineKeyboardButton(text="No",
                                 callback_data="cancel|||{0}"
                                 .format(user_choice))
        ]]

        reply_markup = InlineKeyboardMarkup(buttons)
        bot.send_message(chat_id=chat_id,
                         text="Are you sure you want to remove *{0}* from your"
                              " anime list?".format(anime.name),
                         reply_markup=reply_markup,
                         parse_mode=ParseMode.MARKDOWN)
    return 2


def finally_remove_anime_callback(bot, update):
    chat_id = update.callback_query.message.chat.id
    callback_data = update.callback_query.data
    redirect_route, user_choice = tuple(callback_data.split('|||'))
    user_choice = int(user_choice)

    if redirect_route == 'removeanime':
        anime = db_utils.get_anime_by_id(chat_id, user_choice)
        db_utils.unsubscribe_user_from_anime(chat_id, anime.name)
        bot.send_message(chat_id=chat_id, text="Done")


    # Handle the cancellation of a callback query
    if redirect_route == 'cancel':
        bot.send_message(chat_id=chat_id,
                         text="Your operation has been cancelled")


    return ConversationHandler.END


# route: /myanime
def get_anime_list(bot, update):
    chat_id = update.message.chat_id
    anime_list = db_utils.get_all_anime(chat_id)
    if len(anime_list) > 0:
        bot_message = "Your Anime List\n\n"
        for index, anime_info in enumerate(anime_list):

            # anime_info = (anime_name, id, last_episode, episodes_url)
            name, _, last_episode, _ = anime_info
            bot_message += "*{0}*. {1} ({2})\n".format(index + 1, name,
                                                       last_episode)
    else:
        bot_message = ("Unfortunately, you are not following any anime at "
                       "the moment")
    bot.send_message(chat_id=chat_id, text=bot_message,
                     parse_mode=ParseMode.MARKDOWN)


# route: /updateallanime
def auto_update_users(bot, job):
    bundle = db_utils.get_anime_subscriber_bundle()
    for anime_name, subscriber_bundle in bundle.items():
        anime, related_chat_ids = tuple(subscriber_bundle)
        results = gogo_scraper.get_episode_updates(anime.episodes_url,
                                                   anime.last_episode)
        new_eps, recent_ep, last_ep = results
        anime.last_episode = recent_ep
        anime.save()
        for chat_id in related_chat_ids:
            send_batch_update_messages(bot, chat_id, [Update(anime,
                                                             new_eps,
                                                             recent_ep,
                                                             last_ep)],
                                       send_changes_only=True)


def unknown_handler(bot, update):
    bot.send_message(
        chat_id=update.message.chat_id,
        text="Sorry, I do not understand. Please use one of my availabe "
             "commands. If you do not know what they are, use /help",
        parse_mode=ParseMode.MARKDOWN
    )


def help(bot, update):
    help_message = (
        "Hi, I am the AnimePlug.\n"
        "You can get to me to supply you with episode updates on any anime "
        "that you follow using one of my available commands\n\n"

        "*Commands*:\n\n"

        "/start\n"
        "This command is used to introduce ourselves to each other. "
        "You can use this command anytime to change how I refer to you.\n\n"

        "/myanime\n"
        "This command is used to list all the anime you are currently "
        "following.\n\n"

        "/addanime\n"
        "This command let's me know you want to add a new anime to your list. "
        "Once you call this, I will help you add a new anime.\n\n"

        "/updateanime\n"
        "If you just can't wait for me to automatically check for new episodes "
        "of an anime, you can use this command to manually check up on one of "
        "the anime you have added. This command is also effective if you just "
        "want to get the download url of the recent episode of an anime you "
        "follow.\n\n"

        "/updateallanime\n"
        "This is similar to the /updateanime command but checks for updates on "
        "all the anime you have added.\n\n"

        "/removeanime\n"
        "This is used to remove an anime from the list of anime you are "
        "following\n\n"

        "/cancel\n"
        "If at any point during a process (such as adding or updating an "
        "anime), you feel like quitting, just use this command and I'll end "
        "it.\n\n"
    )

    bot.send_message(chat_id=update.message.chat_id,
                     text=help_message,
                     parse_mode=ParseMode.MARKDOWN)


def send_batch_update_messages(bot, chat_id, scraping_results_batch,
                               send_changes_only=False):

    download_mesg = ''
    user = db_utils.get_user_by_id(chat_id)
    username = user.nickname or ''

    for scraping_results in scraping_results_batch:
        # scraping_results = (anime_name, num_new_eps, recent_episode, last_ep)
        if scraping_results.num_new_eps == 0:
            bot_message = ("The most recent episode of *{0}* is Episode {1}. "
                           "There have been no new episodes since I last "
                           "checked".format(scraping_results.anime_obj.name,
                                            scraping_results.recent_ep)
                           )
        else:
            if scraping_results.num_new_eps == 1:
                episode = 'episode'
                has_have = 'has'
            else:
                episode = 'episodes'
                has_have = 'have'
            bot_message = ("Good news {0}! There have been updates to "
                           "*{1}*.\n\n Since I last checked, there {2} been "
                           "{3} more {4}. The most recent episode is Episode "
                           "{5}".format(
                               username, scraping_results.anime_obj.name,
                               has_have, scraping_results.num_new_eps,
                               episode, scraping_results.recent_ep
                           ))


        # Download url message
        episodes_list_url = scraping_results.anime_obj.episodes_url
        try:
            download_url, _ = gogo_scraper.get_episode_download_url(
                episodes_list_url
            )
            download_mesg = ("You can download Episode {0} of *{1}* "
                             "here:".format(scraping_results.recent_ep,
                                            scraping_results.anime_obj.name)
                            )

        except:
            download_url = None
            download_mesg = ("Sadly, I couldn't find any download url "
                             "for episode {}".format(scraping_results.recent_ep)
                            )

        # Actually send messages
        if send_changes_only and scraping_results.num_new_eps == 0:
            pass
        else:

            bot.send_message(chat_id=chat_id,
                             text=bot_message, parse_mode=ParseMode.MARKDOWN)

            if download_mesg:
                bot.send_message(chat_id=chat_id,
                                 text=download_mesg,
                                 parse_mode=ParseMode.MARKDOWN)

            if download_url:
                bot.send_message(chat_id=chat_id, text=download_url)

        # To prevent exceeding telegram's 30 messages per second limit
        time.sleep(0.2)
