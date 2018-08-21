'''
    Module for handling the scraping of anime information from gogoanime
'''
import re
import requests
from bs4 import BeautifulSoup

session = requests.Session()

BASE_URL = "https://www.gogoanime.se/"
BASE_SEARCH_URL = "https://www.gogoanime.se/search.html?keyword="
DEFAULT_EP = '0'
EP_START = '0'
EP_END = '5000'
EP_NUM_REGEX = r"EP\s(?P<episode_number>\d+)"
EP_NUM_PATTERN = re.compile(EP_NUM_REGEX, re.IGNORECASE)
EPISODES_LIST_BASE_URL = "https://www.gogoanime.se/load-list-episode?"


def search_for_anime(anime_name):
    '''
        Function to return the results of a search term.

        It takes the search term as the input and returns a list of tuples, 
        where each tuple contains a matching anime name and the url to the 
        main page of that anime

        >>> search_for_anime("A Town Where You Live")
        [('A Town Where You Live', 'https://www.gogoanime.se/category/a-town-where-you-live')]

        >>> search_for_anime("AnImpossibleThingToFind")
        []
    '''
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
    '''
        Function to get the url of the page that contains the list of episodes
        for a specified anime

        It accepts the url for the main gogoanime page of the anime, and returns
        the url that contains, solely, the list of episodes

        >>> get_episode_list_url("https://www.gogoanime.se/category/a-town-where-you-live")
        'https://www.gogoanime.se/load-list-episode?ep_start=0&ep_end=5000&id=184&default_ep=0'

        >>> get_episode_list_url("https://www.gogoanime.se/category/non-existent-url-supplied")
        Traceback (most recent call last):
            ...
        AssertionError: The url provided does not point to the main page of any anime on gogoanime
    '''
    response = session.get(main_page_link)
    main_page_soup = BeautifulSoup(response.content, 'html.parser')
    assert main_page_soup.find('input', {'id': 'movie_id'}), "The url provided does not " \
        "point to the main page of any anime on gogoanime"

    movie_id = main_page_soup.find('input', {'id': 'movie_id'})['value']

    episodes_list_url = EPISODES_LIST_BASE_URL + \
                        'ep_start=' + EP_START + \
                        '&ep_end=' + EP_END + \
                        '&id=' + movie_id + \
                        '&default_ep=' + DEFAULT_EP

    return episodes_list_url


def get_episode_updates(episodes_list_url, last_episode=None):
    '''
        Function to get the list of episodes for an anime and determine
        if there have been any updates.

        It accepts the url to the list of episodes and an optional parameter
        for the last episode recorded. It then returns a tuple containing the
        number of new episodes, the most recent episode number, and the last
        episode recorded (the one that was passed to it when it was called).
        If no value is given to last_episode when the function is called, or if
        last_episode is None, it will return the same tuple but with number of new
        episodes and last episode set to None.

        >>> get_episode_updates("https://www.gogoanime.se/load-list-episode?ep_start=0&ep_end=5000&id=7144&default_ep=0")
        (None, 5, None)

        >>> get_episode_updates("https://www.gogoanime.se/load-list-episode?ep_start=0&ep_end=5000&id=7144&default_ep=0", 4)
        (1, 5, 4)
    '''
    response = session.get(episodes_list_url)
    episodes_list_soup = BeautifulSoup(response.content, 'html.parser')
    all_li = episodes_list_soup.find_all('li')
    latest_li = all_li[0]
    recent_ep = latest_li.find('div', {'class', 'name'}).text.strip(' ')
    recent_episode = int(EP_NUM_PATTERN.search(recent_ep).group('episode_number'))

    if last_episode is not None:
        num_new_episodes = recent_episode - last_episode
        return (num_new_episodes, recent_episode, last_episode)
    else:
        return (None, recent_episode, None)
