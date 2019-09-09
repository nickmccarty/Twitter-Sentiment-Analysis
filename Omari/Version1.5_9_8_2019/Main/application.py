import os
from flask import Flask,render_template,redirect,request,jsonify,url_for
import tweepy
from model import logregress_linsvc
import requests
import json
import datetime
import time
import numpy as np
import mysql.connector
from mysql.connector import Error,errorcode





application= Flask(__name__)

###############################
#Configure Tweepy'''
#############################
consumer_key = os.environ.get('CONSUMER_KEY')
consumer_secret = os.environ.get('CONSUMER_SECRET')
access_token = os.environ.get('ACCESS_TOKEN')
access_token_secret = os.environ.get('ACCESS_SECRET')



consumer_key2 = os.environ.get('CONSUMER_KEY2')
consumer_secret2 = os.environ.get('CONSUMER_SECRET2')
access_token2 = os.environ.get('ACCESS_TOKEN2')
access_token_secret2 = os.environ.get('ACCESS_SECRET2')

oauth_keys = [
            [consumer_key,consumer_secret,access_token,access_token_secret],
            [consumer_key2,consumer_secret2,access_token2,access_token_secret2]
        ]

auths = []
for consumer_key,consumer_secret,access_token,access_token_secret in oauth_keys:
    auth = tweepy.OAuthHandler(consumer_key,consumer_secret)
    auth.set_access_token(access_token,access_token_secret)
    auths.append(auth)


global api
api = tweepy.API(auths, monitor_rate_limit=True, wait_on_rate_limit=True)


########################################################################

#Setup tweepy api call functions
############### CHANGE ITEM COUNT IN FINAL VERSION

#######################################################################
#Query for pulling tweets containing a keyword'''
def api_topic(api,topic):
    tweet_dict = {'dates':[],'text':[]}
    for tweet in tweepy.Cursor(api.search,q=topic, tweet_mode='extended',lang="en").items(300):
        if 'RT @' not in tweet.full_text:
            tweet_dict['dates'].append((tweet.created_at).strftime('%m-%d-%Y'))
            tweet_dict['text'].append(tweet.full_text)

    return tweet_dict
#######################################################################
#Query for pulling tweets only from a single useer timelime specified as the input, when form choice is 'user' '''
def api_user(api,user):
    user_posts = {'dates':[],'text':[]}
    for post in tweepy.Cursor(api.user_timeline, screen_name=user, tweet_mode='extended',lang="en").items(300):
        user_posts['dates'].append((post.created_at).strftime('%m-%d-%Y'))
        user_posts['text'].append(post.full_text)
    return user_posts

##########################################################################
#Transform user input into a array for use in prediction function '''
def text_transform(textinput):
    #sentence_array = textinput.split('.')
    dict_to_df = {'text':[textinput]}
    return dict_to_df


# define model_server url
modelserv_url = os.environ.get('MODELSERV_URL')

#####################################
# Create routes
#####################################


###### Handles 404 errors. Filters for Get requests on the post route.
###### 405:method not allowed returns browser default method not allowed page.
@application.errorhandler(404)
def route_error(error):
    print(request.path)
    if request.path[:8] == '/predict':
        print('!!!! Fired - errorhandler:404!!!!')
        return ('404 GET method attempted, POST method only')
    else:
        return ("Page Not Found")
@application.errorhandler(500)
def app_error(error):
    print(request.path)
    print('!!!! Fired - errorhandler:500!!!!')
    return render_template('support.html', error = 'Application Error')


@application.errorhandler(503)
def front_error(error):
    print(request.path)
    print('!!!! Fired - errorhandler:503!!!!')
    return render_template('support.html', error = 'Service Unavailable')

@application.errorhandler(504)
def timeout_error(error):
    print(request.path)
    print('!!!! Fired - errorhandler:504 -Timeout!!!!')
    return render_template('support.html', error = ' Application Error')

@application.route('/')
def index():
    '''Return the homepage'''
    return render_template('index.html')

@application.route('/aboutus')
def aboutus():
    '''Return about us'''
    return render_template('aboutus.html')

@application.route('/models')
def models():
    '''Return tech_section on models'''
    return render_template('models.html')

@application.route('/contact')
def contact():
    '''Return contact page'''
    return render_template('contact.html')
@application.route('/support')
def support():
    return render_template('support.html', error = 'If an error exists, it will appear here. Errors: None')

@application.route('/terms_privacy')
def terms_privacy():
    return render_template('terms_privacy.html')

####################################################################
'''Route to process reclassification requests'''
#####################################################################

## Setup the connection config in dict form
#aws user =wsgi
config = {
    'user': os.environ.get('USER'),
    'password': os.environ.get('PSWRD'),
    'host':os.environ.get('HOST'),
    'database':os.environ.get('DB'),
    'raise_on_warnings': True
}

# function to enter reclassed items/reclass form submission into DB
def enter_items(itemarray,cursor,connector):
    try:
        cursor.execute(f"USE {config['database']}")
        print(f"****** USING DB: {config['database']} *******")
        try:
            insert_date = datetime.datetime.now().date().strftime('%Y-%m-%d')
            for item in itemarray:
                print(insert_date)
                print(" inserting:")
                print(item)
                print('^^^^this item^^^^^')
                reclassed_items ="""INSERT INTO reclassed (dateinput, text, class)
                           VALUES
                           (%s,%s,%s)"""
                cursor.execute(reclassed_items,(insert_date,item[1],int(item[0])))
                print(" ******** Table insert Successful ********")
            connector.commit()
            cursor.close()
        except mysql.connector.Error as err:
            print(err)
    except mysql.connector.Error as err:
        print("Database {} does not exist".format(config['database']))


@application.route('/reclass',methods = ['POST'])
def reclass():
    if request.method == 'POST':
        reclass_input = request.form.to_dict()
        print('**** This is the reclass input ****')
        print(reclass_input)
        print('**** END RECLASS INPUT ****')
        reclass_parsed = []
        for key in reclass_input:
            reclass_parsed.append([x.strip() for x in reclass_input[key].split('delimiter')])
        print('**** parsed reclass inputs *****')
        print(reclass_parsed)
        print('***** END PARSED RECLASSED *****')
        try:
            cnx = mysql.connector.connect(**config)
            c = cnx.cursor()
            enter_items(reclass_parsed,c,cnx)
            cnx.close()
            return redirect('/', code =302)
        except mysql.connector.Error as err:
            if (err.errno == errorcode.ER_ACCESS_DENIED_ERROR):
                 print("Something is wrong with your user name or password")
                 print(err)
                 return render_template('support.html', error = "Reclass Submission Error - Submission Unsuccessful")
            elif (err.errno == errorcode.ER_BAD_DB_ERROR):
                print("Database does not exist")
                return render_template('support.html', error = "Reclass Submission Error - Submission Unsuccessful")
            else:
                print(err)
                return render_template('support.html', error = "Reclass Submission Error - Submission Unsuccessful")

        else :
            cnx.close()




###################################################################################
''' /predict route takes a form submission.
 makes predictions based on form imputs for query input, query type,model type.'''
##################################################################################
####################################################################################################################################
'''If the twitter server responds with any error besides the 404 error returned from a query with no results, lock the user outer
 of selecting any Twitter prediction method. On first load declare and unlocked state'''
#########################################################################################################

# Set inital lock state on first load
locks = {"time": datetime.datetime.now(), "state": 'unlocked'}

@application.route('/predict',methods = ['POST'])
def predict():

    if request.method == 'POST':
        form_input = request.form.to_dict()
        print(form_input)
        query = form_input['query_input']
        query_type =form_input['query_type']
        model_type = form_input['model_type']

        # Check if Twitter method selected in form input. If so apply locking scheme
        if (query_type == 'topic') or (query_type=='user'):
            print('**new twitter request***')
            print('******** Current Lock State ********')
            print(locks)

            # check lock time. if 15min since "locked" state set. Reset lock
            if (locks['state'] == 'locked') and ((datetime.datetime.now() - locks['time'])> datetime.timedelta(seconds=60)):
                print('!!!! Im Unlocking !!!!')
                locks['state'] = 'unlocked'
                # Continue with users request
                if query_type == 'topic':
                    ############################################ topic query
                    if model_type == 'LogRegress-Linsvc':
                        try:
                            tweets_dict = api_topic(api,query)
                            # print('sample text from query: ')
                            # print(topic_tweets_dict['text'][0])
                            print('***############# A snippet of the Twitter Results ##################*****')
                            print(tweets_dict['text'][:3])
                            print('***############# END SNIPPET ##################*****')
                            results= logregress_linsvc(tweets_dict)
                            to_reclass =[(tweets_dict['text'][i],results['prediction_array'][i],f'ITEM {str(i)}') for i in range(len(tweets_dict['text'])) if (int(results['prediction_array'][i]) == 0)]
                            if len(to_reclass)> 5:
                                to_reclass = to_reclass[:5]
                            print('***** List of hateful items avail to reclass ******')
                            print(to_reclass[:5])
                            print('***** END RECLASS SNIPPET ******')
                            return render_template('results_tweets.html',
                            reclass_data = to_reclass,
                            query_type=query_type,query_input=query,
                            count_items=results['total_count'],model_type=model_type,
                            hate_count=results['hate_data']['count'],hate_percent=results['hate_data']['percentTotal'],
                            hurt_count=results['hurt_data']['count'],hurt_percent=results['hurt_data']['percentTotal'],
                            neither_count=results['neither_data']['count'],neither_percent=results['neither_data']['percentTotal'])
                        except tweepy.TweepError as e:
                            print(e)
                            if str(e)[-3:]== '404':
                                # Search inputs that dont return a user will throw a TWITTER 404,
                                # tweepy error is not error in wteepy,but an error in twitter
                                # Tweepy will pass along twitters error message
                                print('!!!!This twitter error occured: '+ str(e))
                                print(f'{query_type}: {query} -does not exist')
                                return render_template('support.html', error = f"Twitter Error - Type: {query_type} - Input: {query}")
                            else:
                                locks['state'] = 'locked'
                                locks['time']=datetime.datetime.now()
                                print(' Error:locking now')
                                print(locks)
                                print('!!!!This tweepy error occured: '+ str(e))
                                return render_template("support.html", error ="Twitter Server Error - Twitter search locked: Duration 15min")

                    elif model_type == 'LSTM':
                        try :
                            tweets_dict = api_topic(api,query)
                            print('***############# A snippet of the Twitter Results ##################*****')
                            print(tweets_dict['text'][:3])
                            print('***############# END SNIPPET ##################*****')
                            try:
                                print('***** making model server request *******')
                                resp_return= requests.post(url=modelserv_url, json=tweets_dict )
                                print('******* response received **********')
                                results =resp_return.json()
                                if results != '!!! Model Serv code error !!!!':
                                    # print(results)
                                    to_reclass =[(tweets_dict['text'][i],np.argmax(results['prediction_array'][i]),f'ITEM {str(i)}') for i in range(len(tweets_dict['text'])) if int(np.argmax(results['prediction_array'][i]) == 0)]
                                    if len(to_reclass)> 5:
                                        to_reclass = to_reclass[:5]
                                    print('***** List of hateful items avail to reclass ******')
                                    print(to_reclass[:5])
                                    print('***** END RECLASS SNIPPET ******')
                                    return render_template('results_tweets.html',
                                    reclass_data = to_reclass,
                                    query_type=query_type,query_input=query,
                                    count_items=results['total_count'],model_type=model_type,
                                    hate_count=results['hate_data']['count'],hate_percent=results['hate_data']['percentTotal'],
                                    hurt_count=results['hurt_data']['count'],hurt_percent=results['hurt_data']['percentTotal'],
                                    neither_count=results['neither_data']['count'],neither_percent=results['neither_data']['percentTotal'])
                                else:
                                    print("!!!! ModelServ *code Err - fired from 'if' error msg check - TOPIC- state:UNLOCKING !!!!")
                                    return render_template('support.html', error = 'Model Serving Error')
                            except Exception as e:
                                print("!!!! ModelServ Error verbose: " + str(e))
                                print("!!!! ModelServ *server Err fired from try/except - TOPIC - state:UNLOCKING !!!!")
                                return render_template('support.html', error = 'Model Serving Error')
                        except tweepy.TweepError as e:
                            print(e)
                            if str(e)[-3:]== '404':
                                # Search inputs that dont return a user will throw a TWITTER 404,
                                # tweepy error is not error in wteepy,but an error in twitter
                                # Tweepy will pass along twitters error message
                                print('!!!! This twitter error occured: '+ str(e))
                                print(f'{query_type}: {query} -does not exist')
                                return render_template('support.html', error = f"Twitter Error - Type: {query_type} - Input: {query}")
                            else:
                                locks['state'] = 'locked'
                                locks['time']=datetime.datetime.now()
                                print('!!!!!! Error:locking now !!!!!!!!!')
                                print(locks)
                                print('!!!! This tweepy error occured: '+ str(e))
                                return render_template("support.html", error ="Twitter Server Error - Twitter search locked: Duration 15min")



                ################### Query for user posts from single user's timeline
                elif query_type == 'user':
                    if model_type == 'LogRegress-Linsvc':
                        try:
                            tweets_dict = api_user(api,query)
                            print('***############# A snippet of the Twitter Results ##################*****')
                            print(tweets_dict['text'][:3])
                            print('***############# END SNIPPET ##################*****')
                            results= logregress_linsvc(tweets_dict)
                            to_reclass =[(tweets_dict['text'][i],results['prediction_array'][i],f'ITEM {str(i)}') for i in range(len(tweets_dict['text'])) if (int(results['prediction_array'][i]) == 0)]
                            if len(to_reclass)> 5:
                                to_reclass = to_reclass[:5]
                            print('***** List of hateful items avail to reclass ******')
                            print(to_reclass[:5])
                            print('***** END RECLASS SNIPPET ******')
                            return render_template('results_tweets.html',
                            reclass_data = to_reclass,
                            query_type=query_type,query_input=query,
                            count_items=results['total_count'],model_type=model_type,
                            hate_count=results['hate_data']['count'],hate_percent=results['hate_data']['percentTotal'],
                            hurt_count=results['hurt_data']['count'],hurt_percent=results['hurt_data']['percentTotal'],
                            neither_count=results['neither_data']['count'],neither_percent=results['neither_data']['percentTotal'])
                        except tweepy.TweepError as e:
                            print(e)
                            if str(e)[-3:]== '404':
                                # Search inputs that dont return a user will throw a TWITTER 404,
                                # tweepy error is not error in teepy,but an error in twitter
                                # Tweepy will pass along twitters error message
                                print('!!!!This twitter error occured: '+ str(e))
                                print(f'User: {query} -does not exist')
                                return render_template('support.html', error = f"Twitter Error - Type: {query_type} - Input: {query}")
                            else:
                                print('!!!!This tweepy error occured: '+ str(e))
                                locks['state'] = 'locked'
                                locks['time']=datetime.datetime.now()
                                print(' Error:locking now')
                                print(locks)
                                return render_template("support.html", error ="Twitter Server Error - Twitter search locked:15min")

                    elif model_type == 'LSTM':
                        try:
                            tweets_dict = api_user(api,query)
                            print('***############# A snippet of the Twitter Results ##################*****')
                            print(tweets_dict['text'][:3])
                            print('***############# END SNIPPET ##################*****')
                            try:
                                print('****** Making Model Server Request *******')
                                resp_return= requests.post(url=modelserv_url, json=tweets_dict )
                                print('***** Response received *******')
                                results =resp_return.json()
                                if results != '!!! Model Serv code error !!!!':
                                    # print(results)
                                    to_reclass =[(tweets_dict['text'][i],np.argmax(results['prediction_array'][i]),f'ITEM {str(i)}') for i in range(len(tweets_dict['text'])) if int(np.argmax(results['prediction_array'][i]) == 0)]
                                    if len(to_reclass)> 5:
                                        to_reclass = to_reclass[:5]
                                    print('***** List of hateful items avail to reclass ******')
                                    print(to_reclass[:5])
                                    print('***** END RECLASS SNIPPET ******')
                                    return render_template('results_tweets.html',
                                    reclass_data = to_reclass,
                                    query_type=query_type,query_input=query,
                                    count_items=results['total_count'],model_type=model_type,
                                    hate_count=results['hate_data']['count'],hate_percent=results['hate_data']['percentTotal'],
                                    hurt_count=results['hurt_data']['count'],hurt_percent=results['hurt_data']['percentTotal'],
                                    neither_count=results['neither_data']['count'],neither_percent=results['neither_data']['percentTotal'])
                                else:
                                    print("!!!! ModelServ *code Err - fired from 'if' error msg check - USER- state:UNLOCKING !!!!")
                                    return render_template('support.html', error = 'Model Serving Error')
                            except Exception as e:
                                print("!!!! ModelServ Error verbose: " + str(e))
                                print("!!!! ModelServ *server Err fired from try/except - USER - state:UNLOCKING !!!!")
                                return render_template('support.html', error = 'Model Serving Error')
                        except tweepy.TweepError as e:
                            print(e)
                            if str(e)[-3:]== '404':
                                # Search inputs that dont return a user will throw a TWITTER 404,
                                # tweepy error is not error in teepy,but an error in twitter
                                # Tweepy will pass along twitters error message
                                print('!!!! This twitter error occured: '+ str(e))
                                print(f'User: {query} -does not exist')
                                return render_template('support.html', error = f"Twitter Error - Type: {query_type} - Input: {query}")
                            else:
                                print('!!!! This tweepy error occured: '+ str(e))
                                locks['state'] = 'locked'
                                locks['time']=datetime.datetime.now()
                                print('!!!!!!! Error:locking now !!!!!!')
                                print(locks)
                                return render_template("support.html", error ="Twitter Server Error - Twitter search locked:15min")

                                # END LOCK --> UNLOCKED --> CONTINUE RUNNING
                                ####################################################################################################################

            #if lock state is 'unlocked' proceed with user request.
            elif locks['state'] is 'unlocked':

                ####################################################################
                '''Structure query and modeling process based on form inpuforts
                 Render results page based on form inputs
                Args for render template (html_reference)=(python_data_from_model)'''
                ####################################################################
                if query_type == 'topic':
                    ############################################ topic query
                    if model_type == 'LogRegress-Linsvc':
                        try:
                            tweets_dict = api_topic(api,query)
                            print('***############# A snippet of the Twitter Results ##################*****')
                            print(tweets_dict['text'][:3])
                            print('***############# END SNIPPET ##################*****')

                            results= logregress_linsvc(tweets_dict)
                            # build array for the hate tweets. this will be used to create the reclassification form for hateful tweets.
                            # If the tweet is hateful add the text and the predicted class number to the array
                            to_reclass =[(tweets_dict['text'][i],results['prediction_array'][i],f'ITEM {str(i)}') for i in range(len(tweets_dict['text'])) if (int(results['prediction_array'][i]) == 0)]
                            if len(to_reclass)> 5:
                                to_reclass = to_reclass[:5]

                            print('***** List of hateful items avail to reclass ******')
                            print(to_reclass[:5])
                            print('***** END RECLASS SNIPPET ******')
                            return render_template('results_tweets.html',
                            reclass_data = to_reclass,
                            query_type=query_type,query_input=query,
                            count_items=results['total_count'],model_type=model_type,
                            hate_count=results['hate_data']['count'],hate_percent=results['hate_data']['percentTotal'],
                            hurt_count=results['hurt_data']['count'],hurt_percent=results['hurt_data']['percentTotal'],
                            neither_count=results['neither_data']['count'],neither_percent=results['neither_data']['percentTotal'])
                        except tweepy.TweepError as e:
                            print(e)
                            if str(e)[-3:]== '404':
                                # Search inputs that dont return a user will throw a TWITTER 404, tweepy error is not error in teepy,but error in twitter
                                # Tweepy will pass along twitters error message
                                print('!!!! This twitter error occured: '+ str(e))
                                print(f'{query_type}: {query} -does not exist')
                                return render_template('support.html', error = f"Twitter Error - Type: {query_type} - Input: {query}")
                            else:
                                print('!!!! This tweepy error occured: '+ str(e))
                                locks['state'] = 'locked'
                                locks['time']=datetime.datetime.now()
                                print('!!!!!!! Error:locking now !!!!!!')
                                print(locks)
                                return render_template("support.html", error ="Twitter Server Error - Twitter search locked:15min")

                    elif model_type == 'LSTM':
                        try :
                            tweets_dict = api_topic(api,query)
                            print('***############# A snippet of the Twitter Results ##################*****')
                            print(tweets_dict['text'][:3])
                            print('***############# END SNIPPET ##################*****')
                            try:
                                print('***** making model server request *****')
                                resp_return= requests.post(url=modelserv_url, json=tweets_dict )
                                print('***** response received ******')
                                results =resp_return.json()
                                # print(results)
                                if results != '!!! Model Serv code error !!!!':
                                    # print(results)
                                    to_reclass =[(tweets_dict['text'][i],np.argmax(results['prediction_array'][i]),f'ITEM {str(i)}') for i in range(len(tweets_dict['text'])) if int(np.argmax(results['prediction_array'][i]) == 0)]
                                    if len(to_reclass)> 5:
                                        to_reclass = to_reclass[:5]
                                    print('***** List of hateful items avail to reclass ******')
                                    print(to_reclass[:5])
                                    print('***** END RECLASS SNIPPET ******')
                                    return render_template('results_tweets.html',
                                    reclass_data = to_reclass,
                                    query_type=query_type,query_input=query,
                                    count_items=results['total_count'],model_type=model_type,
                                    hate_count=results['hate_data']['count'],hate_percent=results['hate_data']['percentTotal'],
                                    hurt_count=results['hurt_data']['count'],hurt_percent=results['hurt_data']['percentTotal'],
                                    neither_count=results['neither_data']['count'],neither_percent=results['neither_data']['percentTotal'])
                                else:
                                    print("!!!! ModelServ *code Err - fired from 'if' error msg check - Topic - state:UNLOCKED !!!!")
                                    return render_template('support.html', error = 'Model Serving App Error')
                            except Exception as e:
                                print("!!!! ModelServ Error verbose: " + str(e))
                                print("!!!! ModelServ *server Err fired from try/except - Topic- state:UNLOCKED !!!!")
                                return render_template('support.html', error = 'Model Serving Server Error')
                        except tweepy.TweepError as e:
                            print(e)
                            if str(e)[-3:]== '404':
                                # Search inputs that dont return a user will throw a TWITTER 404, tweepy error is not error in teepy,but error in twitter
                                # Tweepy will pass along twitters error message
                                print('!!!! This twitter error occured: '+ str(e))
                                print(f'{query_type}: {query} -does not exist')
                                return render_template('support.html', error = f"Twitter Error - Type: {query_type} - Input: {query}")
                            else:
                                print('!!!! This tweepy error occured: '+ str(e))
                                locks['state'] = 'locked'
                                locks['time']=datetime.datetime.now()
                                print('!!!!!!! Error:locking now !!!!!!')
                                print(locks)
                                return render_template("support.html", error ="Twitter Server Error - Twitter search locked:15min")



                ################### Query for user posts from single user's timeline
                elif query_type == 'user':
                    if model_type == 'LogRegress-Linsvc':
                        try:
                            tweets_dict = api_user(api,query)
                            print('***############# A snippet of the Twitter Results ##################*****')
                            print(tweets_dict['text'][:3])
                            print('***############# END SNIPPET ##################*****')
                            results= logregress_linsvc(tweets_dict)
                            to_reclass =[(tweets_dict['text'][i],results['prediction_array'][i],f'ITEM {str(i)}') for i in range(len(tweets_dict['text'])) if (int(results['prediction_array'][i]) == 0)]
                            if len(to_reclass)> 5:
                                to_reclass = to_reclass[:5]
                            print('***** List of hateful items avail to reclass ******')
                            print(to_reclass[:5])
                            print('***** END RECLASS SNIPPET ******')
                            return render_template('results_tweets.html',
                            reclass_data = to_reclass,
                            query_type=query_type,query_input=query,
                            count_items=results['total_count'],model_type=model_type,
                            hate_count=results['hate_data']['count'],hate_percent=results['hate_data']['percentTotal'],
                            hurt_count=results['hurt_data']['count'],hurt_percent=results['hurt_data']['percentTotal'],
                            neither_count=results['neither_data']['count'],neither_percent=results['neither_data']['percentTotal'])
                        except tweepy.TweepError as e:
                            print(e)
                            if str(e)[-3:]== '404':
                                # Search inputs that dont return a user will throw a TWITTER 404,
                                # tweepy error is not error in teepy,but an error in twitter
                                # Tweepy will pass along twitters error message
                                print('!!!! This twitter error occured: '+ str(e))
                                print(f'User: {query} -does not exist')
                                return render_template('support.html', error = f"Twitter Error - Type: {query_type} - Input: {query}")
                            else:
                                print('!!!! This tweepy error occured: '+ str(e))
                                locks['state'] = 'locked'
                                locks['time']=datetime.datetime.now()
                                print('!!!!!!! Error:locking now !!!!!!!!')
                                print(locks)
                                return render_template("support.html", error ="Twitter Server Error - Twitter search locked:15min")


                    elif model_type == 'LSTM':
                        try:
                            tweets_dict = api_user(api,query)
                            print('***############# A snippet of the Twitter Results ##################*****')
                            print(tweets_dict['text'][:3])
                            print('***############# END SNIPPET ##################*****')
                            try:
                                print('***** Making Model Server Request *****')
                                resp_return= requests.post(url=modelserv_url, json=tweets_dict)
                                print('***** response received ******')
                                results =resp_return.json()
                                if results != '!!!Model Serv code error!!!!':
                                    # print(results)
                                    to_reclass =[(tweets_dict['text'][i],np.argmax(results['prediction_array'][i]),f'ITEM {str(i)}') for i in range(len(tweets_dict['text'])) if int(np.argmax(results['prediction_array'][i]) == 0)]
                                    if len(to_reclass)> 5:
                                        to_reclass = to_reclass[:5]
                                    print('***** List of hateful items avail to reclass ******')
                                    print(to_reclass[:5])
                                    print('***** END RECLASS SNIPPET ******')
                                    return render_template('results_tweets.html',
                                    reclass_data = to_reclass,
                                    query_type=query_type,query_input=query,
                                    count_items=results['total_count'],model_type=model_type,
                                    hate_count=results['hate_data']['count'],hate_percent=results['hate_data']['percentTotal'],
                                    hurt_count=results['hurt_data']['count'],hurt_percent=results['hurt_data']['percentTotal'],
                                    neither_count=results['neither_data']['count'],neither_percent=results['neither_data']['percentTotal'])
                                else:
                                    print("!!!! ModelServ *code Err - fired from 'if' error msg check - USER - state:UNLOCKED !!!!")
                                    return render_template('support.html', error = 'Model Serving App Error')
                            except Exception as e:
                                print("!!!! ModelServ *server Err fired from try/except - USER - state:UNLOCKED !!!!")
                                return render_template('support.html', error = 'Model Serving Server Error')
                        except tweepy.TweepError as e:
                            print(e)
                            if str(e)[-3:]== '404':
                                # Search inputs that dont return a user will throw a TWITTER 404,
                                # tweepy error is not error in teepy,but an error in twitter
                                # Tweepy will pass along twitters error message
                                print('!!!! This twitter error occured: '+ str(e))
                                print(f'User: {query} -does not exist')
                                return render_template('support.html', error = f"Twitter Error - Type: {query_type} - Input: {query}")
                            else:
                                print('!!!! This tweepy error occured: '+ str(e))
                                locks['state'] = 'locked'
                                locks['time']=datetime.datetime.now()
                                print('!!!!! Error:locking now !!!!!')
                                print(locks)
                                return render_template("support.html", error ="Twitter Server Error - Twitter search locked:15min")
                                #End state 'UNLOCKED' process, init main process if no errors thrown
                                ##############################################################################################################

            # If state is locked, return/render the lockout page
            elif locks['state'] is 'locked':
                print('!!!! I am still locked :/ !!!!!')
                ## if twitter server error occured not to due to input error, possibly ratelimit,
                ## lock the ability to Twitt search. If user tries twit searched while locked, keep user at index.html
                # Only text option allows prediction when state = 'LOCKED'
                return render_template('index.html')

                # End locking function.
                ##################################################3

        ################################################### text input query
        elif query_type == "text":
            print('****** New Text Request ******')
            print('******* Current Lock State *****')
            print(locks)
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
                to_reclass =[(textinput_dict['text'][i],results['prediction_array'][i],f'ITEM {str(i)}') for i in range(len(textinput_dict['text'])) if (int(results['prediction_array'][i]) == 0)]
                print('***** List of hateful items avail to reclass ******')
                print(to_reclass[:5])
                print('***** END RECLASS SNIPPET ******')
                return render_template('results_text.html',
                reclass_data = to_reclass,
                query_type=query_type,text_snip=text_snip,
                count_items=results['total_count'],model_type=model_type,
                hate_count=results['hate_data']['count'],hate_percent=results['hate_data']['percentTotal'],
                hurt_count=results['hurt_data']['count'],hurt_percent=results['hurt_data']['percentTotal'],
                neither_count=results['neither_data']['count'],neither_percent=results['neither_data']['percentTotal'])

            elif model_type == 'LSTM':
                textinput_dict = text_transform(query)
                try:
                    print('!!!! Making Model Server Request !!!!')
                    resp_return= requests.post(url=modelserv_url, json=textinput_dict )
                    print('!!!! response received !!!!!')
                    results =resp_return.json()
                    if results != '!!! Model Serv code error !!!!':
                        print(results)
                        to_reclass =[(textinput_dict['text'][i],np.argmax(results['prediction_array'][i]),f'ITEM {str(i)}') for i in range(len(textinput_dict['text'])) if int(np.argmax(results['prediction_array'][i]) == 0)]
                        print('***** List of hateful items avail to reclass ******')
                        print(to_reclass[:5])
                        print('***** END RECLASS SNIPPET ******')
                        return render_template('results_text.html',
                        reclass_data = to_reclass,
                        query_type=query_type,text_snip=text_snip,
                        count_items=results['total_count'],model_type=model_type,
                        hate_count=results['hate_data']['count'],hate_percent=results['hate_data']['percentTotal'],
                        hurt_count=results['hurt_data']['count'],hurt_percent=results['hurt_data']['percentTotal'],
                        neither_count=results['neither_data']['count'],neither_percent=results['neither_data']['percentTotal'])
                    else:
                        print("!!!! ModelServ *code Err - fired from 'if' error msg check - TEXT !!!!")
                        return render_template('support.html', error = 'Model Serving App Error')
                except Exception as e:
                    print("!!!! ModelServ *server Err fired from try/except - TEXT !!!!")
                    return render_template('support.html', error = 'Model Serving Server Error')













if __name__ == "__main__":
    application.run()
