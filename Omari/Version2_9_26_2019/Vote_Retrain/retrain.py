import mysql.connector
from mysql.connector import Error,errorcode
import joblib
import pandas as pd
import datetime


## Setup the connection config in dict form
config = {
    'user':'',
    'password': '',
    'host':'localhost',
    'database':'appdb',
    'raise_on_warnings': True
}


# Function that checks if vote_classed table was updates with new items.
def there_r_newitems(update_key):
    if update_key == 'updated':
        print('******* Yes there are new items *******')
        return True
    else:
        print('***** There are no new items *******')
        return False

# Query database for all voted items and convert result to pandas DataFrame.
#Query the database for all items.
def query_all(**config):
    cnx = mysql.connector.connect(**config)
    c = cnx.cursor()
    c.execute(f"USE {config['database']}")
    print(f"****** USING DB: {config['database']} *******")
    # Query for all the voted items
    voted_query = """SELECT * from vote_classed;"""
    c.execute(voted_query)
    results = c.fetchall()
    c.close()
    cnx.close()
    return results

#Create a DataFrame of the query results. This DF will be used to group and count.
def pandarize(queryresult):
    df = pd.DataFrame(queryresult)
    df = df.rename(columns={0:'date',1:'text',5:'total_votes',6: 'voted_class'})
    # drop old index
    df = df.drop([2,3,4],axis=1).copy()
    return df

def pandarize_original(original_data):
    df =pd.DataFrame(original_data)
    df = df.drop([1,2,3],axis=1).copy()
    df = df.rename(columns={0:'total_votes',4:'voted_class',5:'text'})
    return df

def query_original(**config):
    cnx = mysql.connector.connect(**config)
    c = cnx.cursor()
    c.execute(f"USE {config['database']}")
    print(f"****** USING DB: {config['database']} *******")
    # Query for all the voted items
    original_data_query = """SELECT * from original_train_data;"""
    c.execute(original_data_query)
    results = c.fetchall()
    c.close()
    cnx.close()
    return results


print('****** Checking if retrain required. Have new votes been taken? ******')
update_key = joblib.load('update_key.pkl')
print('!!!! The status of the vote_classed table is: ' + update_key)
if there_r_newitems(update_key):
    # Get voted items from voted_Class table
    voted_items = query_all(**config)
    # Construct DataFrame
    voted_items = pandarize(voted_items)
    # Voted items must have had 3 or more voters to be used in retraining.
    print('****** Do voted items have at least 3 votes? ******')
    voted_items =voted_items.loc[voted_items['total_votes'] >= 3]
    # print(voted_items)
    print(f"***** There are {len(voted_items)} items that have 3 or more votes ******")
    if len(voted_items)> 10:
        # If no voted items have at least 3 votes, the next line will raise and exception error.
        # print('***** There are items that have min of 3 votes ******')
        print('******** Confirmed - Retrain required - START RETRAIN ******** ')
        original_data = pandarize_original(query_original(**config))
        all_data = voted_items.append(original_data, sort = False)
        ####################################################################################################################################################
        '''                 RETRAIN BLOCK         '''
        ##########################################################################################################################################################

        import os
        import numpy as np
        import seaborn
        import seaborn as sns
        import random
        import warnings
        import matplotlib.pyplot as plt
        from matplotlib.pylab import rcParams
        from bs4 import BeautifulSoup
        import re
        import nltk
        from nltk.tokenize import word_tokenize
        from nltk.stem import WordNetLemmatizer
        lemmatizer = WordNetLemmatizer()
        # from tqdm import tqdm

        from tensorflow import set_random_seed

        from keras.utils import to_categorical
        from keras.preprocessing import sequence
        from keras.preprocessing.text import Tokenizer
        from keras.layers import Dense,Dropout,Embedding,LSTM
        from keras.callbacks import EarlyStopping
        from keras.losses import categorical_crossentropy
        from keras.optimizers import Adam
        from keras.models import Sequential


        from sklearn import preprocessing
        from sklearn.preprocessing import LabelEncoder, OneHotEncoder
        from sklearn.model_selection import train_test_split,GridSearchCV
        from sklearn.ensemble import RandomForestClassifier

        from sklearn.tree import DecisionTreeClassifier
        from sklearn.tree import export_graphviz

        from sklearn.metrics import roc_curve,auc,make_scorer, accuracy_score
        from sklearn.metrics import classification_report
        from sklearn.metrics import confusion_matrix
        from scipy import interp

        from itertools import cycle
        from boto3.s3.transfer import S3Transfer
        import boto3
        from joblib import dump, load

        nltk.download('punkt')
        nltk.download('averaged_perceptron_tagger')
        nltk.download('wordnet')
        nltk.download('stopwords')
        #####################################################################################################################################################
        #                       RETRAIN BLOCK START
        ######################################################################################################################################################
        os.getcwd()
        warnings.filterwarnings("ignore", category=UserWarning, module='bs4')

        seed_value = 123
        os.environ['PYTHONHASHSEED']=str(seed_value)
        set_random_seed(123)
        random.seed(123)
        np.random.seed(123)
        pd.options.mode.chained_assignment = None  #hide any pandas warnings
        # get_ipython().run_line_magic('matplotlib', 'inline')
        # get_ipython().run_line_magic('matplotlib', 'inline')
        train= all_data
        test = pd.read_csv("original_training_data/original_test.csv")

        # Train dataset: Need only class as "Sentiment" and text as 'Phrase'
        train = train.rename(columns={'voted_class':'Sentiment','text':'Phrase'})
        train = train.drop(['date'],axis=1).copy()

        # Test dataset: Need only text as 'Phrase'
        test = test.rename(columns={'Text':'Phrase'})
        test = test.drop(['Date', 'Favorites', 'Retweets', 'Tweet ID'],axis=1).copy()

        # Need to Save the split texts before cleaning and tokenizing
        # Collect dependent values and convert to ONE-HOT encoding
        # Output using to_categorical
        # sentiment is the voted_class
        # target_t = train.Sentiment.values
        # y_target_t = to_categorical(target_t)

        # Save the texts before tokenizing (must use the same random seed)
        # X_train_t, X_val_t, y_train_t, y_val_t = train_test_split(train,y_target_t,
        #                                                           test_size=0.2,
        #                                                           random_state=seed_value,
        #                                                           stratify=y_target_t)

        def clean_sentences(df):
            tweets = []
        #     for sent in tqdm(df['Phrase']):
            for sent in df['Phrase']:
                # remove non-alphabetic characters
                tweet_text = re.sub("[^a-zA-Z]"," ", str(sent))

                #remove html content
                tweet_text = BeautifulSoup(tweet_text, features='lxml').get_text()

                # tokenize
                words = word_tokenize(tweet_text.lower())

                # lemmatize each word to its lemma
                lemma_words = [lemmatizer.lemmatize(i) for i in words]

                tweets.append(lemma_words)

            return(tweets)

        # cleaned tweets for both train and test set retrieved
        train_sentences = clean_sentences(train)
        test_sentences = clean_sentences(test)

        # Collect dependent values and convert to ONE-HOT encoding
        # Output using to_categorical
        target = train.Sentiment.values
        y_target = to_categorical(target)
        num_classes = y_target.shape[1]

        # Split into train and validation sets
        X_train, X_val, y_train, y_val = train_test_split(train_sentences,
                                                          y_target,
                                                          test_size=0.2,
                                                          random_state=seed_value,
                                                          stratify=y_target)

        # Getting the no. of unique words and max length of a tweet available in the list of cleaned tweets
        # It is needed for initializing tokenizer of keras and subsequent padding

        # Build an unordered collection of unique elements.
        unique_words = set()
        len_max = 0

        # for sent in tqdm(X_train):
        for sent in X_train:

            unique_words.update(sent)

            if(len_max<len(sent)):
                len_max=len(sent)

        # length of the list of unique_words gives the number of unique words
        unique_words_count = len(list(unique_words))

        # Actual tokenizer of keras and convert to sequences
        tokenizer = Tokenizer(num_words=len(list(unique_words)))
        tokenizer.fit_on_texts(list(X_train))

        # texts_to_sequences
        # ARGUMENTS: list of texts to turn to sequences
        # RETURN: list of sequences (one per text input)
        X_train = tokenizer.texts_to_sequences(X_train)
        X_val = tokenizer.texts_to_sequences(X_val)
        X_test = tokenizer.texts_to_sequences(test_sentences)

        # Padding is done to equalize the lengths of all input tweets.
        # LTSM networks need all inputs to be same length.
        # Therefore, tweets lesser than max length will be made equal using extra zeros at end. This is padding.
        # Also, you always have to give a three-dimensional array as an input to your LSTM network
        X_train = sequence.pad_sequences(X_train, maxlen=len_max)
        X_val = sequence.pad_sequences(X_val, maxlen=len_max)
        X_test = sequence.pad_sequences(X_test, maxlen=len_max)

        # Early stopping to prevent overfitting deep learning neural network models
        # This is a method that allows you to specify an arbitrary large number of training epochs.
        # This stops training once the model performance stops improving on a hold out validation dataset
        early_stopping = EarlyStopping(min_delta = 0.001, mode = 'max', monitor = 'val_acc', patience = 2)
        callback = [early_stopping]

        # Create the model
        model = Sequential()
        model.add(Embedding(unique_words_count,300,input_length=len_max))
        model.add(LSTM(128,dropout=0.5,recurrent_dropout=0.5,return_sequences=True))
        model.add(LSTM(64,dropout=0.5,recurrent_dropout=0.5,return_sequences=False))
        model.add(Dense(100,activation='relu')) #try elu
        model.add(Dropout(0.5))
        model.add(Dense(num_classes,activation='softmax'))
        model.compile(optimizer=Adam(lr=0.005),
                      loss='categorical_crossentropy',
                      metrics=['acc'])
        model.summary()

        # Count of number of data points in each category
        hate_ct = y_train.sum(axis = 0)[0]
        offensive_ct = y_train.sum(axis = 0)[1]
        neither_ct = y_train.sum(axis = 0)[2]
        total_ct = y_train.sum()

        # Calculating the inverse ratio of each category to use for the weights of the model
        inv_ratio_hate = 1 - (hate_ct / total_ct)
        inv_ratio_hurtful = 1 - (offensive_ct / total_ct)
        inv_ratio_neither = 1 - (neither_ct / total_ct)

        # fit the model adjusting for epochs, batch, and weight
        model.fit(
            X_train, y_train,
            validation_data=(X_val,y_val),
            epochs=15, #may not run all due to callback
            batch_size=256, #faster with larger batch_size but it's generalizing
            verbose=1,
            callbacks=callback, #stops training once the model stops improving. Prevents overfitting.
            class_weight={0: inv_ratio_hate,
                          1: inv_ratio_hurtful,
                          2: inv_ratio_neither} #use inverse ratio to set hate with highest weight (somewhat arbitrary)
        )

        # Predict validation sentiment!
        y_pred = model.predict(X_val)

        # Keras and Sklearn read arrays differently
        # Create function to convert keras array to show only one highest sentiment result per list
        def keras_output_sklearn(y):
            result = []
            for element in y:
                result.append(np.argmax(element))
            return result

        # Saving model
        # date = datetime.datetime.now().strftime('%Y-%m-%d')
        model.save(f'models/LSTM_model.h5')

        # ## How did the Model Do?
        # Create count of the number of epochs
        epoch_count = range(1,len(model.history.history['loss']) + 1)

        # Visualize the learning curve.
        plt.plot(epoch_count,model.history.history['loss'],'r--')
        plt.plot(epoch_count,model.history.history['val_loss'],'b-')
        plt.legend(['Training Loss', 'Validation Loss'])
        plt.xlabel('Epoch')
        plt.ylabel('Loss')
        plt.title('Training vs Validation Loss')

        # save figure
        plt.savefig('training_eval/loss.png')

        # plt.show()

        # Use trained Keras model to predict test inputs and generate ROC data
        # Plot ROC for each of the 3 classes
        # Plot linewidth.
        lw = 2

        # 3 classes to classify
        n_classes = 3

        # Compute ROC curve and ROC area for each class
        fpr = dict()
        tpr = dict()
        roc_auc = dict()
        for i in range(n_classes):
            fpr[i], tpr[i], _ = roc_curve(y_val[:, i], y_pred[:, i])
            roc_auc[i] = auc(fpr[i], tpr[i])

        # Compute micro-average ROC curve and ROC area
        fpr["micro"], tpr["micro"], _ = roc_curve(y_val.ravel(), y_pred.ravel())
        roc_auc["micro"] = auc(fpr["micro"], tpr["micro"])

        # Compute macro-average ROC curve and ROC area

        # First aggregate all false positive rates
        all_fpr = np.unique(np.concatenate([fpr[i] for i in range(n_classes)]))

        # Then interpolate all ROC curves at this points
        mean_tpr = np.zeros_like(all_fpr)
        for i in range(n_classes):
            mean_tpr += interp(all_fpr, fpr[i], tpr[i])

        # Finally average it and compute AUC
        mean_tpr /= n_classes

        fpr["macro"] = all_fpr
        tpr["macro"] = mean_tpr
        roc_auc["macro"] = auc(fpr["macro"], tpr["macro"])

        # Plot all ROC curves
        plt.figure(1)
        plt.plot(fpr["micro"], tpr["micro"],
                 label='micro-average ROC curve (area = {0:0.2f})'
                       ''.format(roc_auc["micro"]),
                 color='deeppink', linestyle=':', linewidth=4)

        plt.plot(fpr["macro"], tpr["macro"],
                 label='macro-average ROC curve (area = {0:0.2f})'
                       ''.format(roc_auc["macro"]),
                 color='navy', linestyle=':', linewidth=4)

        colors = cycle(['aqua', 'darkorange', 'cornflowerblue'])
        for i, color in zip(range(n_classes), colors):
            plt.plot(fpr[i], tpr[i], color=color, lw=lw,
                     label='ROC curve of class {0} (area = {1:0.2f})'
                     ''.format(i, roc_auc[i]))

        plt.plot([0, 1], [0, 1], 'k--', lw=lw)
        plt.xlim([0.0, 1.0])
        plt.ylim([0.0, 1.05])
        plt.xlabel('False Positive Rate')
        plt.ylabel('True Positive Rate')
        plt.title('ROC multi-class')
        plt.legend(loc="lower right")

        # Save figure
        plt.savefig('training_eval/roc.png')

        # plt.show()

        # Use seaborn to see counts in percentages
        # Truth categories yield 100%
        confusion_matrix_t = confusion_matrix(keras_output_sklearn(y_val),keras_output_sklearn(y_pred))

        matrix_proportions = np.zeros((3,3))
        for i in range(0,3):
            matrix_proportions[i,:] = confusion_matrix_t[i,:]/float(confusion_matrix_t[i,:].sum())
        names=['Hate','Offensive','Neither']
        # save result as pandas df
        confusion_df = pd.DataFrame(matrix_proportions, index=names,columns=names)
        plt.figure(figsize=(5,5))
        seaborn.heatmap(confusion_df,annot=True,annot_kws={"size": 12},cmap='gist_gray_r',cbar=False, square=True,fmt='.2f')
        plt.ylabel(r'True categories',fontsize=14)
        plt.xlabel(r'Predicted categories',fontsize=14)
        plt.title('Confusion Matrix')
        plt.tick_params(labelsize=12)

        #Uncomment line below if you want to save the output
        plt.savefig('training_eval/confusion.png')

        # print(classification_report(keras_output_sklearn(y_val), keras_output_sklearn(y_pred)))


        # Upload to s3
        try:
            access_key = os.environ.get('AWS_ACCESS')
            secret_key = os.environ.get('AWS_SECRET_KEY')
            filepath = 'lstm_models/LSTM_model.h5'
            bucket_name ='retrained-models'
            folder_name = 'lstm_models'
            filename = "LSTM_model.h5"
            #have all the variables populated which are required below
            client = boto3.client('s3', aws_access_key_id=access_key,aws_secret_access_key=secret_key)
            transfer = S3Transfer(client)
            transfer.upload_file(filepath, bucket_name, folder_name+"/"+filename)
            print('**** S3 Upload Successful *****')
        except Exception as e:
            print('!!!!!!!! S3 Upload Failed !!!!!!!!')
            print(e)
            pass

        ####################################################################################################################################################
        '''     END   RETRAIN     BLOCK         '''
        ##########################################################################################################################################################

    else:
        print('****** No items have at least 3 votes.******')
        pass



else:
    print('****** Script Ended without retraining *****')
    pass
