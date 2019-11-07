# Changes in V3.0


## Changes to `application.py`

### Ability to reclassify items from any predicted class

  The process of building the form has been moved out the main Flask file `application.py`. The functions used to create the reclassification form now reside in `form_builder.py`.

### Search form and Twitter response validation coverage

  Add coverage for Twitter 401 errors, or submitting the initial search form without an input in the text field.  

## File addition `form_builder.py`
  This file contains the functions used to determine how and with which content to build the reclassification form with. If no items were predicted to be hate, now users may reclassify those items classified as hurtful/offensive. If no offensive items exist in the classification, then users may classify the 'harmless' items. Because the result parsing if different for each model(the model outputs are different format), there are separate functions to build the reclassification form.

  * `build_form_options_log()` - This is the function to build the form when classification was executed with the Logistic regression model.

  * `build_form_options_lstm()` - This is the function to build the form when classification was executed with the Long Short Term Memory model.




---
