# Vote_Retrain <--folder
    - contains all files/scripts to handle voting on user reclassified items and retraining operations.


###  reclass_voting.py
    - Script to vote on the final class, for items reclassed by users.
    - See `voting_README.md`

### retrain.py
    - Script that handles the creation of the new dataset(original data + user reclassed items), lstm model retraining, AWS model uploading.
    - See  `retrain_README.md`
