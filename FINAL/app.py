import os
from flask import Flask, render_template,request
import tweepy
#import query_functions as query_funct
#import pandas as pd
# import numpy as np
# import request
# from request import *

# import sqlite3
# from sqlite3 import Error
# import nltk
# import requests

# import json

 #model function goes Here


app= Flask(__name__)
consumer_key = 'ccUDQyUZqI3ljuvSdpGwnEVtA'
consumer_secret = 'EnyT1YekZlwIw9drTanRlB3CEXHRnx7YJ1R578HXHH2fFi8nQi'
access_token = '1153798652290203651-zlVEr2pkOIoR5vccxYSROXrzD0PGsk'
access_token_secret = 'aEZ8f10oyknxpOvtog5D2icjgl3O6s61n5i5o2TavrAoP'



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


#####################################
# Create routes
#####################################


@app.route('/')
def index():
    '''Return the homepage'''
    return render_template('index.html')

@app.route('/aboutus')
def aboutus():
    '''Return about us'''
    return render_template('aboutus.html')

@app.route('/models')
def models():
    '''Return tech_section on models'''
    return render_template('models.html')

@app.route('/contact')
def contact():
    '''Return contact page'''
    return render_template('contact.html')

# @app.route('/test')
# def test():
#     test_string =" Hi my name is omari B. 120-1###"
#     topic_tweets_df = text_transform(test_string)
#     p = m.logregress_linsvc(topic_tweets_df)
#     return jsonify(p)

###################################################################################
''' /predict route takes a form submission.
 makes predictions based on form imputs for query input, query type,model type.'''
 ##################################################################################
@app.route('/predict',methods = ['POST'])
def predict():
    if request.method == 'POST':
        global api
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)
        api = tweepy.API(auth, wait_on_rate_limit=True)

        form_input = request.form.to_dict()
        print(form_input)
        query = form_input['query_input']
        query_type =form_input['query_type']
        model_type = form_input['model_type']
        ####################################################################
        '''Structure query and modeling process based on form inpuforts
         Render results page based on form inputs
        Args for render template (html_reference)=(python_data_from_model)'''
        ####################################################################
        if query_type == 'topic':
            ############################################ topic query
            if model_type == 'LogRegress-Linsvc':
                from model import logregress_linsvc
                topic_tweets_dict = api_topic(api,query)
                # print('sample text from query: ')
                # print(topic_tweets_dict['text'][0])
                results= logregress_linsvc(topic_tweets_dict)
                return render_template('results_tweets.html',
                query_type=query_type,query_input=query,
                count_items=results['total_count'],model_type=model_type,
                hate_count=results['hate_data']['count'],hate_percent=results['hate_data']['percentTotal'],
                hurt_count=results['hurt_data']['count'],hurt_percent=results['hurt_data']['percentTotal'],
                neither_count=results['neither_data']['count'],neither_percent=results['neither_data']['percentTotal'])

            elif model_type == 'LSTM':
                from lstm import LSTM
                topic_tweets_dict = api_topic(api,query)
                results =LSTM(topic_tweets_dict)
                return render_template('results_tweets.html',
                query_type=query_type,query_input=query,
                count_items=results['total_count'],model_type=model_type,
                hate_count=results['hate_data']['count'],hate_percent=results['hate_data']['percentTotal'],
                hurt_count=results['hurt_data']['count'],hurt_percent=results['hurt_data']['percentTotal'],
                neither_count=results['neither_data']['count'],neither_percent=results['neither_data']['percentTotal'])

            elif model_type == 'luck':
                results = "I'll finish by deadline.Swear"


        ################### Query for user posts from single user's timeline
        elif query_type == 'user':
            if model_type == 'LogRegress-Linsvc':
                from model import logregress_linsvc
                user_tweets_dict = api_user(api,query)
                results= logregress_linsvc(user_tweets_dict)
                return render_template('results_tweets.html',
                query_type=query_type,query_input=query,
                count_items=results['total_count'],model_type=model_type,
                hate_count=results['hate_data']['count'],hate_percent=results['hate_data']['percentTotal'],
                hurt_count=results['hurt_data']['count'],hurt_percent=results['hurt_data']['percentTotal'],
                neither_count=results['neither_data']['count'],neither_percent=results['neither_data']['percentTotal'])

            elif model_type == 'LSTM':
                from lstm import LSTM
                user_tweets_dict = api_user(api,query)
                results =LSTM(user_tweets_dict)
                return render_template('results_tweets.html',
                query_type=query_type,query_input=query,
                count_items=results['total_count'],model_type=model_type,
                hate_count=results['hate_data']['count'],hate_percent=results['hate_data']['percentTotal'],
                hurt_count=results['hurt_data']['count'],hurt_percent=results['hurt_data']['percentTotal'],
                neither_count=results['neither_data']['count'],neither_percent=results['neither_data']['percentTotal'])




        ################################################### text input query
        elif query_type == "text":
            # Hide user input and reduce text lenght when displayed in results.
            # If text < 500 characters, show half of text inputs.
            # if text input  > 500 characters, truncate it and show max 500 characters.
            char_count = len(query)
            if char_count > 500:
                text_snip = query[:500]
            else:
                text_snip = query[:int(len(query)/2)]

            ####################################
            if model_type == 'LogRegress-Linsvc':
                from model import logregress_linsvc
                textinput_dict = text_transform(query)
                results = logregress_linsvc(textinput_dict)
                return render_template('results_text.html',
                query_type=query_type,text_snip=text_snip,
                count_items=results['total_count'],model_type=model_type,
                hate_count=results['hate_data']['count'],hate_percent=results['hate_data']['percentTotal'],
                hurt_count=results['hurt_data']['count'],hurt_percent=results['hurt_data']['percentTotal'],
                neither_count=results['neither_data']['count'],neither_percent=results['neither_data']['percentTotal'])

            elif model_type == 'LSTM':
                from lstm import LSTM
                textinput_dict = text_transform(query)
                results =LSTM(textinput_dict)
                return render_template('results_text.html',
                query_type=query_type,text_snip=text_snip,
                count_items=results['total_count'],model_type=model_type,
                hate_count=results['hate_data']['count'],hate_percent=results['hate_data']['percentTotal'],
                hurt_count=results['hurt_data']['count'],hurt_percent=results['hurt_data']['percentTotal'],
                neither_count=results['neither_data']['count'],neither_percent=results['neither_data']['percentTotal'])




    return  render_template('index.html') #<<<<<<<<<<< this goes to JS file that build result on page.




if __name__ == "__main__":
    app.run()
