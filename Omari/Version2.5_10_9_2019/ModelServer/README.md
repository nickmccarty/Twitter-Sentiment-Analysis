# - ModelServer <---folder
    - contains the files necessary for serving ONLY the LSTM model.

### application.py  
    - Main FLask/WSGI file file. All functions to serve predictions, respond to requests, and Flask routes/views reside There

### utils.py
    - Contains runner functions used to clean/parse text input. Some of these functions are used in/by certain vectorizers. The method of pickling requires these functions to be stored externally( with an accompanying init.py). 
