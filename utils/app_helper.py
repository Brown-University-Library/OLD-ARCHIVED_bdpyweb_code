# -*- coding: utf-8 -*-

"""
Helper for bdpyweb_app.py
"""

import datetime, os
import requests


class Helper( object ):
    """ Helper functions. """

    def __init__( self, logger ):
        self.logger = logger
        self.logger.debug( u'helper initialized' )

    def validate_request( self, params ):
        keys_good = u'init'
        required_keys = [ u'api_authorization_code', u'api_identity', u'isbn',  u'user_barcode' ]
        for required_key in required_keys:
            if required_key not in params.keys():
                keys_good = False
                break
        ## next, ip address check
        return False

    # end class Helper()
