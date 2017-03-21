"""
This class provide to ananlysis the setiment from the twitter

@author Ideas2it
"""

import json
from pycorenlp import StanfordCoreNLP
from  TwitterApi import TwitterApi
import time
import pandas as pd
import re
import chardet
from DBConnector import DBConnector
from DBManipulation import  DBManipulation
import matplotlib.pyplot as plt
import numpy as np

class SentenceAnalyzer(object):

    CONSUMER_KEY = "cFnNRscFfGxq4FmghZz5LHbJ6"

    CONSUMER_SECRET = "uVz70SBDcHSWO6Z0b6W1D0cndpCl2HTexI8gzRDYMkfc4trLMj"

    ACCESS_TOKEN = "481384592-xaiSfZLeid86pkg4jk6VFN43KYNlyovWQfIwWwUd"

    ACCESS_SECRET = "P3VXNASEoQe1q4LmROOw5AAmXEpw8cOt9Nzzc1nrEaEti"

    CREATE_TABLE_QUERY = "CREATE TABLE sentiment_analysis(   ID INTEGER PRIMARY KEY   AUTOINCREMENT,   sentence  TEXT, sentimentValue INTEGER , sentiment TEXT )"

    INSERT_QUERY = "INSERT INTO sentiment_analysis (sentence,sentimentValue, sentiment) VALUES(?,?,?)"

    SELECT_ALL_QUERY ="SELECT * FROM sentiment_analysis"

    def __init__(self, server_host):
        if server_host == None :
            raise Exception('Stanford server not running .... ')
        self.nlp = StanfordCoreNLP(server_host)

    def analysis(self, is_table_exist, is_pandas_enabled, is_tweet_need):
        try:
            if is_tweet_need :
                tweets = self.get_tweets();
                if tweets == None:
                    raise Exception('Exception while fetching twitter data')
                if is_table_exist == False:
                    self.create_table(self.CREATE_TABLE_QUERY)

                list_data = []
                for tweet in tweets :
                    txt = self.clean_tweet(tweet.text)
                    tweet_txt = self.convert_str_utf8(txt)
                    resp = self.sentiment_analyzer(tweet_txt)
                    if resp != None :
                        for sentence in resp["sentences"]:
                            data = (str(" ".join([t["word"] for t in sentence["tokens"]])),sentence["sentimentValue"],str(sentence["sentiment"]) )
                            list_data.append(data)
                if list_data :
                    self.insert_mass_data(self.INSERT_QUERY, list_data)
            if is_pandas_enabled :
                self.pandas_analysis()
        except Exception as ex:
            print(str(ex))
            raise ex

    def create_table(self, tableString):
        connector = DBConnector('', "SentenceAnalyzer.db")
        conn = connector.create_schema()
        db_cmt = DBManipulation(conn)
        db_cmt.create_table(tableString)

    def get_all_data(self):
        connector = DBConnector('', "SentenceAnalyzer.db")
        conn = connector.create_schema()
        db_cmt = DBManipulation(conn)
        return db_cmt.select_all_data(self.SELECT_ALL_QUERY)

    def insert_mass_data(self, query, query_data):
        """ Make call to insert bulk data"""

        connector = DBConnector('', "SentenceAnalyzer.db")
        conn = connector.create_schema()
        db_cmt = DBManipulation(conn)
        db_cmt.many_insert_query_executor(query, query_data)

    def get_tweets(self):
        try:
            twitter = TwitterApi()
            twitter.authenticate(self.ACCESS_TOKEN, self.ACCESS_SECRET,
                                 self.CONSUMER_KEY, self.CONSUMER_SECRET)
            twitter.twitter_api()
            tweets = twitter.search('World Cup', 5)
            return tweets
        except Exception as ex:
            return None;

    def clean_tweet(self, tweet):
        return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t]) | (\w +:\ / \ / \S +)", " ", tweet).split())

    def convert_str_utf8(self, txt):
        if txt == None or txt == '':
            return None
        try:
            #tweet_txt = txt.decode('unicode_escape').encode('ascii','ignore')
            tweet_txt = txt.encode('ascii', 'ignore')
            return tweet_txt
        except Exception as ex:
            return None

    def sentiment_analyzer(self, tweet):
        if isinstance(tweet, str) and tweet != None :
            resp = self.nlp.annotate(tweet, properties={
                'annotators': 'sentiment',
                'outputFormat': 'json',
                'timeout': 1000,
            })
            return resp
        else:
            return None

    def pandas_analysis(self):
        connector = DBConnector('', "SentenceAnalyzer.db")
        conn = connector.create_schema()
        if conn != None :
            df = pd.io.sql.read_sql(self.SELECT_ALL_QUERY, conn)
            plt.scatter(x=df['ID'], y=df['sentimentValue'])
            #print df
            #df.plot()
            #df.groupby(['sentiment'])
            #sentiment_sum = df.pivot_table('sentimentValue', rows='sentiment', aggfunc='sum')
            #plt.figure()
            #sentiment_sum.plot(kind='barh', stacked=True, title="Sum of Sentiment value")
            #plt.figure()
            #sentiment_count = df.pivot_table('sentimentValue', rows='sentiment', aggfunc='count')
            #sentiment_count.plot(kind='barh', title="Count of Sentiment in sentence")
            plt.show()
        else :
            raise Exception("The data cant retrieved from SQLITE")

if __name__ == "__main__" :
    analyzer = SentenceAnalyzer('http://localhost:9000')
    analyzer.analysis(True, True, False)