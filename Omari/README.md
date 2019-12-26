# Neural Networks, ML, and NLP for hate speech classification

Sentiment analysis of streaming data is quickly approaching ubiquity. From the nonprofit sector to business to government agencies, virtually any manner of organization stands to benefit from performing some sort of “opinion mining” on available data. One common use case is the analysis of data from social media activity to gain a sense of the “feeling” that underlies posts and comments.

In light of the recent social climate, and the growing link between hateful rhetoric becoming hateful actions, we have chosen to use our skills as Data Analysts to develop a tool that can query a data source and classify speech in text as either 'hateful', 'offensive', or 'neither hateful nor offensive'.

The Erase Hate application uses a Long Short-Term Memory classification model to classify text as either ‘hateful’, ‘offensive’, or ‘neither hateful nor offensive’. Users may query Twitter for data or input a block of text. After classification results are provided, user’s may then reclassify the text items if they disagree with the models’ classification. This human classified data is then used in further model re-training, a scheduled and fully automated process (including updating the web app to use the most recent model). The entire architecture is comprised of a distributed system with many components working in the AWS cloud. In addition to the Web UI there is an API, and a Python library API wrapper (available on PyPi) that provides easy interfacing with the API. In depth documentation is provided for both the Web UI, API, and Python library.

### Repo Structure
Live Application - https://www.erasehateapp.com

[Deployed Application Components](https://github.com/nickmccarty/Twitter-Sentiment-Analysis/tree/master/Omari/Version3.0_11_6_2019 'Live App')
The complete deployed application and its components can be found here.

- Folder: Main - The web facing front end. An AWS deployed front-end. Responsible for executing/routing users queries.  
- Folder: ModelServer - A dedicated AWS instance used only for serving predictions from the LSTM model.
- Folder: Vote_Retrain - Scripts that control the database functions, and model retraining procedure

**A library for prior versions is contained here** [Version Repo](https://github.com/oblockton/Erase-Hate-Versioning 'Version Repo')


[LSTM Model Building](https://github.com/nickmccarty/Twitter-Sentiment-Analysis/tree/master/FINAL/LSTM 'LSTM Model Building')

[API Repo & Docs](https://github.com/oblockton/Erase_Hate_Python_Library 'API Repo & Docs')
PyPi Module https://pypi.org/search/?q=erasehate
