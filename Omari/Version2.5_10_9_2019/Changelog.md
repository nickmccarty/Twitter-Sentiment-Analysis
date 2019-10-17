
# CHANGELOG

## V2.5 10/9/2019
#### Add feature - Dedicated API routes
  * Created dedicated Flask views for serving API & Erase Hate Python Library users. These routes serve predictions, and insert reclassed items into DB.

  * Files affected - `ModelServer/application.py`, `Main/application.py`

  * **Details/README's**
    * API Reclass Submission - Main  | `CHANGELOG.md` [link](https://github.com/oblockton/Erase-Hate-Versioning/blob/master/Version2.5_10_9_2019/Main/CHANGELOG.md 'API reclassification & TweepyMashup Update submission')

    * API Prediction - ModelServer | `CHANGELOG.md` [link](https://github.com/oblockton/Erase-Hate-Versioning/blob/master/Version2.5_10_9_2019/ModelServer/CHANGELOG.md 'ModelServer API prediction')

* **Requirements.txt update to use tweepymashup v1.0.7 `tweepymashup=1.0.7`**
      - no code changes were made to files importing tweepymashup


## V2
#### Add feature - Retraining
  * Added retraining script. New item & original training data combined into a new dataset, based on certain rules. If all criteria/rules pass, retraining takes place. New model is uploaded to S3 for use by the model server.

  * Files affected - `ModelServer/application.py`, files added - `Vote_Retrain/retrain.py`

  * **Details/README's**
    * Retrain script overview - Vote Retrain | `retrain_README.md` [link](https://github.com/oblockton/Erase-Hate-Versioning/blob/master/Version2_9_26_2019/Vote_Retrain/retrain_README.md 'Retraining Script README')

    * Model Server changes  - ModelServer| `Changelog.md` [link](https://github.com/oblockton/Erase-Hate-Versioning/blob/master/Version2_9_26_2019/ModelServer/Changelog.md 'ModelServer Changelog')

## V1.5
#### Add feature - Reclassification
  * A max of 5 'hate' items from a users search are made available for reclassification.
  * Reclassified items stored in DB.
  * Python voting script added to assign the final class for use in retraining.
  * **Details/README's**
    * Front-End changes in Application.py | `Main/reclass_readme.md` [link](https://github.com/oblockton/Erase-Hate-Versioning/blob/master/Version1.5_9_8_2019/Main/reclass_readme.md 'Reclass Submit README')
    * Voting in reclass_voting.py | `Vote_Retrain/voting_README.md` [link](https://github.com/oblockton/Erase-Hate-Versioning/blob/master/Version1.5_9_8_2019/Vote_Retrain/voting_README.md 'Voting Script README')

#### Add feature - Multi-Auth/API switching.
  * Add ability to switch tweepy AUTH Handler as ratelimit approaches.
  * Layers on top of Original lock and 'wait_on_rate_limit' feature.
    * Multi-Auth built by combining the lastet Tweepy verison 3.8.0, with NIRG's tweepy fork for multi-auth switching.
    * Create PIP module for use in AWS front-end environment build.
      * pip install tweepy-mashup
  * **Details/README's**
    * Multi-Auth changes in application.py | `Main/multi_auth_rate_README.md` [link](https://github.com/oblockton/Erase-Hate-Versioning/blob/master/Version1.5_9_8_2019/Main/multi_auth_rate_README.md 'Auth & Rate Limit README')

#### Minor code change
  * Modelserver response/output now includes LSTM prediction array. Used in reclass feature.


### V 1

* Original version. Features:

  * Classify text, tweet user timeline, tweet keyword/topic search results.
  * Provide total items classed, counts for each applicable class, and percentage of total items.
  * Lock tweepy search use on any tweepy error not related to search results. Basic catchall for rate limit errors.
