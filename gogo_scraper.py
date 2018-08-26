'''
    Module for handling the scraping of anime information from gogoanime
'''
import re
import requests
from bs4 import BeautifulSoup

SESSION = requests.Session()

BASE_URL = "https://www.gogoanime.se/"
BASE_SEARCH_URL = "https://www.gogoanime.se/search.html?keyword="
EPISODES_LIST_BASE_URL = "https://www.gogoanime.se/load-list-episode?"
DEFAULT_EP = '0'
EP_START = '0'
EP_END = '5000'

# Regular expressions
EP_NUM_REGEX = r"EP\s(?P<episode_number>\d+)"
EP_NUM_PATTERN = re.compile(EP_NUM_REGEX, re.IGNORECASE)
INVALID_DOWNLOAD_LINK_REGEX = r"https://([^\.]+\.)?googleusercontent.*"
INVALID_DOWNLOAD_LINK_PATTERN = re.compile(INVALID_DOWNLOAD_LINK_REGEX)
DOWNLOAD_TEXT_REGEX = r"DOWNLOAD\((?P<video_quality>[\w\d]+?P)-MP4\)"
DOWNLOAD_TEXT_PATTERN = re.compile(DOWNLOAD_TEXT_REGEX)


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
    response = SESSION.get(search_url)
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
    response = SESSION.get(main_page_link)
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

        >>> get_episode_updates("https://www.gogoanime.se/load-list-episode?ep_start=0&ep_end=5000&id=184&default_ep=0")
        (None, 12, None)

        If you specify an episode number
        
        >>> get_episode_updates("https://www.gogoanime.se/load-list-episode?ep_start=0&ep_end=5000&id=184&default_ep=0", 9)
        (3, 12, 9)

        If the episode you specify is greater than the last episode available

        >>> get_episode_updates("https://www.gogoanime.se/load-list-episode?ep_start=0&ep_end=5000&id=184&default_ep=0", 20)
        (0, 12, 20)
    '''
    response = SESSION.get(episodes_list_url)
    episodes_list_soup = BeautifulSoup(response.content, 'html.parser')
    all_li = episodes_list_soup.find_all('li')
    recent_ep = all_li[0].select_one('div.name').text.strip(' ')
    recent_episode = int(EP_NUM_PATTERN.search(recent_ep).group('episode_number'))

    if last_episode is not None:
        num_new_episodes = recent_episode - last_episode
        if num_new_episodes > 0:
            return (num_new_episodes, recent_episode, last_episode)
        return (0, recent_episode, last_episode)
    else:
        return (None, recent_episode, None)

    
def get_episode_download_url(episodes_list_url, episode_number=None):
    '''
        Function to get the download_url of a specified url

        It accepts the url of the episodes_list page

        By default, it just gets the download url of the most recent episode

        >>> get_episode_download_url("https://www.gogoanime.se/load-list-episode?ep_start=0&ep_end=5000&id=153&default_ep=0")
        ('https://video.xx.fbcdn.net/v/t42.9040-2/10000000_211297229481503_3664118707107397632_n.mp4?_nc_cat=0&efg=eyJybHIiOjE1MDAsInJsYSI6NDA5NiwidmVuY29kZV90YWciOiJzdmVfaGQifQ%3D%3D&rl=1500&vabr=949&oh=8537fb152d15ce1cb28dcdc11734a0b7&oe=5B8049B3', None)

        If an episode number is provided, it gets the download url for that episode number

        >>> get_episode_download_url("https://www.gogoanime.se/load-list-episode?ep_start=0&ep_end=5000&id=7144&default_ep=0",
        ... episode_number=2)
        ('https://video.xx.fbcdn.net/v/t42.9040-2/10000000_230189951156549_3709612027203813376_n.mp4?_nc_cat=0&efg=eyJybHIiOjE1MDAsInJsYSI6NDA5NiwidmVuY29kZV90YWciOiJzdmVfaGQifQ%3D%3D&rl=1500&vabr=768&oh=41ce7c0c63da55b397f47768f0778e52&oe=5B7F1F8B', None)

        If the episode number provided is not within the available episodes it will raise a ValueError

        >>> get_episode_download_url("https://www.gogoanime.se/load-list-episode?ep_start=0&ep_end=5000&id=153&default_ep=0",
        ... episode_number=1000)
        Traceback (most recent call last):
            ...
        ValueError: Episode number 1000 out of the range of available episodes. Episodes for this anime are in the range of 1 - 25

        Test for movie (anime with one episode)

        >>> get_episode_download_url("https://www.gogoanime.se/load-list-episode?ep_start=0&ep_end=1&id=7087&default_ep=0", 1)
        ('https://video.xx.fbcdn.net/v/t42.9040-2/10000000_1747977148611324_1412507683004612608_n.mp4?_nc_cat=0&efg=eyJybHIiOjE1MDAsInJsYSI6NDA5NiwidmVuY29kZV90YWciOiJzdmVfaGQifQ%3D%3D&rl=1500&vabr=555&oh=bdfc61cac3dd4e43c89af757b565e980&oe=5B7E102C', None)

        Test for download links that have expired

        >>> get_episode_download_url("https://www.gogoanime.se/load-list-episode?ep_start=0&ep_end=1&id=5977&default_ep=0")
        Traceback (most recent call last):
            ...
        AssertionError: All download urls have expired

        Test for download links where quality is specified
        # Test missing here
    '''

    # Get the url for the main page for that particular episode
    response = SESSION.get(episodes_list_url)
    episodes_list_soup = BeautifulSoup(response.content, 'html.parser')
    all_li = episodes_list_soup.find_all('li')

    # Selecting the specific episode number happens here
    if episode_number:
        latest_ep = all_li[0].select_one('div.name').text.strip(' ')
        first_ep = all_li[-1].select_one('div.name').text.strip(' ')
        latest_episode = int(EP_NUM_PATTERN.search(latest_ep).group('episode_number'))
        first_episode = int(EP_NUM_PATTERN.search(first_ep).group('episode_number'))

        if not (episode_number >= first_episode and episode_number <= latest_episode):
            raise ValueError('Episode number {} out of the range of available episodes. '
                             'Episodes for this anime are in the range of {} - {}' \
                             .format(episode_number, first_episode, latest_episode))

        li_index = latest_episode - episode_number
        episode_page_relative_url = all_li[li_index].a['href']

    else:
        episode_page_relative_url = all_li[0].a['href']

    episode_page_url = BASE_URL + episode_page_relative_url.strip(' ').strip('/')

    # Go to the main page for that episode and get the url to the download page
    response = SESSION.get(episode_page_url)
    episode_page_soup  = BeautifulSoup(response.content, 'html.parser')
    episode_download_page_url = episode_page_soup.select_one('div.download-anime').a['href']

    # Go to episode download page and get download link and return it
    response = SESSION.get(episode_download_page_url)
    download_page_soup = BeautifulSoup(response.content, 'html.parser')

    # We need to select from just the first mirror_link since that is the onl
    download_link_divs = download_page_soup.select_one('.mirror_link').select('.dowload')

    for div in download_link_divs:
        download_link = div.a['href']
        if not INVALID_DOWNLOAD_LINK_PATTERN.search(download_link):
            download_text = div.a.text.replace('\n', '').replace(' ', '').upper()
            text_description = DOWNLOAD_TEXT_PATTERN.search(download_text)
            video_quality = None
            if text_description and text_description.group('video_quality') != 'AUTOP':
                video_quality = text_description.group('video_quality')

            return (download_link, video_quality)
    
    # If it gets to this stage without finding the download url, then it should
    # raise an error that all urls on the gogoanime page have expired
    raise AssertionError("All download urls have expired")