import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
import re
import nltk
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
lemmatizer = WordNetLemmatizer()
from keras.preprocessing import sequence
from keras.preprocessing.text import Tokenizer
from keras.models import load_model
from keras import backend as K


def LSTM(input):
    K.clear_session()

    ################# Formatting Functions #########################

    def clean_sentences(tweet_input):
    #tweet_input must be a list of tweets
        tweets = []
        for x in tweet_input:
            # remove non-alphabetic characters
            tweet_text = re.sub("[^a-zA-Z]"," ", str(x))
            #remove html content
            tweet_text = BeautifulSoup(tweet_text).get_text()
            # tokenize
            words = word_tokenize(tweet_text.lower())
            # lemmatize each word to its lemma
            lemma_words = [lemmatizer.lemmatize(i) for i in words]
            tweets.append(lemma_words)
        return(tweets)

    def token_maker(cleaned1_tweets):
        # Tokenizer of keras and convert to sequences
        tokenizer = Tokenizer(num_words=unique_words)
        tokenizer.fit_on_texts(list(cleaned1_tweets))
        return tokenizer.texts_to_sequences(cleaned1_tweets)

    def keras_output_sklearn(y):
        result = []
        for element in y:
            result.append(np.argmax(element))
        return result






    ################### Actually Running the Model #####################
    #Model Parameters
    unique_words = 28701
    len_max = 53

    #Transforming input into a list
    tweets = [x for x in input['text']]

    print('Cleaning tweets')
    cleaned1 = clean_sentences(tweets)

    print('Tokenizing tweets')
    tokened_tweets = token_maker(cleaned1)

    print('Padding tweets')
    padded_tweets = sequence.pad_sequences(tokened_tweets, maxlen=len_max)

    print('Loading the model')



    model = load_model('model_acc.h5')

    print('Deciding whats hate and what aint')
    prediction_prob = model.predict(padded_tweets)
    prediction = keras_output_sklearn(prediction_prob)

    print('The Hate Decition has been made')
    # return [prediction, prediction_prob]

    hate = 0
    hurtful = 0
    neither = 0

    for x in prediction:
       if str(x) == '0':
           hate +=1
       elif str(x) == '1':
           hurtful += 1
       elif str(x) == '2':
           neither += 1
    print ("Printing predicted values: ")

    print(f'Hateful tweets: {hate}; % of total: {hate/(hate+hurtful+neither)}')
    #hate_results = f'Hateful tweets: {hate}; % of total: {hate/(hate+hurtful+neither)}'

    print(f'Hurtful tweets: {hurtful}; % of total: {hurtful/(hate+hurtful+neither)}')
    #hurtful_results = f'Hurtful tweets: {hurtful}; % of total: {hurtful/(hate+hurtful+neither)}'

    print(f'Neither tweets: {neither}; % of total: {neither/(hate+hurtful+neither)}')
    #neither_results = f'Neither tweets: {neither}; % of total: {neither/(hate+hurtful+neither)}'
    # results = {'hate':hate_results,
    #             'hurtful':hurtful_results,
    #             'neither':neither_results} <<<<<old results format.
    ##############################################################################################################
    '''New result format. Allows better for parsing for possible db uploading. Prior format returned strings. '''
    ##############################################################################################################
    results = {
                'hate_data':{'count':hate,
                            'percentTotal':int((hate/(hate+hurtful+neither))*100)},
                'hurt_data':{'count':hurtful,
                            'percentTotal':int((hurtful/(hate+hurtful+neither))*100)},
                'neither_data':{'count':neither,
                                'percentTotal':int((neither/(hate+hurtful+neither))*100)},
                'total_count':hate+hurtful+neither
                }
    K.clear_session()
    return results
