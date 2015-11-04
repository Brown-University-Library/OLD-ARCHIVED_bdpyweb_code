#### about

bdpyweb is a [flask](http://flask.pocoo.org) wrapper around [bdpy](https://github.com/Brown-University-Library/borrowdirect.py), a python library for the [BorrowDirect](http://www.borrowdirect.org) api.



#### usage

sample script...

    # -*- coding: utf-8 -*-

    from __future__ import unicode_literals
    import os
    import requests


    ## settings
    URL = os.environ['bdpyweb_flask_api_url']
    API_IDENTITY = os.environ['bdpyweb_flask_api_identity']
    API_KEY = os.environ['bdpyweb_flask_api_auth_key']

    params = {
        'api_identity': API_IDENTITY,
        'api_authorization_code': API_KEY,
        'user_barcode': 'the_patron_barcode',
        'isbn': 'the_isbn'
        }
    r = requests.post( URL, data=params )
    print r.content

    # on success, the json response...
    # {
    #   "bd_confirmation_code": "BRO-12345678",
    #   "found": true,
    #   "requestable": true,
    #   "search_result": "SUCCESS"
    # }

    # on failure, the json response...
    # {
    #   "bd_confirmation_code": null,
    #   "found": false,
    #   "requestable": false,
    #   "search_result": "FAILURE"
    # }


#### notes

- the requirements.txt [shellvars-py](https://github.com/aneilbaboo/shellvars-py) is not technically necessary for this code to run, but is required for the way we load our environmental variables, and won't hurt anything if not used.

- code contact: birkin_diana@brown.edu

---
