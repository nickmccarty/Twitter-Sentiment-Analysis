import os

import pandas as pd
import numpy as np
# import request
# from request import *
from flask import Flask, jsonify, render_template,request
import sqlite3
from sqlite3 import Error
# import requests
import tweepy
import json
from query_functions import api_topic,text_transform
from model import * #model function goes Here
from utils import tokenize,preprocess

app= Flask(__name__)

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

######## /prectic route takes a form submission. makes predictions based on form imputs for query input, query type,model type.
@app.route('/predict',methods = ['POST'])
def predict():
    if request.method == 'POST':
        consumer_key = "4yLfbC723iTMdpVuMG4sUIbgy"
        consumer_secret = "WbztNPnzgWJNRpvwSuC6ViDyXNDwtjfKsSl5d6hBhbc1FDPE1t"
        access_token = "955855581360910337-NxKQ23Q033lhuemZlFGyFUb5TaoiYqr"
        access_token_secret = "qlqToJDCA9KgAHvuE8AnszPKf23MowZAHUk7xs0tVeBMQ"
        global api
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)
        api = tweepy.API(auth, wait_on_rate_limit=True)

        form_input = request.form.to_dict()
        print(form_input)
        query = form_input['query_input']
        query_type =form_input['query_type']
        model_type = form_input['model_type']
        if query_type == 'topic':
            ####### topic query
            if model_type == 'loglinsvc':
                topic_tweets_df = api_topic(api,query)
                results =logregress_linsvc(topic_tweets_df)
            elif model_type == 'lstm':
                topic_tweets_df = api_topic(api,query)
                results =LSTM(topic_tweets_df)
            elif model_type == 'luck':
                results = "I'll finish by deadline.Swear"
        ############### text input query
        elif query_type == "text":
            if model_type == 'loglinsvc':
                textinput_df = text_transform(query)
                results = logregress_linsvc(textinput_df)
            elif model_type == 'lstm':
                textinput_df = text_transform(query)
                results =LSTM(textinput_df)
            elif model_type == 'luck':
                results = "Be a better"

        # else if query_type == 'user':
        #     if model_type == 'loglinsvc':
        #         user_tweets_df = userapicall_funct(query)
        #         results = logregress_linsvc(user_tweets_df)
        #     else:
        #         user_tweets_df = userapicall_funct(query)
        #         results =LSTM(user_tweets_df)
        # print("Flask print of results: ", results)
    # predictions = modelfunction(tweet_df) <<<<<<< call prediction function on the api results
    return  jsonify(results)#<<<<<<<<<<< this goes to JS file that build result on page.




if __name__ == "__main__":
    app.run()
