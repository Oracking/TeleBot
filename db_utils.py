from models import User, Anime


def create_user(chat_id, nickname=None):
    chat_id = int(chat_id)
    new_user, created = User.get_or_create(chat_id=chat_id)
    if nickname:
        nickname = nickname.replace('\n', '').strip(' ')
        new_user.nickname = nickname
        new_user.save()
    return new_user


def nickname_user(chat_id, nickname):
    chat_id = int(chat_id)
    user, created = User.get_or_create(chat_id=chat_id)
    try:
        nickname = nickname.replace('\n', '').strip(' ')
        user.nickname = nickname
        user.save()
        return (True, user)
    except:
        return (False, None)


def anime_in_db(chat_id, anime_name):
    try:
        Anime.get(name=anime_name)
        return True
    except:
        return False


def user_is_subscribed(chat_id, anime_name):
    chat_id = int(chat_id)
    if not anime_in_db(chat_id, anime_name):
        return False
    else:
        user, created = User.get_or_create(chat_id=chat_id)
        anime = Anime.get(name=anime_name)
        if user in anime.users:
            return True
        return False


def subscribe_user_to_anime(chat_id, anime_name):
    chat_id = int(chat_id)
    if not user_is_subscribed(chat_id, anime_name):
        anime = Anime.get(name=anime_name)
        user = User.get(chat_id=chat_id)
        anime.users.add(user)


def add_new_anime(chat_id, anime_name, episodes_list_url, last_episode):
    chat_id, last_episode = (int(chat_id), int(last_episode))
    user = User.get(chat_id=chat_id)
    new_anime, created = Anime.get_or_create(name=anime_name)
    new_anime.episodes_url, new_anime.last_episode = (episodes_list_url, last_episode)
    new_anime.save()
    if not user_is_subscribed(chat_id, anime_name):
        user.animes.add(new_anime)
    return new_anime


def get_all_anime(chat_id):
    user = User.get(chat_id=chat_id)
    anime_list = []
    animes = user.animes.order_by(Anime.name)
    for anime in animes:
        anime_list.append((anime.name, anime.get_id(), anime.last_episode, anime.episodes_url))
    return anime_list


def get_anime_by_id(chat_id, anime_id):
    try:
        anime = Anime.get(id=anime_id)
        return anime
    except:
        return None


def get_anime_subscriber_bundle():
    animes = Anime.select()
    bundle = {}
    for anime in animes:
        bundle[anime.name] = [anime, []]
        users = anime.users
        for user in users:
            bundle[anime.name][1].append(user.chat_id)
    return bundle


if __name__ == '__main__':
    pass
    # pseudo_id = 4354
    # new_user = create_user(pseudo_id)
    # add_new_anime(pseudo_id,'Mesu','htt',49)
    # add_new_anime(pseudo_id, 'Soku', 'htt', 49)
    # add_new_anime(pseudo_id, 'Joku', 'htt', 49)
    # all_anime = get_all_anime(pseudo_id)
    # print(all_anime)