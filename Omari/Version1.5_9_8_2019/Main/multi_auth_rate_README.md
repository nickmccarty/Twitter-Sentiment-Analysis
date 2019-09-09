# Multi- Authentication Handler

## Combine Tweepy 3.8.0 and NIRG's forked Tweepy for python2

* NIRG"s forked version contained the ability to switch between api keys when rate limit approached. This was built for python2.

* Since the python2 version of Tweepy was released, many new beneficial feats added.

* Made the NIRG fork Py3 compatible and merged with Tweepy latest version.

* Use `monitor_rate_limit=true` as a param to monitor rate limit and switch when it approaches.

* To be used in AWS a requirements.txt with the normal format `modulename=vers.i.on`, upload to PyPI required.

* PyPi package is tweepy-mashup. Version is 1.0.0

  `pip install tweepy-mashup`

* Updated requirements.txt to include this package
  > requirements.text

    `tweepy-mashup=1.0.0`

* **Tweepy Mashup repo** [link] (https://github.com/oblockton/tweepy_fix 'Tweepy Mashup Repo')
