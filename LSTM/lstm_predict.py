import os
import numpy as np 
import pandas as pd 
import seaborn

import warnings
warnings.filterwarnings("ignore", category=UserWarning, module='bs4')

# The Natural Language Toolkit, or more commonly NLTK, is a suite of libraries and programs for symbolic and 
# statistical natural language processing for English written in the Python programming language.
import nltk
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
lemmatizer = WordNetLemmatizer()
from bs4 import BeautifulSoup
import re

#TQDM is a progress bar library with good support for nested loops and Jupyter/IPython notebooks.
from tqdm import tqdm

# Use Keras Tensorflow deeplearning library
from keras.utils import to_categorical
import random
from tensorflow import set_random_seed
from sklearn.model_selection import train_test_split
from keras.preprocessing import sequence
from keras.preprocessing.text import Tokenizer
from keras.layers import Dense,Dropout,Embedding,LSTM
from keras.callbacks import EarlyStopping
from keras.losses import categorical_crossentropy
from keras.optimizers import Adam
from keras.models import Sequential

#set random seed for the session and also for tensorflow that runs in background for keras
set_random_seed(123)
random.seed(123)

import matplotlib.pyplot as plt
import seaborn as sns

from sklearn import preprocessing
from sklearn.preprocessing import LabelEncoder, OneHotEncoder
from sklearn.model_selection import train_test_split,GridSearchCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.tree import export_graphviz
from matplotlib.pylab import rcParams

from sklearn.metrics import roc_curve,auc,make_scorer, accuracy_score
from sklearn.metrics import classification_report
from sklearn.metrics import confusion_matrix

import eli5 # for permutation importance
from eli5.sklearn import PermutationImportance

import shap # for SHAP value
from pdpbox import pdp, info_plots # flor partial plots 

np.random.seed(123)
pd.options.mode.chained_assignment = None  #hide any pandas warnings


# Load Dataset
test = pd.read_csv("../LSTM/input/test.csv")

#print(test.head())

# Test dataset: Need only text as 'Phrase'
test = test.rename(columns={'Text':'Phrase'})
test = test.drop(['Date', 'Favorites', 'Retweets', 'Tweet ID'],axis=1).copy()
#print(test.head())


def clean_sentences(df):
    tweets = []
    
    for sent in tqdm(df['Phrase']):
        
        # remove non-alphabetic characters
        tweet_text = re.sub("[^a-zA-Z]"," ", str(sent))
        
        #remove html content
        tweet_text = BeautifulSoup(tweet_text).get_text()
        
        # tokenize
        words = word_tokenize(tweet_text.lower())
        
        # lemmatize each word to its lemma
        lemma_words = [lemmatizer.lemmatize(i) for i in words]
        
        tweets.append(lemma_words)
        
    return(tweets)

test_sentences = clean_sentences(test)

# Getting the no of unique words and max length of a tweet available in the list of cleaned tweets
# It is needed for initializing tokenizer of keras and subsequent padding

# Build an unordered collection of unique elements.

#based on train data
unique_words = 28701
len_max = 53

# for sent in tqdm(test_sentences):
    
#     unique_words.update(sent)
    
#     if(len_max<len(sent)):
#         len_max=len(sent)

tokenizer = Tokenizer(unique_words)
tokenizer.fit_on_texts(list(test_sentences))

X_test = tokenizer.texts_to_sequences(test_sentences)
X_test = sequence.pad_sequences(X_test, maxlen=len_max)


#print(X_test.shape)


# to load it again
from keras.models import load_model
model = load_model('lstm_model.h5',compile=False)

# # save as JSON
# json_string = model.to_json()

# # save as YAML
# yaml_string = model.to_yaml()

# # model reconstruction from JSON:
# from keras.models import model_from_json
# model = model_from_json(json_string)

# # model reconstruction from YAML:
# from keras.models import model_from_yaml
# model = model_from_yaml(yaml_string)

# RUN MODEL on TEST DATA!
predicted_output = model.predict(X_test, batch_size=256)

# covert keras arrays
def keras_output_sklearn(y):
    
    result = []
    
    for element in y:
        result.append(np.argmax(element))
        

    return result

# create pandas df with predictions 
df_test_predict = pd.DataFrame(keras_output_sklearn(predicted_output))

# rename column
df_test_predict.rename(columns={df_test_predict.columns[0]: "result" }, inplace = True)

# replace sentiment values
df_test_predict = df_test_predict.replace({0:'hate',1:'offensive',2:'neutral'})

# normalize to percentages
norm = pd.DataFrame(df_test_predict['result'].value_counts(normalize=True)*100)

# print results
print(f"hate prediction: {norm.loc['hate','result']}")
print(f"offensive prediction: {norm.loc['offensive','result']}")
print(f"neutral prediction: {norm.loc['neutral','result']}")