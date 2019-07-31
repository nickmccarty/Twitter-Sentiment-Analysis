import pandas as pd
import numpy as np
import pickle
import sys
from sklearn.feature_extraction.text import TfidfVectorizer
import nltk
from nltk.stem.porter import *
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
lemmatizer = WordNetLemmatizer()
from bs4 import BeautifulSoup
import string
import re
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer as VS
from textstat.textstat import *
from sklearn.linear_model import LogisticRegression
from sklearn.feature_selection import SelectFromModel
from sklearn.metrics import classification_report
from sklearn.svm import LinearSVC
from sklearn.model_selection import GridSearchCV
# import matplotlib.pyplot as plt
# import seaborn
import joblib
# %matplotlib inline
#########################################################################
'''the model runs in appy.py. however the pkl files are loaded in model.py.the pickle idf & tfidf files
    use preprocess and tokenize in their vectorizers. those functions must be available to main.
    removing them from the main predict function, and importing those function into app.py prevents Error
    Attribute Error:module __main_ has no attribute 'preprocess' '''
#######################################################################
def preprocess(text_string):
    """
    Accepts a text string and replaces:
    1) urls with URLHERE
    2) lots of whitespace with one instance
    3) mentions with MENTIONHERE

    This allows us to get standardized counts of urls and mentions
    Without caring about specific people mentioned
    """
    space_pattern = '\s+'
    giant_url_regex = ('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|'
        '[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
    mention_regex = '@[\w\-\:]+'
    emoji_regex = '&#[0-9\;\:]+'
    parsed_text = re.sub(space_pattern, ' ', text_string)
    parsed_text = re.sub(giant_url_regex, '', parsed_text)
    parsed_text = re.sub(mention_regex, '', parsed_text)
    parsed_text = re.sub(emoji_regex,'',parsed_text)
    parsed_text = parsed_text.strip(string.punctuation)
    return parsed_text

def tokenize(tweet):

    tokens = []
    # remove non-alphabetic characters
    tweet_text = tweet_text = re.sub("[^a-zA-Z]"," ", str(tweet))
    #remove html content
    tweet_text = BeautifulSoup(tweet_text, features ='lxml').get_text()
    # tokenize
    words = word_tokenize(tweet_text.lower())
    # lemmatize each word to its lemma
    lemma_words = [lemmatizer.lemmatize(i) for i in words]
    tokens.append(lemma_words)
    return(tokens[0])

def logregress_linsvc(input):

    nltk.download('averaged_perceptron_tagger')
    nltk.download('punkt')
    nltk.download('wordnet')

    df = input

    print(df.describe())

    print(df.columns)

    base_tweets=df.tweet
    tweets = [x for x in base_tweets if type(x) == str]

    stopwords = nltk.corpus.stopwords.words("english")

    other_exclusions = ["#ff", "ff", "rt"]
    stopwords.extend(other_exclusions)

    # stemmer = PorterStemmer()

    #################################################################################################
    '''Preprocess tweets, tokenize, and gather feature,POS tags'''
    ################################################################################################






    def basic_tokenize(tweet):
        """Same as tokenize but without the stemming"""
        tweet = " ".join(re.split("[^a-zA-Z.,!?]*", tweet.lower())).strip()
        return tweet.split()

    sentiment_analyzer = VS()

    def count_twitter_objs(text_string):
        """
        Accepts a text string and replaces:
        1) urls with URLHERE
        2) lots of whitespace with one instance
        3) mentions with MENTIONHERE
        4) hashtags with HASHTAGHERE

        This allows us to get standardized counts of urls and mentions
        Without caring about specific people mentioned.

        Returns counts of urls, mentions, and hashtags.
        """
        space_pattern = '\s+'
        giant_url_regex = ('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|'
            '[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
        mention_regex = '@[\w\-]+'
        hashtag_regex = '#[\w\-]+'
        parsed_text = re.sub(space_pattern, ' ', text_string)
        parsed_text = re.sub(giant_url_regex, 'URLHERE', parsed_text)
        parsed_text = re.sub(mention_regex, 'MENTIONHERE', parsed_text)
        parsed_text = re.sub(hashtag_regex, 'HASHTAGHERE', parsed_text)
        return(parsed_text.count('URLHERE'),parsed_text.count('MENTIONHERE'),parsed_text.count('HASHTAGHERE'))

    def other_features(tweet):
        """This function takes a string and returns a list of features.
        These include Sentiment scores, Text and Readability scores,
        as well as Twitter specific features"""
        ##SENTIMENT
        sentiment = sentiment_analyzer.polarity_scores(tweet)

        words = preprocess(tweet) #Get text only

        syllables = textstat.syllable_count(words) #count syllables in words
        num_chars = sum(len(w) for w in words) #num chars in words
        num_chars_total = len(tweet)
        num_terms = len(tweet.split())
        num_words = len(words.split())
        avg_syl = round(float((syllables+0.001))/float(num_words+0.001),4)
        num_unique_terms = len(set(words.split()))

        ###Modified FK grade, where avg words per sentence is just num words/1
        FKRA = round(float(0.39 * float(num_words)/1.0) + float(11.8 * avg_syl) - 15.59,1)
        ##Modified FRE score, where sentence fixed to 1
        FRE = round(206.835 - 1.015*(float(num_words)/1.0) - (84.6*float(avg_syl)),2)

        twitter_objs = count_twitter_objs(tweet) #Count #, @, and http://
        features = [FKRA, FRE, syllables, avg_syl, num_chars, num_chars_total, num_terms, num_words,
                    num_unique_terms,sentiment['neu'], sentiment['compound'],
                    twitter_objs[2],twitter_objs[1],twitter_objs[0]]

        #features = pandas.DataFrame(features)
        return features

    def get_feature_array(tweets):
        feats=[]
        for t in tweets:
            feats.append(other_features(t))
        return np.array(feats)

    def get_pos_tags(tweets):
        """Takes a list of strings (tweets) and
        returns a list of strings of (POS tags).
        """
        tweet_tags = []
        for t in tweets:
            tokens = basic_tokenize(preprocess(t))
            tags = nltk.pos_tag(tokens)
            tag_list = [x[1] for x in tags]
            #for i in range(0, len(tokens)):
            tag_str = " ".join(tag_list)
            tweet_tags.append(tag_str)
        return tweet_tags

    ###########################################################################################
    '''Preprocess End'''
    ###########################################################################################


    import warnings

    import os
    warnings.simplefilter(action='ignore', category=FutureWarning)

    ########################
    '''Load pickled vectorizers'''
    #########################print (len(tweets), " tweets to classify")
    print ("Loading trained classifier... ")


    model = joblib.load('model_py3.pkl')

    print ("Loading other information...")
    ###############
    tf_vectorizer = joblib.load('true_tfidf_py3.pkl')
    #############

    idf_vector = joblib.load('idf_py3.pkl')

    #############

    pos_vectorizer = joblib.load('pos_vect_py3.pkl')

    #######################################################
    '''Construct tfidf matrix and get relevant scores'''
    #######################################################
    tf_array = tf_vectorizer.fit_transform(tweets).toarray()
    tfidf_array = tf_array*idf_vector
    print ("Built TF-IDF array")

    #################################################
    '''Construct POS TF matrix and get vocab dict'''
    #################################################
    pos_tags = get_pos_tags(tweets)
    pos_array = pos_vectorizer.fit_transform(pos_tags).toarray()
    print ("Built POS array")

    ###################################################
    ''' Get features'''
    ###################################################
    other_feats = get_feature_array(tweets)
    print ("Built other features array")

    #Now join them all up
    X = np.concatenate([tfidf_array,pos_array,other_feats],axis=1)

    print(X.shape)


    #####################################################
    '''Running the Model'''
    #####################################################
    print ("Running classification model...")
    y_preds = model.predict(X)

    print ("Loading data to classify...")

    def class_to_name(class_label):
        """
        This function can be used to map a numeric
        feature name to a particular class.
        """
        if class_label == 0:
            return "Hate speech"
        elif class_label == 1:
            return "Offensive language"
        elif class_label == 2:
            return "Neither"
        else:
            return "No label"
    hate = 0
    hurtful = 0
    neither = 0
    for x in y_preds:
       if str(x) == '0':
           hate +=1
       elif str(x) == '1':
           hurtful += 1
       elif str(x) == '2':
           neither += 1
    print ("Printing predicted values: ")

    print(f'Hateful tweets: {hate}; % of total: {hate/(hate+hurtful+neither)}')
    hate_results = f'Hateful tweets: {hate}; % of total: {hate/(hate+hurtful+neither)}'

    print(f'Hurtful tweets: {hurtful}; % of total: {hurtful/(hate+hurtful+neither)}')
    hurtful_results = f'Hurtful tweets: {hurtful}; % of total: {hurtful/(hate+hurtful+neither)}'

    print(f'Neither tweets: {neither}; % of total: {neither/(hate+hurtful+neither)}')
    neither_results = f'Neither tweets: {neither}; % of total: {neither/(hate+hurtful+neither)}'
    results = {'hate':hate_results,
                'hurtful':hurtful_results,
                'neither':neither_results}
    return results

def LSTM(input):
    return "no lstm model file yet"

# for i,t in enumerate(tweets):
#     print (t)
#     print (class_to_name(y_preds[i]))
