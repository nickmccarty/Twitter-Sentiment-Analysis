# Main <--folder
    - contains all files for front end, twiiter handling, & LogRegress Model predictions


### .ebextensions
    - Custom config instructions for AWS deployment

### Application.py
    - Contains the core front end code. All routes/views resides here

### model.py
    - Contains code for the Log Regress model prediction.

### utils.py
    - Runner functions used to clean & parse input for prediction. Some of these functions are used in/by the TFIDF vectorizer & POS tag vectorizer. The method of pickling requires these functions to be stored externally( with an accompanying init.py).
