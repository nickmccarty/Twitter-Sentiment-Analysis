# Changes to `application.py`

## Switch to loading lstm_model.h5 from the s3 bucket.

  * The most recently trained model exist in s3. No model file is furthermore loaded onto the instance when deploy. The model file is retrieved from s3.

  > Downloading the s3 stored model file.
  ~~~~
  access_key = ''
  secret_key = ''
  bucket_name ='retrained-models'
  folder_name = 'lstm_models'
  filename = "LSTM_model.h5"
  s3_file_path= folder_name+'/'+filename


  s3 = boto3.client('s3',aws_access_key_id=access_key,aws_secret_access_key=secret_key)
  s3.download_file(bucket_name , s3_file_path, filename)
  ~~~~


## Add Boto3 dependencies to requirements.txt
  * `boto3==1.9.236, botocore==1.12.236, docutils==0.15.2, jmespath==0.9.4, s3transfer==0.2.1`
