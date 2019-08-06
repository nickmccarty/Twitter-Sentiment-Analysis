
# import nltk
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
lemmatizer = WordNetLemmatizer()
from bs4 import BeautifulSoup
import string
import re

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
    tweet_text = BeautifulSoup(tweet_text, features="lxml").get_text()

    # tokenize
    words = word_tokenize(tweet_text.lower())

    # lemmatize each word to its lemma
    lemma_words = [lemmatizer.lemmatize(i) for i in words]

    #tokens.append(lemma_words)

    return(lemma_words)
