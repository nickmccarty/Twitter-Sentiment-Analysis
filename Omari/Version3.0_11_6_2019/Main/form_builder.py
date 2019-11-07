import numpy as np

""" Function to build the reclassification form. If hate resuslts were predicted, user will reclassify hateeful tweets. If no hate results returned, users may
 reclassify the hurtful tweets. If neither hate nor hurtful tweets were returned, users may reclassify the harmless tweets."""




def build_form_options_log(tweets_dict,results, reclass_text_strings):
    if results['hate_data']['count'] > 0:
        to_reclass =[(tweets_dict['text'][i],results['prediction_array'][i],f'ITEM {str(i)}') for i in range(len(tweets_dict['text'])) if (int(results['prediction_array'][i]) == 0)]
        if len(to_reclass)> 5:
            to_reclass = to_reclass[:5]
        print('***** List of hateful items avail to reclass ******')
        print(to_reclass[:5])
        print('***** END RECLASS SNIPPET ******')
        # Build reclass form with hate tweets if hate tweets were returned.
        form_opt_data = [reclass_text_strings['hate']['h1'],reclass_text_strings['hate']['span'],reclass_text_strings['hate']['delimit'],reclass_text_strings['no_change'],
                        reclass_text_strings['hurt']['delimit'],reclass_text_strings['hurt']['form_opt'],reclass_text_strings['neither']['delimit'],reclass_text_strings['neither']['form_opt']]
        return {'reclass_texts':to_reclass,'form':form_opt_data}
    elif results['hurt_data']['count'] > 0:
        to_reclass =[(tweets_dict['text'][i],results['prediction_array'][i],f'ITEM {str(i)}') for i in range(len(tweets_dict['text'])) if (int(results['prediction_array'][i]) == 1)]
        if len(to_reclass)> 5:
            to_reclass = to_reclass[:5]
        print('***** List of hurtfull items avail to reclass ******')
        print(to_reclass[:5])
        print('***** END RECLASS SNIPPET ******')
        # Build reclass form with hurtful tweets IF no hate tweets were returned.
        form_opt_data = [reclass_text_strings['hurt']['h1'],reclass_text_strings['hurt']['span'],reclass_text_strings['hurt']['delimit'],reclass_text_strings['no_change'],
                        reclass_text_strings['hate']['delimit'],reclass_text_strings['hate']['form_opt'],reclass_text_strings['neither']['delimit'],reclass_text_strings['neither']['form_opt']]

        return {'reclass_texts':to_reclass,'form':form_opt_data}
    else:
        to_reclass =[(tweets_dict['text'][i],results['prediction_array'][i],f'ITEM {str(i)}') for i in range(len(tweets_dict['text'])) if (int(results['prediction_array'][i]) == 2)]
        if len(to_reclass)> 5:
            to_reclass = to_reclass[:5]
        print('***** List of hurtfull items avail to reclass ******')
        print(to_reclass[:5])
        print('***** END RECLASS SNIPPET ******')
        # Build reclass form with hate tweets if hate tweets were returned.
        form_opt_data = [reclass_text_strings['neither']['h1'],reclass_text_strings['neither']['span'],reclass_text_strings['neither']['delimit'],reclass_text_strings['no_change'],
                        reclass_text_strings['hurt']['delimit'],reclass_text_strings['hurt']['form_opt'],reclass_text_strings['hate']['delimit'],reclass_text_strings['hate']['form_opt']]
        return {'reclass_texts':to_reclass,'form':form_opt_data}






def build_form_options_lstm(tweets_dict,results,reclass_text_strings):
    if results['hate_data']['count'] > 0:
        to_reclass =[(tweets_dict['text'][i],np.argmax(results['prediction_array'][i]),f'ITEM {str(i)}') for i in range(len(tweets_dict['text'])) if int(np.argmax(results['prediction_array'][i]) == 0)]
        if len(to_reclass)> 5:
            to_reclass = to_reclass[:5]
        print('***** List of hateful items avail to reclass ******')
        print(to_reclass[:5])
        print('***** END RECLASS SNIPPET ******')
        # Build reclass form with hate tweets if hate tweets were returned.
        form_opt_data = [reclass_text_strings['hate']['h1'],reclass_text_strings['hate']['span'],reclass_text_strings['hate']['delimit'],reclass_text_strings['no_change'],
                        reclass_text_strings['hurt']['delimit'],reclass_text_strings['hurt']['form_opt'],reclass_text_strings['neither']['delimit'],reclass_text_strings['neither']['form_opt']]
        return {'reclass_texts':to_reclass,'form':form_opt_data}
    elif results['hurt_data']['count'] > 0:
        to_reclass =[(tweets_dict['text'][i],np.argmax(results['prediction_array'][i]),f'ITEM {str(i)}') for i in range(len(tweets_dict['text'])) if int(np.argmax(results['prediction_array'][i]) == 1)]
        if len(to_reclass)> 5:
            to_reclass = to_reclass[:5]
        print('***** List of hateful items avail to reclass ******')
        print(to_reclass[:5])
        print('***** END RECLASS SNIPPET ******')
        # Build reclass form with hurtful tweets IF no hate tweets were returned.
        form_opt_data = [reclass_text_strings['hurt']['h1'],reclass_text_strings['hurt']['span'],reclass_text_strings['hurt']['delimit'],reclass_text_strings['no_change'],
                        reclass_text_strings['hate']['delimit'],reclass_text_strings['hate']['form_opt'],reclass_text_strings['neither']['delimit'],reclass_text_strings['neither']['form_opt']]

        return {'reclass_texts':to_reclass,'form':form_opt_data}
    else:
        to_reclass =[(tweets_dict['text'][i],np.argmax(results['prediction_array'][i]),f'ITEM {str(i)}') for i in range(len(tweets_dict['text'])) if int(np.argmax(results['prediction_array'][i]) == 2)]
        if len(to_reclass)> 5:
            to_reclass = to_reclass[:5]
        print('***** List of hateful items avail to reclass ******')
        print(to_reclass[:5])
        print('***** END RECLASS SNIPPET ******')
        # Build reclass form with hate tweets if hate tweets were returned.
        form_opt_data = [reclass_text_strings['neither']['h1'],reclass_text_strings['neither']['span'],reclass_text_strings['neither']['delimit'],reclass_text_strings['no_change'],
                        reclass_text_strings['hurt']['delimit'],reclass_text_strings['hurt']['form_opt'],reclass_text_strings['hate']['delimit'],reclass_text_strings['hate']['form_opt']]
        return {'reclass_texts':to_reclass,'form':form_opt_data}
