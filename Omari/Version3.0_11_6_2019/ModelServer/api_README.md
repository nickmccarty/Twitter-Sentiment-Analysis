# API - api codes and error messages
---

`api_receiver` Is the route that accepts API request for classification service. This route will return error codes an error message to help in debugging any issues. The main points at which an error will occur will be during validation of the POST request data.

* API codes have been added as such:
 - 200 = Successful
 - 500 = Failed. Code error, SQL insert error, or any other exceptions.
 
 - Error messages are returned to the client with more specific info.

**Post data must be a list of strings**


###  Data sent, not a list

  `if isinstance(input,list):`
  on failure:
  `return jsonify({ 'api_code':500, 'message':"Model Server Error, TypeError: prediction input not a list. Proper input ['text','text','text','text']" })
`

  **API error code**: 500.
  **Message**: Model Server Error, TypeError: prediction input not a list. Proper input ['text','text','text','text']

### Items in list not strings

  `if all(isinstance(item,str) for item in input):`
  on failure:
  `return jsonify({ 'api_code':500, 'message':"Model Server Error, TypeError: one or more items in prediction input not string type.Proper input ['text','text','text','text']" })`

  **API error code**: 500.
  **Message**:Model Server Error, TypeError: one or more items in prediction input not string type.Proper input ['text','text','text','text']
