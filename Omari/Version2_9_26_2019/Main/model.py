import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
import nltk
import re
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer as VS
from textstat.textstat import *
from utils import preprocess
import joblib
import warnings

########################
'''Load pickled vectorizers'''
#########################print (len(tweets), " tweets to classify")
print ("Loading trained classifier... ")
model = joblib.load('true_model_py3.pkl')

print ("Loading other information...")
###############
tf_vectorizer = joblib.load('actual_tfidf_py3.pkl')
#############
idf_vector = joblib.load('actual_idf_py3.pkl')
#############
pos_vectorizer = joblib.load('actual_pos_vect_py3.pkl')


#########################################################################
#   the model runs in appy.py. however the pkl files are loaded in model.py.the pickle idf & tfidf files
#    use preprocess and tokenize in their vectorizers. those functions are stored in utils.py.
# an __init__.py file ,and import of utils into models.py is necessasry to avoid addtribute error '''
#######################################################################

#################################################################################################
# Preprocess tweets, tokenize, and gather feature,POS tags'''
################################################################################################

stopwords = nltk.corpus.stopwords.words("english")

other_exclusions = ["#ff", "ff", "rt"]
stopwords.extend(other_exclusions)

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
# Preprocess End'''
###########################################################################################
#######################################################
'''Construct tfidf matrix and get relevant scores'''
#######################################################
def tfidf_matrix(input):
    tf_array = tf_vectorizer.fit_transform(input['text']).toarray()
    tfidf_array = tf_array*idf_vector
    print ("Built TF-IDF array")
    return tfidf_array

#################################################
'''Construct POS TF matrix and get vocab dict'''
#################################################
def pos_matrix(input):

    pos_tags = get_pos_tags(input['text'])
    pos_array = pos_vectorizer.fit_transform(pos_tags).toarray()
    print ("Built POS array")
    return pos_array

    ###################################################
    ''' Get features'''
    ###################################################
def otherfeat_matrix(input):
    other_feats = get_feature_array(input['text'])
    print ("Built other features array")
    return other_feats

###########################################################################
# predict
########################################################################3

def logregress_linsvc(input):

    warnings.simplefilter(action='ignore', category=FutureWarning)

    tfidf_array = tfidf_matrix(input)
    pos_array = pos_matrix(input)
    other_feats = otherfeat_matrix(input)

    #Now join them all up
    X = np.concatenate([tfidf_array,pos_array,other_feats],axis=1)
    # print(X.shape)

    #####################################################
    '''Running the Model'''
    #####################################################
    print ("Running classification model...")
    y_preds = model.predict(X)

    print ("Loading data to classify...")

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


    results = { 'prediction_array': y_preds,
                'hate_data':{'count':hate,
                            'percentTotal':int((hate/(hate+hurtful+neither))*100)},
                'hurt_data':{'count':hurtful,
                            'percentTotal':int((hurtful/(hate+hurtful+neither))*100)},
                'neither_data':{'count':neither,
                                'percentTotal':int((neither/(hate+hurtful+neither))*100)},
                'total_count':hate+hurtful+neither
                }
    print(results)
    return results
