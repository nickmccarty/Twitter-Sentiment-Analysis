# Retraining Feature Operation

* Voting script runs on schedule every day @ 9pm PST/UTC -8hrs

* Purpose of retraining is to retrain the LSTM model, using items that were re-classed by the users in addition to the original training data.

* The table `vote_classed` contains the reclassed items and their respective votes.

* Retraining only happens if when there are new items in the database, these items have at least 3 votes/voters, and there are at least 10 items that have 3 votes each. Setting a threshold of 10 items prevents unnecessary retraining, retraining on a few item is unlikely to impact the models prediction ability. Only retraining on items with at least 3 voters is to avoid items with only 1 voter influencing the model.

* Only those items with 3 votes are used in the retraining. These items are combined with the original training data to create the new dataset.

## Process Overview

* Determine if there are new items. An update key was stored if/when vote took place and items were inserted into the `vote_classed` table.

> Update key Loading
~~~~
update_key = joblib.load('update_key.pkl')
~~~~

>  In function `there_r_newitems()` we check the update key.
~~~~
if update_key == 'updated':
      print('******* Yes there are new items *******')
      return True
  else:
      print('***** There are no new items *******')
      return False
~~~~

* If new items do exist. Query the database for all items. Locate any items with total of 3 votes, store those items as variable `voted_items`. Then retrain if at least 10 items have at least 3 votes each.
    > If there_r_newitems() returned True. Determine which items meet the threshold.
    ~~~~
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
    ~~~~

* Query database for original data. Create dataframe of original data. Combine original and new (3 vote)items into one dataframe. Then begin retraining.
  ~~~~
  print('******** Confirmed - Retrain required - START RETRAIN ******** ')
      original_data = pandarize_original(query_original(**config))
      all_data = voted_items.append(original_data, sort = False)
  ~~~~




### S3 Upload , post-retraining.

* Once retraining has completed. Upload the new model to s3 bucket.

* s3 bucket is version enabled. Uploading the same file name will trigger AWS to assign a version ID to file. Allows one to retrieve prior versions, non-overwriting method.

* Only the most recent version is served to clients requesting the model file(aka the model server `application.py` script), unless an older version is explicitly specified.

    > Uploading to S3 bucket.
    ~~~~
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
    ~~~~
