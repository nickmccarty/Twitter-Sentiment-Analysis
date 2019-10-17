# API - api codes and error messages
---

## Dedicated API reclassification route. /api_reclass_submit, methods = ['POST']

  * A separate route has been added to ingest reclassified item. For the most part the route is the same as the route which serves the webpage, however the data parse, outputs and internal print statement have been adjusted to demark API usage, and better serve Erase Hate Python Library users. Return statements now return a response as opposed to render_template(as would happen for the web page.)

  * This new route accepts a list of lists as such.:
  `[['class label', 'text/tweet'], ['classlabel', 'text2/tweet2'], ['classlabel', 'text3/tweet3']]`
      - **Any reclassification form parsing must be completed by the user, using custom code or the Erase Hate Python Library prior to posting to this route.**

   - With the input being different from the route that serves the webpage, a new sql input helper function has been created. `enter_items_api`

  * API codes have been added as such:
   - 200 = Successful
   - 500 = Failed. Code error, SQL insert error, or any other exceptions.
   - 403 = ACCESS DENIED -SQL Err - authentication
   - 404 = BAD_DB_ERROR - SQL selected database nonexistent

   - Error messages are returned to the client with more specific info.

 **Errors will generally occur in two areas. At validation of POST data, or at SQL insert.**
  - However, since data is validated before SQL insertion is attempted, SQL error should generally not occur.
---
##  Validating data in post request.
  Data sent in post request is validated before any SQL insert is attempted. If validation fails, api error codes and message are also returned in the request response.

### POST data not a list
`if isinstance(reclass_input,list):`
> On failure
  `return jsonify({'api_code':500, 'message':'DB insert Unsuccessful. TypeError: data input must be a list.[ [classlabel, text] ] or [ (classlabel,text) ]'})`

**API code**: 500
**Message**: DB insert Unsuccessful. TypeError: data input must be a list.[ [classlabel, text] ] or [ (classlabel,text) ]

### POST data list items , not a list. Post data must be list of lists or list of tuples.
`if all(isinstance(item,(list,tuple)) for item in reclass_input):`
> On failure
  `                return jsonify({'api_code':500, 'message':'DB insert Unsuccessful. TypeError: data input must be a list of lists or tuples.[ [classlabel, text] ] or [ (classlabel,text) ]'})`

**API code**: 500
**Message** : DB insert Unsuccessful. TypeError: data input must be a list of lists or tuples.[ [classlabel, text] ] or [ (classlabel,text) ]

### Class labels not 0,1,or 2
The post data should have the class labels at the first index as such:
`[['class label', 'text/tweet'], ['classlabel', 'text2/tweet2'], ['classlabel', 'text3/tweet3']]`
We check that index to validate if it is a 0,1, or 2.

`if all(str(item[0])=='0' or str(item[0])=='1' or str(item[0])=='2' for item in reclass_input ):`
> On failure
  ` return jsonify({'api_code':500, 'message':'DB insert Unsuccessful. Class labels must be 0, 1, or 2. Integer or string.[ [classlabel, text] ] or [ (classlabel,text) ]. 0 =hate, 1 =offensive, 2 =neither'})`

**API code**: 500
**Message**: DB insert Unsuccessful. Class labels must be 0, 1, or 2. Integer or string.[ [classlabel, text] ] or [ (classlabel,text) ]. 0 =hate, 1 =offensive, 2 =neither

---
## SQL & mysqlconnector specific error handling

### SQL Access Denied

This error generally should not occur as the config of sql is handled on the server. This error could occur during a sql injection attempt.
`except mysql.connector.Error as err:`

`if (err.errno == errorcode.ER_ACCESS_DENIED_ERROR):
                 print("!!!! Something is wrong with your user name or password- API SUBMIT REQUEST !!!!")
                 print(str(err))
                 cnx.close()
                 return jsonify({ 'api_code':403, 'message':'ACCESS DENIED: {}'.format(err) })`

**API code**: 403
**Message**: ACCESS DENIED: verbose error details passed  on to user.

### Bad DB error

This error generally should not occur as the config of sql is handled on the server. This error could occur during a SQL injection attempt.
`except mysql.connector.Error as err:`

`elif (err.errno == errorcode.ER_BAD_DB_ERROR):
                print("!!! Database does not exist - API SUBMIT REQUEST !!!")
                print(str(err))
                cnx.close()
                return jsonify({ 'api_code':404, 'message':'BAD_DB_ERROR: {}'.format(err) })`

**API code**: 404
**Message**: BAD_DB_ERROR: verbose error details passed on to user.

### Inserting a string into a SQL column, which only accepts integers.

This error should not occur. Users may input class labels and text as a string or integer format. Before SQL insertion is attempted, the input is cast as the appropriate data type. If the input cannot be cast as an integer, such as the string 'two'. A ValueError will be raised. However is a table input error occurs and is uncaught by ValueError, SQL will raise a 1366 error code.
`except mysql.connector.Error as err:`

`elif err.errno == 1366:
                print(' SQL connector err - Table entry - likely not integer - API SUBMIT REQUEST')
                print(str(err))
                cnx.close()
                return jsonify({ 'api_code':500, 'message':'DB insert Unsuccessful-Likely Expected integer for class label: {}'.format(str(err)) })`

**API code**: 500
**Message**: DB insert Unsuccessful-Likely Expected integer for class label:pass on verbose error message from SQL.

### Uncaught SQL specific errors

Uncaught SQL errors.

`except mysql.connector.Error as err:`
`else:
                print('Some other SQL error occured - API SUBMIT REQUEST')
                print(str(err))
                cnx.close()
                return jsonify({ 'api_code':500, 'message':'DB insert Unsuccessful at SQL Exception-else: {}'.format(str(err)) })`

**API code**: 500
**Message**: DB insert Unsuccessful at SQL Exception-else: verbose error message from SQL passed to user.

### Error casting class label as input as integer.

To ensure the API continues on a Python casting error and eventually return an error message to the end user, we must first catch the ValueError specifically within the `enter_items()` function.

> Here we catch the casting error, then re raise the ValueError with our own message that will be passed onto the user. This initial catching happens in the enter_items() function which is the function that handles the table insertion.

~~~~
except ValueError as err:
        # Check if error casting a string format classlabel, as integer for table input.Ex: casting string 'one' as int raises value error.
        # Table only accepts int.
        if str(err)[:23] == 'invalid literal for int':
            print("!!!! Error at item insert into table SQL - Class Label input can't be cast as int() i.e 'six' not allowed: {}".format(err))
            connector.close()
            # Raise a ValueError to be caught later.
            raise ValueError('int cast classlabel')
        else:
            print('!!!! Error at item insert into table SQL - Not Class label casting : {}'.format(err))
            raise ValueError(err)
~~~~~

Now that we have caught re- raised the ValueError with a custom error message that identifies the value error as a casting error, we can catch and pass on to the user a more specific error message as it applies to their data input. We will also pass on a different message if the error was not a class label casting issue.

~~~~~
except ValueError as valerr:
              if str(valerr) == 'int cast classlabel':
                  print('!!! enter_items_api() Passed Value Error . integer.at table insert.Class label')
                  cnx.close()
                  return jsonify({ 'api_code':500, 'message':'DB insert Unsuccessful at index [0] of your data, Classlabel, expected single digit integer or a single number in string format: passed from enter_items_api() :{}'.format(str(valerr)) })
              else:
                  print('!!! enter_items_api() Passed Value Error .NOT  integer error: verbose {}'.format(valerr))
                  cnx.close()
                  return jsonify({ 'api_code':500, 'message':'DB insert Unsuccessful:Uncaught Value error at table entry. check input types. verbose: {}'.format(str(valerr)) })
~~~~~

* If error was an issue casting class label to integer:
**API code**: 500
**Message**: DB insert Unsuccessful at index [0] of your data, Classlabel, expected single digit integer or a single number in string format: passed from enter_items_api() :verbose :error message from python.

* If some other error casting a data type to the correct type for SQL insertion:
**API code**:500
**Message**: DB insert Unsuccessful: Uncaught Value error at table entry. check input types. verbose: error message from python
---

### Uncaught exception- any other issue with reclassed item submission process.

Error if any other error occurs that isn't caught.

`except Exception as e :
              print('!!!! Error in Reclass Submisson - Not a SQL error - API SUBMIT REQUEST !!!!')
              print('Error: {}'.format(e))
              cnx.close()
              return jsonify({'api_code':500, 'message':'DB insert Unsuccessful . Uncaught Server Exception: {}'.format(e)})`

**API code**: 500
**Message**: DB insert Unsuccessful . Uncaught Server Exception: verbose python error message passed on to user
