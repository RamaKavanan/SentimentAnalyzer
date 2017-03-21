"""
This class provide the wrapper around tweepy to access twitter data

@author Ideas2it
"""

import tweepy

class TwitterApi(object):

    def __init__(self, auth = None, twitter_api = None):
        self._auth = auth
        self._twitter_api = twitter_api

    def authenticate(self, api_token, api_secret, customer_key, customer_secret):
        try:
            self._auth = tweepy.OAuthHandler(customer_key, customer_secret)
            self._auth.set_access_token(api_token, api_secret)
        except Exception as ex:
            print(ex)
            self._auth = None

    def twitter_api(self):
        if self._auth == None :
            raise  Exception('Authentication Object was null')
        self._twitter_api = tweepy.API(self._auth)

    def search(self, search_term, count):
        if search_term == None and self._twitter_api == None:
            raise Exception('Twitter API / Search term should not be empty')
        return self._twitter_api.search(q=search_term, count=count)

    def get_home_timeline(self, count):
        if self._twitter_api == None:
            raise Exception('Twitter API should not be empty')
        return tweepy.Cursor(self._twitter_api.home_timeline).items(count)