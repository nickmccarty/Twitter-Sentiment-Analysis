import pandas as pd
import datetime
import mysql.connector
from mysql.connector import Error,errorcode
import joblib
from sqlalchemy import create_engine

#################################
'''   Runners '''
#################################

## Setup the connection config in dict form
config = {
    'user':'root',
    'password': 'Heata4321.',
    'host':'localhost',
    'database':'appdb',
    'raise_on_warnings': True
}

#Query the database for the last row/Max(id). This is most recent entry.
# Compare this to the most recent text value stored in a pickle file.
def query_recent(**config):
    cnx = mysql.connector.connect(**config)
    c = cnx.cursor()
    c.execute(f"USE {config['database']}")
    print(f"****** USING DB: {config['database']} *******")
    # Query for the last item entered. Limit result to only that 1 row
    reclassed_query = """SELECT * from reclassed ORDER BY id DESC LIMIT 1;"""
    c.execute(reclassed_query)
    # Take the single result and save the id to a variable for pickling.
    recent_entry = c.fetchall()[0][0]
    c.close()
    cnx.close()
    return recent_entry

# Check if the current last row/max(of id) id is the same as the last time we voted.
# If same no new items reclassed. Don't continue to vote.
def there_r_newitems(currentquery,lastpickle):
    if currentquery != lastpickle:
        print('******* Yes there are new items *******')
        return True
    else:
        print('***** There are no new items *******')
        return True  #   !!!!!!!!!!!!!#@@@@@@@@@@@%%%%%%%%%% change to false for final


#Query the database for all items.
def query_all(**config):
    cnx = mysql.connector.connect(**config)
    c = cnx.cursor()
    c.execute(f"USE {config['database']}")
    print(f"****** USING DB: {config['database']} *******")
    # Query for the last item entered. Limit result to only that 1 row
    reclassed_query = """SELECT * from reclassed;"""
    c.execute(reclassed_query)
    # Take the single result and save the id to a variable for pickling.
    recent_entry = c.fetchall()
    c.close()
    cnx.close()
    return recent_entry

#Create a Dataframe of the query results. This DF will be used to group and count.
def pandarize(queryresult):

    df = pd.DataFrame(queryresult)
    df = df.rename(columns={1:'date',2:'text',3:'class'})
    # drop old index
    df = df.drop([0],axis=1).copy()
    return df

#iterate through groups of text entries. All text in a group
#will have the same text but different classes. Acquire count of each class,
# which equals the count for each class.
def vote(groupby_obj):
# Create list to store the new vote tallies and final class determination.
    voted_items = []
    for group in groupby_obj:
        # create dict to store tally for the current group.
        item_dict = {}
         # add a date record
        item_dict['date voted'] = datetime.datetime.now().strftime('%Y-%m-%d')
        # Dataframe the series returned for the individual group. [0] =column names [1]=series
        text_set = pd.DataFrame(group[1])
        # Current index of the group[1] series has index number from its index in the original dataframe 'df'
        #Recreate the index in the new dataframe so we can index by position in list.
        text_set= text_set.reset_index()
        # Store text string for this group by using first result/[0]
        item_dict['text'] = text_set['text'][0]
        # Take individual like-text group and group by the class value.
        # The count of entries in a class group is the totalvotes for that class.
        textset_votes = pd.DataFrame(text_set.groupby('class').count())
        # Store class votes. Class is now the true index.
        # The row containg the count for a specific class, has an index in the series that is its class
        # [0]=hate [1]=hurtful [2]=neither
        # the acutal count is given in the column values.
        #          index  0  date  text
        # class
        # 0          3  3     3     3
        # 1          1  1     1     1
        # convert to DF , series are ass.

        #If the dataframe of class count(textset_votes) has a sum of votes for any class(has a row(s))
        # the index number of that row is the class, the value in that row is the count of votes.
        # add that count to the tally{item_dict} for current group in iteration.
        # If none , tally record 0 votes.
        try:
            item_dict['hate'] = textset_votes['text'][0]
        except:
            item_dict['hate'] = 0
        try:
            item_dict['hurt'] = textset_votes['text'][1]
        except:
            item_dict['hurt'] = 0
        try:
            item_dict['neither'] = textset_votes['text'][2]
        except:
            item_dict['neither'] = 0

        # Calculate totalvotes
        item_dict['totalvotes'] = item_dict['hate'] + item_dict['hurt'] + item_dict['neither']

        # Create list of vote counts, to find max. If any one index in the list is greater,
        # than the sum of the remaining items, then the decision is a majority win of total vote.
        # if not majority win, use absolute max of count for each class.

        # Create list of totals. or matches index.class order in the df item_dict
        votelist = [item_dict['hate'] , item_dict['hurt'] , item_dict['neither']]
        # Function to determine if any class has a total vote count > sum(votes for remaining class)
        def is_unanimous(votelist):
            maxcount = max(votelist)
    #         print(maxcount)
            if maxcount >= (sum(votelist)-maxcount):
                return votelist.index(maxcount)
            else:
                return False
        # If there is a majority win ,record that class as the voted final class
        if is_unanimous(votelist) is not False:

          item_dict['votedclass'] = is_unanimous(votelist)
        # If no majority win, take max of the 3 classes. The index of that max value is its' class
        elif is_unanimous(votelist) is False:
          # Check if there is a tie for max value in the vote count list
          print('!!!!!! handling tie !!!!')
          print(f"**** List of votes : {votelist} *******")
          print(f'*** Max count in list is: {max(votelist)}')
          max_index =votelist.index(max(votelist))
          print(f'****** Max counts index is: {max_index} ******' )
          # Create list with the max count value removed, then check if any remaining values match.
#           without_max = []
          without_max = [votelist[x] for  x in range(len(votelist)) if max_index != x]

#           for x in range(len(votelist)):
#               print("current iter values' index", x)
#               print(max_index)
#               if max_index != x:
#                   without_max.append(votelist[x])
#               else:
#                   continue
          print(f'**** The list without max : {without_max}')
          if max(votelist) not in without_max:
              # If no tie exist then the class list is the index of the max value
              item_dict['votedclass'] = votelist.index(max(votelist))
          else:
              print(f'*** Yes there was a tie for max val: {max(votelist)} | no decision made ****')
              item_dict['votedclass'] = 777
          # 777 is the value entered for no class decision. remains an int so column tpye can stay as int type.



            #     add to tally
        voted_items.append(item_dict)
    return voted_items

# Inser voted items into database
def insert_voted(config, dataframe):

    engine = create_engine(f"mysql+mysqlconnector://{config['user']}:{config['password']}@{config['host']}:3306/{config['database']}", echo=False)
    dataframe.to_sql(name='vote_classed', con=engine, if_exists = 'replace', index=False)

###################################
#'''   End Runners        '''
########################################


#######################################################################################################
'''    Run the functions as script   '''
 ###################################################################################################
recent_entry = query_recent(**config)
print ('****** This is the most recent entry in this session: ' + str(recent_entry))
# joblib.dump(recent_entry, 'recent_entry.pkl') <<<<<<<<<<<<__________uncomment to re seed the comparison procedure.run only to this line.
compare_recent_to = joblib.load('recent_entry.pkl')
print('****** This is the most recent pickled entry from prior session' + str(compare_recent_to))
print('****** Checking if voting needed *****')
if there_r_newitems(recent_entry,compare_recent_to):
    ####################################################################################################################################################
    '''                VOTE BLOCK        '''
    ##########################################################################################################################################################
    print('******** Confirmed - Vote required - START VOTING ******** ')
    # Save results of db query for all items unvoted.
    results = query_all(**config)
    # print(results)

    # Create groups of like-text.
    df_counting = (pandarize(results).groupby('text'))
    # Vote on all items ,save as df, insert into database
    voted_items = pd.DataFrame(vote(df_counting))
    insert_voted(config,voted_items)
    print( ' **** Items Successfully inserted ****** ')


    ####################################################################################################################################################
    '''     END   VOTE     BLOCK         '''
    ##########################################################################################################################################################

else:
    print('!!!!! NO REVOTE NEEDED, NO NEW ITEMS - CLOSING !!!!!!!!')
    pass

joblib.dump(recent_entry, 'recent_entry.pkl')  #pickle id from this session.
