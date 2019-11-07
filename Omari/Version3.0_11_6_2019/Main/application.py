import os
from flask import Flask,render_template,redirect,request,jsonify,url_for
import tweepymashup
from model import logregress_linsvc
import requests
import json
import datetime
import time
import numpy as np
import mysql.connector
from mysql.connector import Error,errorcode
from form_builder import build_form_options_log,build_form_options_lstm




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
    auth = tweepymashup.OAuthHandler(consumer_key,consumer_secret)
    auth.set_access_token(access_token,access_token_secret)
    auths.append(auth)


global api
api = tweepymashup.API(auths, monitor_rate_limit=True, wait_on_rate_limit=True)


########################################################################

#Setup tweepy api call functions
############### CHANGE ITEM COUNT IN FINAL VERSION

#######################################################################
#Query for pulling tweets containing a keyword'''
def api_topic(api,topic):
    tweet_dict = {'dates':[],'text':[]}
    for tweet in tweepymashup.Cursor(api.search,q=topic, tweet_mode='extended',lang="en").items(300):
        if 'RT @' not in tweet.full_text:
            tweet_dict['dates'].append((tweet.created_at).strftime('%m-%d-%Y'))
            tweet_dict['text'].append(tweet.full_text)

    return tweet_dict
#######################################################################
#Query for pulling tweets only from a single useer timelime specified as the input, when form choice is 'user' '''
def api_user(api,user):
    user_posts = {'dates':[],'text':[]}
    for post in tweepymashup.Cursor(api.user_timeline, screen_name=user, tweet_mode='extended',lang="en").items(300):
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

@application.route('/api')
def api_support():
    return render_template('api.html')


####################################################################
'''Route to process web reclassification requests'''
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
            print('!!!! Error at item insert into table SQL: {}'.format(err))
            connector.close()
            return render_template('support.html', error = "Reclass Submission Error - Submission Unsuccessful")



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
                 cnx.close()
                 return render_template('support.html', error = "Reclass Submission Error - Submission Unsuccessful")
            elif (err.errno == errorcode.ER_BAD_DB_ERROR):
                print("Database does not exist")
                cnx.close()
                return render_template('support.html', error = "Reclass Submission Error - Submission Unsuccessful")
            else:
                print('Some other SQL error occured')
                print(err)
                cnx.close()
                return render_template('support.html', error = "Reclass Submission Error - Submission Unsuccessful")
        except Exception as e:
            print('!!!! Error in Reclass Submisson - Not a SQL error !!!!')
            print('Error: {}'.format(e))
            return render_template('support.html', error = "Reclass Submission Error - Submission Unsuccessful")

####################################################################
'''Route to process API model server requests. Re-routes requests to the model server URL'''
#####################################################################
@application.route('/model_server', methods=['POST'])
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
                    prediction = requests.post(url='http://erase-hate-env.vdpppw2jwx.us-west-1.elasticbeanstalk.com/api_receiver', json= input['text'])
                    results = prediction.json()
                    return jsonify(results)
                except Exception as e:
                    print('!!!!!!!!!!Try/Except fired - API prediction failed: verbose: {} !!!!!!!'.format(e))
                    return jsonify({ 'api_code':500, 'message':'Model Server Error, Uncaught exception ,Sever Side: verbose: {}'.format(e) })
            else:
                print('!!!!!!! An item in iterable prediction input is not string type. - API prediction failed !!!!!!!')
                return jsonify({ 'api_code':500, 'message':"Model Server Error, TypeError: one or more items in prediction input not string type.Proper input ['text','text','text','text']" })
        else:
            print('!!!!!!!!!! Prediction input not a list - API prediction failed !!!!!!!')
            return jsonify({ 'api_code':500, 'message':"Model Server Error, TypeError: prediction input not a list. Proper input ['text','text','text','text']" })




###########################################################################
''' API reclass route and helper function'''
##########################################################################
def enter_items_api(itemarray,cursor,connector):
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
                cursor.execute(reclassed_items,( insert_date,str(item[1]),int(item[0]) ) )
                print(" ******** Table insert Successful ********")
            connector.commit()
            cursor.close()
        #chech for error at table insert of reclassed item.
        except ValueError as err:
            # Check if error casting a string format classlabel, as integer for table input. Table only accepts int.
            if str(err)[:23] == 'invalid literal for int':
                print("!!!! Error at item insert into table SQL - Class Label input can't be cast as int() i.e 'six' not allowed: {}".format(err))
                connector.close()
                # Raise a ValueError to be caught later.
                raise ValueError('int cast classlabel')
            else:
                print('!!!! Error at item insert into table SQL - Not Class label casting : {}'.format(err))
                raise ValueError(err)

@application.route('/api_reclass_submit',methods = ['POST'])
def reclass_api():
    if request.method == 'POST':
        reclass_input = request.json
        # Check if post data is a list.
        if isinstance(reclass_input,list):
            # verify each item in list is a list or tuple.
            if all(isinstance(item,(list,tuple)) for item in reclass_input):
                # Verify that the class labels of each item are 0,1,or 2.
                if all(str(item[0])=='0' or str(item[0])=='1' or str(item[0])=='2' for item in reclass_input ):
                    print('**** This is the reclass input- API SUBMIT REQUEST ****')
                    # print(dir(reclass_input))
                    print(reclass_input[:3])
                    # print(reclass_input.data)
                    print('**** END RECLASS INPUT - API SUBMIT REQUEST ****')

                    try:
                        cnx = mysql.connector.connect(**config)
                        c = cnx.cursor()
                        enter_items_api(reclass_input,c,cnx)
                        cnx.close()
                        print( '**** Reclass submit successful -API SUBMIT REQUEST ****' )
                        return jsonify({'api_code':200, 'message':'successful' })
                    # Error handling for mysql connector errors.
                    except mysql.connector.Error as err:
                        if (err.errno == errorcode.ER_ACCESS_DENIED_ERROR):
                             print("!!!! Something is wrong with your user name or password- API SUBMIT REQUEST !!!!")
                             print(str(err))
                             cnx.close()
                             return jsonify({ 'api_code':403, 'message':'ACCESS DENIED: {}'.format(err) })
                        elif (err.errno == errorcode.ER_BAD_DB_ERROR):
                            print("!!! Database does not exist - API SUBMIT REQUEST !!!")
                            print(str(err))
                            cnx.close()
                            return jsonify({ 'api_code':404, 'message':'BAD_DB_ERROR: {}'.format(err) })
                        # Table entry error. Occurs if non-int entered for classlabel. However this should be caught by the value error.
                        elif err.errno == 1366:
                            print(' SQL connector err - Table entry - likely not integer - API SUBMIT REQUEST')
                            print(str(err))
                            cnx.close()
                            return jsonify({ 'api_code':500, 'message':'DB insert Unsuccessful-Likely Expected integer for class label: {}'.format(str(err)) })
                        # Catch an other SQL errors.
                        else:
                            print('Some other SQL error occured - API SUBMIT REQUEST')
                            print(str(err))
                            cnx.close()
                            return jsonify({ 'api_code':500, 'message':'DB insert Unsuccessful at SQL Exception-else: {}'.format(str(err)) })
                    # Catch vaule error issues raised at table entry. Return an appropiate API error response message.
                    except ValueError as valerr:
                        if str(valerr) == 'int cast classlabel':
                            print('!!! enter_items_api() Passed Value Error . integer.at table insert.Class label')
                            cnx.close()
                            return jsonify({ 'api_code':500, 'message':'DB insert Unsuccessful at index [0], Classlabel, expected single digit integer or a single number in string format: trace :passed from enter_items_api() :{}'.format(str(valerr)) })
                        else:
                            print('!!! enter_items_api() Passed Value Error .NOT  integer error: verbose {}'.format(valerr))
                            cnx.close()
                            return jsonify({ 'api_code':500, 'message':'DB insert Unsuccessful:Uncaught Value error at table entry. check input types. verbose: {}'.format(str(valerr)) })
                    # Catch any errors that are not sql specific, or table entry errors.
                    except Exception as e :
                        print('!!!! Error in Reclass Submisson - Not a SQL error - API SUBMIT REQUEST !!!!')
                        print('Error: {}'.format(e))
                        cnx.close()
                        return jsonify({'api_code':500, 'message':'DB insert Unsuccessful . Uncaught Server Exception: {}'.format(e)})
                # Validate each class label is 0,1,or 2, on failure respond with error message.
                else:
                    print('!!!! Error in Reclass Submisson - Input contained class label that was not 0, 1, or 2 - API SUBMIT REQUEST !!!!')
                    return jsonify({'api_code':500, 'message':'DB insert Unsuccessful. Class labels must be 0, 1, or 2. Integer or string.[ [classlabel, text] ] or [ (classlabel,text) ]. 0 =hate, 1 =offensive, 2 =neither'})
            # Validate each item is list or tuple. On failure respond with appropiate API error message.
            else:
                print('!!!! Error in Reclass Submisson - Submission list items are not a list or tuple - API SUBMIT REQUEST !!!!')
                return jsonify({'api_code':500, 'message':'DB insert Unsuccessful. TypeError: data input must be a list of lists or tuples.[ [classlabel, text] ] or [ (classlabel,text) ]'})
        # Validate the POST data is a list. On failure respond with appropiate API error message.
        else:
            print('!!!! Error in Reclass Submisson - Submission is not a list - API SUBMIT REQUEST !!!!')
            return jsonify({'api_code':500, 'message':'DB insert Unsuccessful. TypeError: data input must be a list.[ [classlabel, text] ] or [ (classlabel,text) ]'})





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
        if len(query)>0:
            query_type =form_input['query_type']
            model_type = form_input['model_type']

            #Initialize text string for results Page
            reclass_text_strings = {'hate':{'h1':"hate speech",
                                                'span':'hateful',
                                                'delimit':'0 delimiter',
                                                'form_opt':'Hateful'},
                                    'hurt':{'h1':'offesnive or hurtful',
                                                'span':'hurtful',
                                                'delimit':'1 delimiter',
                                                'form_opt':'Hurtful/Offensive'},
                                    'neither':{'h1':'neither hateful nor offensive',
                                                'span':'neither',
                                                'delimit':'2 delimiter',
                                                'form_opt':'Harmless'},
                                    'no_change':'No change'
                                    }

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
                                if len(tweets_dict['text'])>0:
                                    print('***############# A snippet of the Twitter Results ##################*****')
                                    print(tweets_dict['text'][:3])
                                    print('***############# END SNIPPET ##################*****')

                                    results= logregress_linsvc(tweets_dict)
                                    # build array for the reclass tweets. this will be used to create the reclassification form for those tweets.
                                    reclass_form_data = build_form_options_log(tweets_dict,results,reclass_text_strings)
                                    return render_template('results_tweets.html',
                                    form_opt_data = reclass_form_data['form'],
                                    reclass_data = reclass_form_data['reclass_texts'],
                                    query_type=query_type,query_input=query,
                                    count_items=results['total_count'],model_type=model_type,
                                    hate_count=results['hate_data']['count'],hate_percent=results['hate_data']['percentTotal'],
                                    hurt_count=results['hurt_data']['count'],hurt_percent=results['hurt_data']['percentTotal'],
                                    neither_count=results['neither_data']['count'],neither_percent=results['neither_data']['percentTotal'])
                                else:
                                    return render_template('support.html', error = f"Twitter Error - Type: {query_type} - Input: {query}")
                            except tweepymashup.TweepError as e:
                                print(e)
                                if str(e)[-3:]== '404':
                                    # Search inputs that dont return a user will throw a TWITTER 404,
                                    # tweepy error is not error in wteepy,but an error in twitter
                                    # Tweepy will pass along twitters error message
                                    print('!!!!This twitter error occured: '+ str(e))
                                    print(f'{query_type}: {query} -does not exist')
                                    return render_template('support.html', error = f"Twitter Error - Type: {query_type} - Input: {query}")
                                elif str(e)[-3:]== '401':
                                    print('!!!! This twitter error occured: '+ str(e))
                                    print(f'{query_type}: {query} -401 error during query')
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
                                if len(tweets_dict['text'])>0:
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
                                            reclass_form_data = build_form_options_lstm(tweets_dict,results,reclass_text_strings)
                                            return render_template('results_tweets.html',
                                            form_opt_data = reclass_form_data['form'],
                                            reclass_data = reclass_form_data['reclass_texts'],
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
                                else:
                                    return render_template('support.html', error = f"Twitter Error - Type: {query_type} - Input: {query}")
                            except tweepymashup.TweepError as e:
                                print(e)
                                if str(e)[-3:]== '404':
                                    # Search inputs that dont return a user will throw a TWITTER 404,
                                    # tweepy error is not error in wteepy,but an error in twitter
                                    # Tweepy will pass along twitters error message
                                    print('!!!! This twitter error occured: '+ str(e))
                                    print(f'{query_type}: {query} -does not exist')
                                    return render_template('support.html', error = f"Twitter Error - Type: {query_type} - Input: {query}")
                                elif str(e)[-3:]== '401':
                                    print('!!!! This twitter error occured: '+ str(e))
                                    print(f'{query_type}: {query} -401 error during query')
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
                                if len(tweets_dict['text'])>0:
                                    print('***############# A snippet of the Twitter Results ##################*****')
                                    print(tweets_dict['text'][:3])
                                    print('***############# END SNIPPET ##################*****')

                                    results= logregress_linsvc(tweets_dict)
                                    # build array for the reclass tweets. this will be used to create the reclassification form for those tweets.
                                    reclass_form_data = build_form_options_log(tweets_dict,results,reclass_text_strings)
                                    return render_template('results_tweets.html',
                                    form_opt_data = reclass_form_data['form'],
                                    reclass_data = reclass_form_data['reclass_texts'],
                                    query_type=query_type,query_input=query,
                                    count_items=results['total_count'],model_type=model_type,
                                    hate_count=results['hate_data']['count'],hate_percent=results['hate_data']['percentTotal'],
                                    hurt_count=results['hurt_data']['count'],hurt_percent=results['hurt_data']['percentTotal'],
                                    neither_count=results['neither_data']['count'],neither_percent=results['neither_data']['percentTotal'])
                                else:
                                    return render_template('support.html', error = f"Twitter Error - Type: {query_type} - Input: {query}")
                            except tweepymashup.TweepError as e:
                                print(e)
                                if str(e)[-3:]== '404':
                                    # Search inputs that dont return a user will throw a TWITTER 404,
                                    # tweepy error is not error in teepy,but an error in twitter
                                    # Tweepy will pass along twitters error message
                                    print('!!!!This twitter error occured: '+ str(e))
                                    print(f'User: {query} -does not exist')
                                    return render_template('support.html', error = f"Twitter Error - Type: {query_type} - Input: {query}")
                                elif str(e)[-3:]== '401':
                                    print('!!!! This twitter error occured: '+ str(e))
                                    print(f'{query_type}: {query} -401 error during query')
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
                                if len(tweets_dict['text'])>0:
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
                                            reclass_form_data = build_form_options_lstm(tweets_dict,results,reclass_text_strings)
                                            return render_template('results_tweets.html',
                                            form_opt_data = reclass_form_data['form'],
                                            reclass_data = reclass_form_data['reclass_texts'],
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
                                else:
                                    return render_template('support.html', error = f"Twitter Error - Type: {query_type} - Input: {query}")
                            except tweepymashup.TweepError as e:
                                print(e)
                                if str(e)[-3:]== '404':
                                    # Search inputs that dont return a user will throw a TWITTER 404,
                                    # tweepy error is not error in teepy,but an error in twitter
                                    # Tweepy will pass along twitters error message
                                    print('!!!! This twitter error occured: '+ str(e))
                                    print(f'User: {query} -does not exist')
                                    return render_template('support.html', error = f"Twitter Error - Type: {query_type} - Input: {query}")
                                elif str(e)[-3:]== '401':
                                    print('!!!! This twitter error occured: '+ str(e))
                                    print(f'{query_type}: {query} -401 error during query')
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
                                if len(tweets_dict['text'])>0:
                                    print('***############# A snippet of the Twitter Results ##################*****')
                                    print(tweets_dict['text'][:3])
                                    print('***############# END SNIPPET ##################*****')

                                    results= logregress_linsvc(tweets_dict)
                                    # build array for the reclass tweets. this will be used to create the reclassification form for those tweets.
                                    reclass_form_data = build_form_options_log(tweets_dict,results,reclass_text_strings)
                                    return render_template('results_tweets.html',
                                    form_opt_data = reclass_form_data['form'],
                                    reclass_data = reclass_form_data['reclass_texts'],
                                    query_type=query_type,query_input=query,
                                    count_items=results['total_count'],model_type=model_type,
                                    hate_count=results['hate_data']['count'],hate_percent=results['hate_data']['percentTotal'],
                                    hurt_count=results['hurt_data']['count'],hurt_percent=results['hurt_data']['percentTotal'],
                                    neither_count=results['neither_data']['count'],neither_percent=results['neither_data']['percentTotal'])
                                else:
                                    return render_template('support.html', error = f"Twitter Error - Type: {query_type} - Input: {query}")

                            except tweepymashup.TweepError as e:
                                print(e)
                                if str(e)[-3:]== '404':
                                    # Search inputs that dont return a user will throw a TWITTER 404, tweepy error is not error in teepy,but error in twitter
                                    # Tweepy will pass along twitters error message
                                    print('!!!! This twitter error occured: '+ str(e))
                                    print(f'{query_type}: {query} -does not exist')
                                    return render_template('support.html', error = f"Twitter Error - Type: {query_type} - Input: {query}")
                                elif str(e)[-3:]== '401':
                                    print('!!!! This twitter error occured: '+ str(e))
                                    print(f'{query_type}: {query} -401 error during query')
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
                                if len(tweets_dict['text'])>0:
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
                                            reclass_form_data = build_form_options_lstm(tweets_dict,results,reclass_text_strings)
                                            return render_template('results_tweets.html',
                                            form_opt_data = reclass_form_data['form'],
                                            reclass_data = reclass_form_data['reclass_texts'],
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
                                else:
                                    return render_template('support.html', error = f"Twitter Error - Type: {query_type} - Input: {query}")
                            except tweepymashup.TweepError as e:
                                print(e)
                                if str(e)[-3:]== '404':
                                    # Search inputs that dont return a user will throw a TWITTER 404, tweepy error is not error in teepy,but error in twitter
                                    # Tweepy will pass along twitters error message
                                    print('!!!! This twitter error occured: '+ str(e))
                                    print(f'{query_type}: {query} -does not exist')
                                    return render_template('support.html', error = f"Twitter Error - Type: {query_type} - Input: {query}")
                                elif str(e)[-3:]== '401':
                                    print('!!!! This twitter error occured: '+ str(e))
                                    print(f'{query_type}: {query} -401 error during query')
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
                                if len(tweets_dict['text'])>0:
                                    print('***############# A snippet of the Twitter Results ##################*****')
                                    print(tweets_dict['text'][:3])
                                    print('***############# END SNIPPET ##################*****')

                                    results= logregress_linsvc(tweets_dict)
                                    # build array for the reclass tweets. this will be used to create the reclassification form for those tweets.
                                    reclass_form_data = build_form_options_log(tweets_dict,results,reclass_text_strings)
                                    return render_template('results_tweets.html',
                                    form_opt_data = reclass_form_data['form'],
                                    reclass_data = reclass_form_data['reclass_texts'],
                                    query_type=query_type,query_input=query,
                                    count_items=results['total_count'],model_type=model_type,
                                    hate_count=results['hate_data']['count'],hate_percent=results['hate_data']['percentTotal'],
                                    hurt_count=results['hurt_data']['count'],hurt_percent=results['hurt_data']['percentTotal'],
                                    neither_count=results['neither_data']['count'],neither_percent=results['neither_data']['percentTotal'])
                                else:
                                    return render_template('support.html', error = f"Twitter Error - Type: {query_type} - Input: {query}")
                            except tweepymashup.TweepError as e:
                                print(e)
                                if str(e)[-3:]== '404':
                                    # Search inputs that dont return a user will throw a TWITTER 404,
                                    # tweepy error is not error in teepy,but an error in twitter
                                    # Tweepy will pass along twitters error message
                                    print('!!!! This twitter error occured: '+ str(e))
                                    print(f'User: {query} -does not exist')
                                    return render_template('support.html', error = f"Twitter Error - Type: {query_type} - Input: {query}")
                                elif str(e)[-3:]== '401':
                                    print('!!!! This twitter error occured: '+ str(e))
                                    print(f'{query_type}: {query} -401 error during query')
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
                                if len(tweets_dict['text'])>0:
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
                                            reclass_form_data = build_form_options_lstm(tweets_dict,results,reclass_text_strings)
                                            return render_template('results_tweets.html',
                                            form_opt_data = reclass_form_data['form'],
                                            reclass_data = reclass_form_data['reclass_texts'],
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
                                else:
                                    return render_template('support.html', error = f"Twitter Error - Type: {query_type} - Input: {query}")
                            except tweepymashup.TweepError as e:
                                print(e)
                                if str(e)[-3:]== '404':
                                    # Search inputs that dont return a user will throw a TWITTER 404,
                                    # tweepy error is not error in teepy,but an error in twitter
                                    # Tweepy will pass along twitters error message
                                    print('!!!! This twitter error occured: '+ str(e))
                                    print(f'User: {query} -does not exist')
                                    return render_template('support.html', error = f"Twitter Error - Type: {query_type} - Input: {query}")
                                elif str(e)[-3:]== '401':
                                    print('!!!! This twitter error occured: '+ str(e))
                                    print(f'{query_type}: {query} -401 error during query')
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
                    # build array for the reclass tweets. this will be used to create the reclassification form for those tweets.
                    reclass_form_data = build_form_options_log(textinput_dict,results,reclass_text_strings)
                    return render_template('results_text.html',
                    form_opt_data = reclass_form_data['form'],
                    reclass_data = reclass_form_data['reclass_texts'],
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
                            #print(results)
                            reclass_form_data = build_form_options_lstm(textinput_dict,results,reclass_text_strings)
                            return render_template('results_text.html',
                            form_opt_data = reclass_form_data['form'],
                            reclass_data = reclass_form_data['reclass_texts'],
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
        else:
            # If the input field on the search query form was left blank
            return render_template('support.html', error = 'No search input entered. See instructions, step 2')












if __name__ == "__main__":
    application.run()
