import os

#import pandas as pd
import numpy as np
# import request
# from request import *
from flask import Flask, jsonify, render_template,request
import sqlite3
from sqlite3 import Error
import nltk
# import requests
import tweepy
import json
from query_functions import *
from model import * #model function goes Here
from lstm import *


app= Flask(__name__)
# consumer_key = os.environ.get('CONSUMER_KEY')
# consumer_secret = os.environ.get('CONSUMER_SECRET')
# access_token = os.environ.get('ACCESS_TOKEN')
# access_token_secret = os.environ.get('ACCESS_SECRET')
consumer_key = 'ccUDQyUZqI3ljuvSdpGwnEVtA'
consumer_secret = 'EnyT1YekZlwIw9drTanRlB3CEXHRnx7YJ1R578HXHH2fFi8nQi'
access_token = '1153798652290203651-zlVEr2pkOIoR5vccxYSROXrzD0PGsk'
access_token_secret = 'aEZ8f10oyknxpOvtog5D2icjgl3O6s61n5i5o2TavrAoP'

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
                user_tweets_dict = api_user(api,query)
                results= logregress_linsvc(user_tweets_dict)
                return render_template('results_tweets.html',
                query_type=query_type,query_input=query,
                count_items=results['total_count'],model_type=model_type,
                hate_count=results['hate_data']['count'],hate_percent=results['hate_data']['percentTotal'],
                hurt_count=results['hurt_data']['count'],hurt_percent=results['hurt_data']['percentTotal'],
                neither_count=results['neither_data']['count'],neither_percent=results['neither_data']['percentTotal'])

            elif model_type == 'LSTM':
                user_tweets_dict = api_user(api,query)
                results =LSTM(user_tweets_dict)
                return render_template('results_tweets.html',
                query_type=query_type,query_input=query,
                count_items=results['total_count'],model_type=model_type,
                hate_count=results['hate_data']['count'],hate_percent=results['hate_data']['percentTotal'],
                hurt_count=results['hurt_data']['count'],hurt_percent=results['hurt_data']['percentTotal'],
                neither_count=results['neither_data']['count'],neither_percent=results['neither_data']['percentTotal'])



            elif model_type == 'luck':
                results = "I'll finish by deadline.Swear"
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
                textinput_dict = text_transform(query)
                results = logregress_linsvc(textinput_dict)
                return render_template('results_text.html',
                query_type=query_type,text_snip=text_snip,
                count_items=results['total_count'],model_type=model_type,
                hate_count=results['hate_data']['count'],hate_percent=results['hate_data']['percentTotal'],
                hurt_count=results['hurt_data']['count'],hurt_percent=results['hurt_data']['percentTotal'],
                neither_count=results['neither_data']['count'],neither_percent=results['neither_data']['percentTotal'])

            elif model_type == 'LSTM':
                textinput_dict = text_transform(query)
                results =LSTM(textinput_dict)
                return render_template('results_text.html',
                query_type=query_type,text_snip=text_snip,
                count_items=results['total_count'],model_type=model_type,
                hate_count=results['hate_data']['count'],hate_percent=results['hate_data']['percentTotal'],
                hurt_count=results['hurt_data']['count'],hurt_percent=results['hurt_data']['percentTotal'],
                neither_count=results['neither_data']['count'],neither_percent=results['neither_data']['percentTotal'])


            elif model_type == 'luck':
                results = "Be better"

    return  render_template('index.html') #<<<<<<<<<<< this goes to JS file that build result on page.




if __name__ == "__main__":
    app.run()
