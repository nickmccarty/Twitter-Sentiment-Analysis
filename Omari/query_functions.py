import requests
import tweepy
import json
import pandas as pd

'''
############## CHANGE ITEM COUNT IN FINAL VERSION
'''
#######################################################################
'''Query for pulling tweets containing a keyword'''
def api_topic(api,topic):
    tweet_dict = {'dates':[],'text':[]}
    for tweet in tweepy.Cursor(api.search,q=topic, tweet_mode='extended',lang="en",since="2018-07-21").items(10):
        tweet_dict['dates'].append(tweet.created_at)
        tweet_dict['text'].append(tweet.full_text)

    return tweet_dict
#######################################################################
'''Query for pulling tweets only from a single useer timelime specified as the input, when form choice is 'user' '''
def api_user(api,user):
    user_posts = {'dates':[],'text':[]}
    for post in tweepy.Cursor(api.user_timeline, id=user, tweet_mode='extended',lang="en").items(10):
        user_posts['dates'].append(post.created_at)
        user_posts['text'].append(post.full_text)
    return user_posts

##########################################################################
'''Transform user input into a array for use in prediction function '''
def text_transform(textinput):
    #sentence_array = textinput.split('.')
    dict_to_df = {'text':[textinput]}
    return dict_to_df
