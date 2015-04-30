# -*- coding: utf-8 -*-

"""
Helper for bdpyweb_app.py
"""

import datetime, json, os
import flask
import requests
from bdpy import BorrowDirect


class Helper( object ):
    """ Helper functions. """

    def __init__( self, logger ):
        self.logger = logger
        self.logger.debug( u'helper initialized' )

    ## main functions

    def validate_request( self, params ):
        """ Checks params, ip, & auth info; returns boolean.
            Called by bdpyweb_app.handle_v1() """
        validity = False
        keys_good = self.check_keys( params )
        ip_good = self.check_ip()
        auth_good = self.check_auth( params )
        if keys_good and ip_good and auth_good:
            validity = True
        self.logger.debug( u'validity, `%s`' % validity )
        return validity

    def do_lookup( self, params ):
        """ Runs lookup; returns bdpy output.
            Called by bdpyweb_app.handle_v1() """
        defaults = self.load_bdpy_defaults()
        bd = BorrowDirect( defaults, self.logger )
        bd.run_request_item( params[u'user_barcode'], 'ISBN', params[u'isbn'] )
        bdpy_result = bd.request_result
        self.logger.debug( u'bdpy_result, `%s`' % bdpy_result )
        return bdpy_result

    def prep_response( self, bdpy_result_dct ):
        """ Prepares webapp response.
            Called by bdpyweb_app.handle_v1() """
        response_dct = {
            u'request': u'time': unicode( datetime.datetime.now() ),
            u'response': bdpy_result_dct
            }
        return response_dct

    ##

    def load_bdpy_defaults( self ):
        """ Loads up non-changing bdpy defaults.
            Called by do_lookup() """
        defaults = {
            u'UNIVERSITY_CODE': unicode( os.environ[u'bdpyweb__BDPY_UNIVERSITY_CODE'] ),
            u'API_URL_ROOT': unicode( os.environ[u'bdpyweb__BDPY_API_ROOT_URL'] ),
            u'PARTNERSHIP_ID': unicode( os.environ[u'bdpyweb__BDPY_PARTNERSHIP_ID'] ),
            u'PICKUP_LOCATION': unicode( os.environ[u'bdpyweb__BDPY_PICKUP_LOCATION'] ),
            }
        self.logger.debug( u'defaults, `%s`' % defaults )
        return defaults

    ## helper functions

    def check_keys( self, params ):
        """ Checks required keys; returns boolean.
            Called by validate_request() """
        keys_good = False
        required_keys = [ u'api_authorization_code', u'api_identity', u'isbn',  u'user_barcode' ]
        for required_key in required_keys:
            if required_key not in params.keys():
                break
            if required_key == required_keys[-1]:
                keys_good = True
        self.logger.debug( u'keys_good, `%s`' % keys_good )
        return keys_good

    def check_ip( self ):
        """ Checks ip; returns boolean.
            Called by validate_request() """
        LEGIT_IPS = json.loads( unicode(os.environ[u'bdpyweb__LEGIT_IPS']))
        ip_good = False
        if flask.request.remote_addr in LEGIT_IPS:
            ip_good = True
        self.logger.debug( u'ip_good, `%s`' % ip_good )
        return ip_good

    def check_auth( self, params ):
        """ Checks auth params; returns boolean.
            Called by validate_request() """
        API_AUTHORIZATION_CODE = unicode( os.environ[u'bdpyweb__API_AUTHORIZATION_CODE'] )  # for v1
        API_IDENTITY = unicode( os.environ[u'bdpyweb__API_IDENTITY'] )  # for v1
        auth_good = False
        if params.get(u'api_authorization_code', u'nope') == API_AUTHORIZATION_CODE:
            if params.get(u'api_identity', u'nope') == API_IDENTITY:
                auth_good = True
        self.logger.debug( u'auth_good, `%s`' % auth_good )
        return auth_good

    # end class Helper()

