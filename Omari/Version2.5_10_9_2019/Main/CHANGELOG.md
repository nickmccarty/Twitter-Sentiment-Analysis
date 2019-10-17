# Changes to `application.py`

## Addition of dedicated API reclassification route. /api_reclass_submit, methods = ['POST']

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

   > Error response format. A dictionary with keys 'api_code' & 'message'
   ~~~~
   {
     api_code: code,
     message: error message
    }
   ~~~~

**See api_README for complete api error details** [API INFO](https://github.com/oblockton/Erase-Hate-Versioning/blob/master/Version2.5_10_9_2019/Main/api_README.md 'API Error codes and messages')

  > Error handling with api_code in return statement and appropriate message.
  ~~~~
  try:
                cnx = mysql.connector.connect(**config)
                c = cnx.cursor()
                enter_items_api(reclass_input,c,cnx)
                cnx.close()
                print( '**** Reclass submit successful -API SUBMIT REQUEST ****' )
                return jsonify({'api_code':200, 'message':'successful' })

            # Error handling for mysql connector errors.
            except mysql.connector.Error as err:
                if (err.errno == errorcode.ER_ACCESS_DENIED_ERROR):
                     print("!!!! Something is wrong with your user name or password- API SUBMIT REQUEST !!!!")
                     print(str(err))
                     cnx.close()
                     return jsonify({ 'api_code':403, 'message':'ACCESS DENIED: {}'.format(err) })
                elif (err.errno == errorcode.ER_BAD_DB_ERROR):
                    print("!!! Database does not exist - API SUBMIT REQUEST !!!")
                    print(str(err))
                    cnx.close()
                    return jsonify({ 'api_code':404, 'message':'BAD_DB_ERROR: {}'.format(err) })

                # Table entry error. Occurs if non-int entered for classlabel. However this should be caught by the value error.
                elif err.errno == 1366:
                    print(' SQL connector err - Table entry - likely not integer - API SUBMIT REQUEST')
                    print(str(err))
                    cnx.close()
                    return jsonify({ 'api_code':500, 'message':'DB insert Unsuccessful-Likely Expected integer for class label: {}'.format(str(err)) })
  ~~~~

## TweepyMashup Updated to 1.0.7

  * No code changes made to `application.py`. However , note the update.


---
