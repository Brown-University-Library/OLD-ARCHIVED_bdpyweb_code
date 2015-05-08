# -*- coding: utf-8 -*-

"""
Helper for bdpyweb_app.py
"""

import datetime, json, os, pprint, time
import flask
import requests
from bdpy import BorrowDirect


class FormHelper( object ):
    """ Helper functions. """

    def __init__( self, logger ):
        """ Helper functions for app->handle_form() """
        self.logger = logger
        self.logger.debug( u'form_helper initialized' )
        self.defaults = {
            u'UNIVERSITY_CODE': unicode( os.environ[u'bdpyweb__BDPYTEST_UNIVERSITY_CODE'] ),
            u'API_URL_ROOT': unicode( os.environ[u'bdpyweb__BDPYTEST_API_ROOT_URL'] ),
            u'PARTNERSHIP_ID': unicode( os.environ[u'bdpyweb__BDPYTEST_PARTNERSHIP_ID'] ),
            u'PICKUP_LOCATION': unicode( os.environ[u'bdpyweb__BDPYTEST_PICKUP_LOCATION'] ),
            u'PATRON_BARCODE': unicode( os.environ[u'bdpyweb__BDPYTEST_PATRON_BARCODE'] ),
            u'AVAILABILITY_API_URL_ROOT': unicode( os.environ[u'bdpyweb__BDPYTEST_AVAILABILITY_API_URL_ROOT'] )
            }

    ## main functions

    def run_search( self, isbn ):
        """ Hits test-server with search & returns output.
            Called by bdpyweb_app.handle_form_post() """
        bd = BorrowDirect( self.defaults, self.logger )
        bd.run_search( self.defaults[u'PATRON_BARCODE'], u'ISBN', isbn )
        bdpy_result = bd.search_result
        if bdpy_result.get( u'Item', None ) and bdpy_result[u'Item'].get( u'AuthorizationId', None ):
            bdpy_result[u'Item'][u'AuthorizationId'] = u'(hidden)'
        return bdpy_result

    def run_request( self, isbn ):
        """ Hits test-server with request & returns output.
            Called by bdpyweb_app.handle_form_post() """
        time.sleep( 1 )
        bd = BorrowDirect( self.defaults, self.logger )
        bd.run_request_item( self.defaults[u'PATRON_BARCODE'], u'ISBN', isbn )
        bdpy_result = bd.request_result
        return bdpy_result

    def hit_availability_api( self, isbn ):
        """ Hits hit_availability_api for holdings data.
            Called by bdpyweb_app.handle_form_post() """
        url = u'%s/%s/' % ( self.defaults[u'AVAILABILITY_API_URL_ROOT'], isbn )
        r = requests.get( url )
        dct = r.json()
        items = dct[u'items']
        for item in items:
            for key in [u'is_available', u'requestable', u'barcode', u'callnumber']:
                del item[key]
        return_dct = {
            u'title': dct.get( u'title', None ),
            u'items': items }
        return return_dct

    def build_response_jsn( self, isbn, search_result, request_result, availability_api_data, start_time ):
        """ Prepares response data.
            Called by bdpyweb_app.handle_form_post() """
        end_time = datetime.datetime.now()
        response_dct = {
            u'request': { u'datetime': unicode(start_time), u'isbn': isbn },
            u'response': {
                u'availability_api_data': availability_api_data,
                u'bd_api_testserver_search_result': search_result,
                u'bd_api_testserver_request_result': request_result,
                u'time_taken': unicode( end_time - start_time ) }
                }
        self.logger.debug( u'response_dct, `%s`' % pprint.pformat(response_dct) )
        return json.dumps( response_dct, sort_keys=True, indent=4 )

    # end class FormHelper


class EzbHelper( object ):
    """ Helper functions for app->handle_ezb_v1() """

    def __init__( self, logger ):
        self.logger = logger
        self.logger.debug( u'ezb_helper initialized' )

    ## main functions (called by bdpyweb_app.py functions)

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

    def interpret_result( self, bdpy_result ):
        """ Examines api result and prepares response expected by easyborrow controller.
            Called by bdpyweb_app.handle_v1()
            Note: at the moment, it does not appear that the new BD api distinguishes between 'found' and 'requestable'. """
        return_dct = {
            u'search_result': u'FAILURE', u'bd_confirmation_code': None, u'found': False, u'requestable': False }
        if u'Request' in bdpy_result.keys():
            if u'RequestNumber' in bdpy_result[u'Request'].keys():
                return_dct[u'search_result'] = u'SUCCESS'
                return_dct[u'bd_confirmation_code'] = bdpy_result[u'Request'][u'RequestNumber']
                return_dct[u'found'] = True
                return_dct[u'requestable'] = True
        self.logger.debug( u'interpreted result-dct, `%s`' % pprint.pformat(return_dct) )
        return return_dct

    ## helper functions (called by above functions)

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
        if params.get( u'api_authorization_code', u'nope' ) == API_AUTHORIZATION_CODE:
            if params.get( u'api_identity', u'nope' ) == API_IDENTITY:
                auth_good = True
        self.logger.debug( u'auth_good, `%s`' % auth_good )
        return auth_good

    # end class Helper()

