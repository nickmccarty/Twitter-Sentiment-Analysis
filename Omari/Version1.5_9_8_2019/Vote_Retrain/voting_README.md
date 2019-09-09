# Voting Feature Operation

* Voting script runs on schedule every day @ 8pm PST/UTC -8hrs

* Purpose of voting is to determine the final class to assign to items that were reclassed by the users. This final class is used in the retraining process.

* The items voted and assigned a final class are then entered into a new table.

* Voting only happens if when there are new items in the database .

* Determine if there are new items. Select the id of the last row aka max(id) of the table entries.
    > In `query_recent()`
    ~~~~
    reclassed_query = """SELECT * from tablename ORDER BY id DESC LIMIT 1;"""
    ~~~~

* Seed the script with a ID to compare to. Once seeded, the cycle continues by saving the id of the last row in the table, every time this file runs, regardless if a vote was taken.
    > Comparing recent items. Comparison function is `there_r_newitems()`, a boolean.
    ~~~~
    recent_entry = query_recent(**config)
    print ('****** This is the most recent entry in this session: ' + str(recent_entry))

    # joblib.dump(recent_entry, 'recent_entry.pkl') <<<<<<<<<<<<__________uncomment to re seed the comparison procedure.run only to this line.

    compare_recent_to = joblib.load('recent_entry.pkl')
    print('****** This is the most recent pickled entry from prior session' + str(compare_recent_to))
    print('****** Checking if voting needed *****')
    if there_r_newitems(recent_entry,compare_recent_to):
    ~~~~

* If new items exits, take a vote. If none new, save the last row id and exit.
      > Saving last row it
      `joblib.dump(recent_entry, 'recent_entry.pkl')  #pickle id from this session.`



### Take a vote.

* `SELECT * ` from the table.
* The table of reclassed items can/will have items that have been reclassed multiple time.
* Group by text, then group by class. This will give the total votes for each class, if that text was classed multiple times.
        > Iterate through each group
        `voted_items = []
          for group in groupby_obj:`

* Vote schema:
    *  Find if there is a majority winner - if any single class has more votes than the sum of the remaining two.
        * If no majority, take the class with max vote count.
          * Toss out any ties for max value.
* While iterating add the calculated data to a dictionary for each item being voted on. Add these objects to a List.

        > Resulting list `voted_items`, should contain no duplicate.
        ~~~~
        [
          {
            date:datetime,
            hate: int,
            hurt:int,
            neither:int,
            text:string,
            total votes: int,
            class: int            
          },
          {
            date:datetime2,
            hate: int,
            hurt:int,
            neither:int,
            text:string2,
            total votes: int,
            class: int            
          },
        ]
        ~~~~

* Make a DF from `voted_items`, insert into new table for only voted items. Using SQLAlchemy `to_sql()`. Replace prior table if exists.
