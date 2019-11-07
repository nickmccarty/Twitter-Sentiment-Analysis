# import os
from flask import Flask,request, jsonify,render_template
# from lstm import LSTM
import numpy as np
from keras.preprocessing import sequence
from keras.preprocessing.text import Tokenizer
import utils
from keras.models import load_model
import boto3
import os

application = Flask(__name__)


unique_words = 28701
len_max = 53
tokenizer = Tokenizer(num_words=unique_words)

def token_maker(cleaned1_tweets):
    # Tokenizer of keras and convert to sequences
    tokenizer.fit_on_texts(list(cleaned1_tweets))
    return tokenizer.texts_to_sequences(cleaned1_tweets)

# Load Model from S3 bucket
access_key = os.environ.get('S3_ACCESS_KEY')
secret_key = os.environ.get('S3_SECRET_KEY')
bucket_name ='retrained-models'
folder_name = 'lstm_models'
filename = "LSTM_model.h5"
s3_file_path= folder_name+'/'+filename


s3 = boto3.client('s3',aws_access_key_id=access_key,aws_secret_access_key=secret_key)
s3.download_file(bucket_name , s3_file_path, filename)



model = load_model(filename)
model._make_predict_function()
# mem.append(('model load',process.memory_info().rss))
# graph = tf.get_default_graph()


def LSTM(input):


    print('Cleaning tweets')
    print('Tokenizing tweets')
    print('Padding tweets')
    print('Loading the model')
    print('Deciding whats hate and what aint')
    # with graph.as_default():
    #     prediction_prob = model.predict(padded_tweets)
    # mem.append(('predict strt',process.memory_info().rss))

    prediction_prob = model.predict(sequence.pad_sequences(token_maker([utils.tokenize(x) for x in input['text']]), maxlen=len_max))
    # mem.append(('predict end',process.memory_info().rss))
    # print(mem)

    print('The Hate Decision has been made')

    hate = 0
    hurtful = 0
    neither = 0

    for x in prediction_prob:
       if (np.argmax(x)) == 0:
           hate +=1
       elif (np.argmax(x)) == 1:
           hurtful += 1
       elif (np.argmax(x)) == 2:
           neither += 1


    ##############################################################################################################
    '''New result format. Allows better parsing for possible db uploading. Prior format returned strings. '''
    ##############################################################################################################
    results = { 'api_code':200,
                'prediction_array': prediction_prob.tolist(),
                'hate_data':{'count':hate,
                            'percentTotal':int((hate/(hate+hurtful+neither))*100)},
                'hurt_data':{'count':hurtful,
                            'percentTotal':int((hurtful/(hate+hurtful+neither))*100)},
                'neither_data':{'count':neither,
                                'percentTotal':int((neither/(hate+hurtful+neither))*100)},
                'total_count':hate+hurtful+neither
                }


    return results






#####################################
# Create routes
#####################################


@application.route('/')
def index():
    '''Return the homepage'''
    return render_template('index.html')



@application.route('/receiver', methods=['POST'])
def model_serv():
    try:
        if request.method == 'POST':
            input = request.json
            print('***############# A snippet of the user input ##################*****')
            print(input['text'][:3])
            print('***############# END SNIPPET ##################*****')
            prediction = LSTM(input)
            return jsonify(prediction)
    except Exception as e:
        print(e)
        print('!!!!!!!!!!Try/Except fired - Return Error500 !!!!!!!')
        return jsonify('!!!Model Serv code error!!!!')

# Route for API/python library prediction/classificcation. POST only. Data sent should be a list of text strings to clasify.
@application.route('/api_receiver', methods=['POST'])
def api_model_serv():
    if request.method == 'POST':
        input = request.json
        # Check that data sent is a list.
        if isinstance(input,list):
            # Verify each item in list is a string.
            if all(isinstance(item,str) for item in input):
                # Create a dict with key text. Allows the API to use the same prediction function as the front-end.
                input = {'text':input}
                try:
                    print('***** API PREDICTION REQUEST *****')
                    print('***############# A snippet of the user input - API ##################*****')
                    print(input['text'][:3])
                    print('***############# END SNIPPET - API ##################*****')
                    prediction = LSTM(input)
                    return jsonify(prediction)
                except Exception as e:
                    print('!!!!!!!!!!Try/Except fired - API prediction failed: verbose: {} !!!!!!!'.format(e))
                    return jsonify({ 'api_code':500, 'message':'Model Server Error, Uncaught exception ,Sever Side: verbose: {}'.format(e) })
            else:
                print('!!!!!!! An item in iterable prediction input is not string type. - API prediction failed !!!!!!!')
                return jsonify({ 'api_code':500, 'message':"Model Server Error, TypeError: one or more items in prediction input not string type.Proper input ['text','text','text','text']" })
        else:
            print('!!!!!!!!!! Prediction input not a list - API prediction failed !!!!!!!')
            return jsonify({ 'api_code':500, 'message':"Model Server Error, TypeError: prediction input not a list. Proper input ['text','text','text','text']" })


if __name__ == "__main__":
    application.run()
