'''
    Simple module to run unit tests for scraper
'''
import re
import unittest
from gogo_scraper import (search_for_anime,
                          get_episode_list_url,
                          get_episode_updates,
                          get_episode_download_url)

class TestGogoScraper(unittest.TestCase):

    def test_search_for_anime(self):

        # Test to see if it correctly finds an anime that exists
        search_results = search_for_anime("A Town Where You Live")
        self.assertEqual(search_results[0][0], "A Town Where You Live")
        self.assertEqual(
            search_results[0][1],
            "https://www.gogoanime.se/category/a-town-where-you-live"
        )

        # Test to see if it returns an empty list when it does not
        # find any anime
        search_results = search_for_anime("AnImpossibleThingToFind")
        self.assertIsInstance(search_results, list)
        self.assertEqual(len(search_results), 0)


    def test_get_episode_list_url(self):
        # Test if it correctly finds one if it exists
        url = get_episode_list_url("https://www.gogoanime.se/category/"
                                   "a-town-where-you-live")
        self.assertEqual(
            url,
            "https://www.gogoanime.se/load-list-episode?ep_start=0"
            "&ep_end=5000&id=184&default_ep=0"
        )

        # Test if it correclty raises an AssertionError if it does not
        # find the anime
        with self.assertRaises(AssertionError):
            get_episode_list_url(
                "https://www.gogoanime.se/category/non-existent-url-supplied"
            )


    def test_get_episode_udpates(self):

        # Test results if there are no parameter is provided for
        # last episode
        updates = get_episode_updates("https://www.gogoanime.se/"
                                      "load-list-episode?ep_start=0&"
                                      "ep_end=5000&id=184&default_ep=0")
        self.assertEqual(updates, (None, 12, None))

        # Test results if a parameter is provided for the last episode
        updates = get_episode_updates("https://www.gogoanime.se/"
                                      "load-list-episode?ep_start=0&"
                                      "ep_end=5000&id=184&default_ep=0", 9)
        self.assertEqual(updates, (3, 12, 9))

        # Test results if the value specified for last episode is
        # greater than the last episode on gogoanime
        updates = get_episode_updates("https://www.gogoanime.se/"
                                      "load-list-episode?ep_start=0&"
                                      "ep_end=5000&id=184&default_ep=0", 20)
        self.assertEqual(updates, (0, 12, 20))


    def test_get_episode_download_url(self):
        successful_url_regex = r'^https://video.xx.fbcdn.net/v'
        successful_url_pattern = re.compile(successful_url_regex)

        # Test results when no value is given for the episode_number
        # parameter
        url, _ = get_episode_download_url("https://www.gogoanime.se/"
                                          "load-list-episode?ep_start=0"
                                          "&ep_end=5000&id=153&default_ep=0")
        self.assertTrue(successful_url_pattern.search(url))

        # Test results if value is provided for episode_number parameter
        url, _ = get_episode_download_url("https://www.gogoanime.se/"
                                          "load-list-episode?ep_start=0"
                                          "&ep_end=5000&id=7144&default_ep=0",
                                          episode_number=2)
        self.assertTrue(successful_url_pattern.search(url))

        # Test if a ValueError is raised when the episode number provided
        # is not within the available episodes
        with self.assertRaises(ValueError):
            get_episode_download_url("https://www.gogoanime.se/"
                                     "load-list-episode?ep_start=0"
                                     "&ep_end=5000&id=153&default_ep=0",
                                     episode_number=1000)

        # Special test for movie (anime with one episode)
        url, _ = get_episode_download_url("https://www.gogoanime.se/"
                                          "load-list-episode?ep_start=0"
                                          "&ep_end=1&id=7087&default_ep=0", 1)
        self.assertTrue(successful_url_pattern.search(url))

        # Test for download links that have expired
        with self.assertRaises(AssertionError):
            get_episode_download_url("https://www.gogoanime.se/"
                                     "load-list-episode?ep_start=0"
                                     "&ep_end=1&id=5977&default_ep=0")


if __name__ == '__main__':
    unittest.main()
