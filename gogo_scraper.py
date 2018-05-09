import requests
from bs4 import BeautifulSoup

session = requests.Session()

BASE_URL = "https://www.gogoanime.se/"
BASE_SEARCH_URL = "https://www.gogoanime.se/search.html?keyword="
DEFAULT_EP = '0'
EP_START = '0'
EP_END = '5000'
EPISODES_LIST_BASE_URL = "https://www.gogoanime.se/load-list-episode?"


def search_for_anime(anime_name):
    url_search_term = anime_name.replace(' ', '%20')
    search_url = BASE_SEARCH_URL + url_search_term
    response = session.get(search_url)
    search_result_soup = BeautifulSoup(response.content, 'html.parser')
    p_tags = search_result_soup.find_all('p', {'class': 'name'})
    result_collection = []
    for p_tag in p_tags:
        name = p_tag.a['title']
        short_link = p_tag.a['href']
        main_page_link = BASE_URL + short_link[1:]
        result_collection.append((name, main_page_link))
    return result_collection


def get_episode_list_url(main_page_link):
    response = session.get(main_page_link)
    main_page_soup = BeautifulSoup(response.content, 'html.parser')
    movie_id = main_page_soup.find('input', {'id': 'movie_id'})['value']

    episodes_list_url = EPISODES_LIST_BASE_URL + \
                        'ep_start=' + EP_START + \
                        '&ep_end=' + EP_END + \
                        '&id=' + movie_id + \
                        '&default_ep=' + DEFAULT_EP

    return episodes_list_url


def get_episode_updates(episodes_list_url, last_episode=None):
    response = session.get(episodes_list_url)
    episodes_list_soup = BeautifulSoup(response.content, 'html.parser')
    all_li = episodes_list_soup.find_all('li')
    recent_episode = len(all_li)
    if last_episode:
        num_new_episodes = recent_episode - last_episode
        return (num_new_episodes, recent_episode, last_episode)
    else:
        return (None, recent_episode, None)
