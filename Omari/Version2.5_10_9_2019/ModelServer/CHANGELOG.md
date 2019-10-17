# Changes to `application.py`

## Addition of dedicated API prediction route. /api_receiver, methods = ['POST']

  * A separate route has been added to serve API predictions. For the most part the route is the same as the route which serves the webpage, however the outputs and internal print statement have been adjusted to demark API usage, and better serve Erase Hate Python Library users.

  * API codes have been added as such:
   - 200 = Successful
   - 500 = Failed. Code error, SQL insert error, or any other exceptions.
   
   - Error messages are returned to the client with more specific info.

  > A api code has been added to the output of successful predictions. This allows api users an easy method of catching success/failure of their prediction requests.  This is the output of a successful prediction request/
  ~~~~
  results = { 'api_code':200,
                'prediction_array': prediction_prob.tolist(),
                'hate_data':{'count':hate,
                            'percentTotal':int((hate/(hate+hurtful+neither))*100)},
                'hurt_data':{'count':hurtful,
                            'percentTotal':int((hurtful/(hate+hurtful+neither))*100)},
                'neither_data':{'count':neither,
                                'percentTotal':int((neither/(hate+hurtful+neither))*100)},
                'total_count':hate+hurtful+neither
  ~~~~

  > This is the output for a failed requests
  ~~~~
  return jsonify({'api_code':500,'message':'Model Server Error'})
  ~~~~


 * Data sent in POST request is validated for correct format. Must be a list of string. If not API error code and message sent in a response to the user.
---
