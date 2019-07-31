import pickle
import numpy as np
import pandas as pd
from sklearn.externals import joblib
from sklearn.svm import LinearSVC
from sklearn.linear_model import LogisticRegression
from sklearn.feature_selection import SelectFromModel
from sklearn.feature_extraction.text import TfidfVectorizer
import nltk
from nltk.stem.porter import *
import string
import re
import tweepy

from bs4 import BeautifulSoup
from nltk.tokenize import sent_tokenize, word_tokenize

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer as VS
from textstat.textstat import *

nltk.download("stopwords")


stopwords=stopwords = nltk.corpus.stopwords.words("english")

other_exclusions = ["#ff", "ff", "rt"]
stopwords.extend(other_exclusions)

sentiment_analyzer = VS()
stemmer = PorterStemmer()


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
    mention_regex = '@[\w\-\:]+' #<<<<<<added the semicolon after the + to remove : at end of Rt's
    emoji_regex = '&#[0-9\;\:]+'    #<<<<<<<<<remove emoji's .ex; &#1214324
    parsed_text = re.sub(space_pattern, ' ', text_string)
    parsed_text = re.sub(giant_url_regex, '', parsed_text)
    parsed_text = re.sub(mention_regex, '', parsed_text)
    parsed_text = re.sub(emoji_regex,'',parsed_text)
    parsed_text = parsed_text.strip(string.punctuation)
    return parsed_text


def tokenize(tweet):
    """Removes punctuation & excess whitespace, sets to lowercase,
    and stems tweets. Returns a list of stemmed tokens."""
    tweet = " ".join(re.split('\s|(?<!\d)[,.]|[,.](?!\d)', tweet.lower())).strip()
    tokens = [stemmer.stem(t) for t in tweet.split()]
    return tokens


def basic_tokenize(tweet):
    """Same as tokenize but without the stemming"""
    tweet = " ".join(re.split("[^a-zA-Z.,!?]*", tweet.lower())).strip()
    return tweet.split()


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


def other_features_(tweet):
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
    features = [FKRA,
                FRE,
                syllables,
                avg_syl,
                num_chars,
                num_chars_total,
                num_terms,
                num_words,
                num_unique_terms,
                sentiment['neu'],
                sentiment['compound'],
                twitter_objs[2],
                twitter_objs[1],
                twitter_objs[0]]

    #features = pandas.DataFrame(features)
    
    return features


def get_oth_features(tweets):
    """Takes a list of tweets, generates features for
    each tweet, and returns a numpy array of tweet x features"""
    feats=[]
    for t in tweets:
        feats.append(other_features_(t))
    return np.array(feats)


def transform_inputs(tweets, tf_vectorizer, idf_vector, pos_vectorizer):
    """
    This function takes a list of tweets, along with used to
    transform the tweets into the format accepted by the model.

    Each tweet is decomposed into
    (a) An array of TF-IDF scores for a set of n-grams in the tweet.
    (b) An array of POS tag sequences in the tweet.
    (c) An array of features including sentiment, vocab, and readability.

    Returns a pandas dataframe where each row is the set of features
    for a tweet. The features are a subset selected using a Logistic
    Regression with L1-regularization on the training data.

    """
    tf_array = tf_vectorizer.fit_transform(tweets).toarray()
    tfidf_array = tf_array*idf_vector
    print("Built TF-IDF array")

    pos_tags = get_pos_tags(tweets)
    pos_array = pos_vectorizer.fit_transform(pos_tags).toarray()
    print("Built POS array")

    oth_array = get_oth_features(tweets)
    print("Built other feature array")

    M = np.concatenate([tfidf_array, pos_array, oth_array],axis=1)
    return pd.DataFrame(M)


def predictions(X, model):
    """
    This function calls the predict function on
    the trained model to generated a predicted y
    value for each observation.
    """
    print(X.shape)
    y_preds = model.predict(X)
    return y_preds


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


def get_tweets_predictions(tweets, perform_prints=True):
    fixed_tweets = []
    for i, t_orig in enumerate(tweets):
        s = t_orig
        try:
            s = s.encode("latin1")
        except:
            try:
                s = s.encode("utf-8")
            except:
                pass
        if type(s) != str:
            fixed_tweets.append(str(s, errors="ignore"))
        else:
            fixed_tweets.append(s)
    assert len(tweets) == len(fixed_tweets), "shouldn't remove any tweets"
    tweets = fixed_tweets
    print(len(tweets), " tweets to classify")

    print("Loading trained classifier... ")





    model = joblib.load('py3models/final_mdl2.pkl')

    print("Loading other information...")

    tf_vectorizer = joblib.load('py3models/final_tfidf2.pkl')
    idf_vector = joblib.load('py3models/final_idf2.pkl')
    pos_vectorizer = joblib.load('py3models/final_pos2.pkl')
    
    
    #Load ngram dict
    #Load pos dictionary
    #Load function to transform data

    print("Transforming inputs...")
    X = transform_inputs(tweets, tf_vectorizer, idf_vector, pos_vectorizer)

    print("Running classification model...")
    predicted_class = predictions(X, model)

    return predicted_class


def pull_tweets(search_term):
    api_key = "ccUDQyUZqI3ljuvSdpGwnEVtA"
    api_secret = "EnyT1YekZlwIw9drTanRlB3CEXHRnx7YJ1R578HXHH2fFi8nQi"
    access_token = "1153798652290203651-zlVEr2pkOIoR5vccxYSROXrzD0PGsk"
    access_token_secret = "aEZ8f10oyknxpOvtog5D2icjgl3O6s61n5i5o2TavrAoP"

    auth = tweepy.OAuthHandler(api_key, api_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth, wait_on_rate_limit=True)
    tweet_list = []
    date_list = []
    print(f'pulling tweets related to {search term}')
    for tweet in tweepy.Cursor(api.search,q=search_term,tweet_mode='extended',lang="en",since="2018-07-21").items(1000):
        if (not tweet.retweeted) and ('RT @' not in tweet.full_text):
            tweet_list.append(tweet.full_text)
            date_list.append(tweet.created_at)

    return {'dates': date_list, 'tweets': tweet_list}

## This is the section that runs


search_term = 'trump'
tweets_pulled = pull_tweets(search_term)
tweet_predictions = get_tweets_predictions(tweets_pulled['tweets'])


# df = pd.read_csv('data/trump_tweets2.csv')
# trump_tweets = df.Text
# trump_tweets = [x for x in trump_tweets if type(x) == str]
# trump_predictions = get_tweets_predictions(trump_tweets)


hate = 0
hurtful = 0
neither = 0

for x in tweet_predictions:
    if str(x) == '0':
        hate +=1
    elif str(x) == '1':
        hurtful += 1
    elif str(x) == '2':
        neither += 1


print(f'Hateful tweets: {hate}; % of total: {hate/(hate+hurtful+neither)}')
print(f'Hurtful tweets: {hurtful}; % of total: {hurtful/(hate+hurtful+neither)}')
print(f'Neither tweets: {neither}; % of total: {neither/(hate+hurtful+neither)}')


# df2 = pd.read_csv('data/tweets.csv')
# tweets2 = df2.Text
# tweets2 = [x for x in tweets2 if type(x) == str]
# tweets2_predictions = get_tweets_predictions(tweets2)


# hate2 = 0
# hurtful2 = 0
# neither2 = 0

# for x in tweets2_predictions:
#     if str(x) == '0':
#         hate2 +=1
#     elif str(x) == '1':
#         hurtful2 += 1
#     elif str(x) == '2':
#         neither2 += 1
        
        
        
# print(f'Hateful tweets 2: {hate2}; % of total: {hate2/(hate2+hurtful2+neither2)}')
# print(f'Hurtful tweets 2: {hurtful2}; % of total: {hurtful2/(hate2+hurtful2+neither2)}')
# print(f'Neither tweets 2: {neither2}; % of total: {neither2/(hate2+hurtful2+neither2)}')


