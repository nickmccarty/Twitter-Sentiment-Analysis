import requests
import tweepy
import json
import pandas as pd



def api_topic(api,topic):
    tweets = tweepy.Cursor(api.search,q="topic",
                           lang="en",
                           since="2018-07-21").items(10)

    tweet_dict = {'dates':[],'tweet':[]}
    for t in tweets:
        tweet_dict['dates'].append(t.created_at)
        tweet_dict['tweet'].append(t.text)
    return pd.DataFrame(tweet_dict)

def text_transform(textinput):
    dict_to_df = {'text':textinput}
    return pd.DataFrame(dict_to_df)
