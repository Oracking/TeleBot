import requests
from bs4 import BeautifulSoup

session = requests.Session()

BASE_URL = "https://www1.gogoanime.se/"
BASE_SEARCH_URL = "https://www1.gogoanime.se/search.html?keyword="
DEFAULT_EP = '0'
EP_START = '0'
EP_END = '5000'
EPISODES_LIST_BASE_URL = "https://www1.gogoanime.se/load-list-episode?"


def get_episode_updates(anime, last_episode):
    url_search_term = anime.replace(' ', '%20')
    search_url = BASE_SEARCH_URL + url_search_term
    response = session.get(search_url)
    search_result_soup = BeautifulSoup(response.content, 'html.parser')
    a = search_result_soup.find('a', {'title': anime})

    if a:

        short_link = a['href']
        main_page_link = BASE_URL + short_link[1:]
        response = session.get(main_page_link)
        main_page_soup = BeautifulSoup(response.content, 'html.parser')
        movie_id = main_page_soup.find('input', {'id': 'movie_id'})['value']

        episodes_list_url = EPISODES_LIST_BASE_URL +     \
                            'ep_start=' + EP_START +     \
                            '&ep_end=' + EP_END +        \
                            '&id=' + movie_id +          \
                            '&default_ep=' + DEFAULT_EP

        response = session.get(episodes_list_url)
        episodes_list_soup = BeautifulSoup(response.content, 'html.parser')
        all_li = episodes_list_soup.find_all('li')
        num_new_episodes = len(all_li) - last_episode
        recent_episode = len(all_li)
        return {'success': True, 'message': None, 'anime_name': anime,
                'body': (num_new_episodes, recent_episode, last_episode)}

    else:

        return {'success': False, 'body': None, 'anime_name': anime,
                'message':
                'The anime: \'*{0}*\' was not found on gogoanime'.format(anime)}
