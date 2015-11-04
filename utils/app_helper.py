# -*- coding: utf-8 -*-

from __future__ import unicode_literals

"""
Helper for bdpyweb_app.py
"""

import datetime, json, os, pprint, time
import flask
import requests
from bdpy import BorrowDirect


class EzbHelper( object ):
    """ Helper functions for app->handle_ezb_v1() """

    def __init__( self, logger ):
        self.logger = logger
        self.logger.debug( 'ezb_helper initialized' )

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
        self.logger.debug( 'validity, `%s`' % validity )
        return validity

    def do_lookup( self, params ):
        """ Runs lookup; returns bdpy output.
            Called by bdpyweb_app.handle_v1() """
        self.logger.debug( 'params, `%s`' % pprint.pformat(params) )
        defaults = self.load_bdpy_defaults()
        bd = BorrowDirect( defaults, self.logger )
        bd.run_request_item( params['user_barcode'], 'ISBN', params['isbn'] )
        bdpy_result = bd.request_result
        self.logger.debug( 'bdpy_result, `%s`' % bdpy_result )
        return bdpy_result

    def interpret_result( self, bdpy_result ):
        """ Examines api result and prepares response expected by easyborrow controller.
            Called by bdpyweb_app.handle_v1()
            Note: at the moment, it does not appear that the new BD api distinguishes between 'found' and 'requestable'. """
        return_dct = {
            'search_result': 'FAILURE', 'bd_confirmation_code': None, 'found': False, 'requestable': False }
        if 'Request' in bdpy_result.keys():
            if 'RequestNumber' in bdpy_result['Request'].keys():
                return_dct['search_result'] = 'SUCCESS'
                return_dct['bd_confirmation_code'] = bdpy_result['Request']['RequestNumber']
                return_dct['found'] = True
                return_dct['requestable'] = True
        self.logger.debug( 'interpreted result-dct, `%s`' % pprint.pformat(return_dct) )
        return return_dct

    ## helper functions (called by above functions)

    def load_bdpy_defaults( self ):
        """ Loads up non-changing bdpy defaults.
            Called by do_lookup() """
        defaults = {
            'API_URL_ROOT': unicode( os.environ['bdpyweb__BDPY_API_ROOT_URL'] ),
            'API_KEY': unicode( os.environ['bdpyweb__BDPY_API_KEY'] ),
            'UNIVERSITY_CODE': unicode( os.environ['bdpyweb__BDPY_UNIVERSITY_CODE'] ),
            'PARTNERSHIP_ID': unicode( os.environ['bdpyweb__BDPY_PARTNERSHIP_ID'] ),
            'PICKUP_LOCATION': unicode( os.environ['bdpyweb__BDPY_PICKUP_LOCATION'] ),
            }
        self.logger.debug( 'defaults, `%s`' % defaults )
        return defaults

    def check_keys( self, params ):
        """ Checks required keys; returns boolean.
            Called by validate_request() """
        keys_good = False
        required_keys = [ 'api_authorization_code', 'api_identity', 'isbn',  'user_barcode' ]
        for required_key in required_keys:
            if required_key not in params.keys():
                break
            if required_key == required_keys[-1]:
                keys_good = True
        self.logger.debug( 'keys_good, `%s`' % keys_good )
        return keys_good

    def check_ip( self ):
        """ Checks ip; returns boolean.
            Called by validate_request() """
        LEGIT_IPS = json.loads( unicode(os.environ['bdpyweb__LEGIT_IPS']))
        ip_good = False
        if flask.request.remote_addr in LEGIT_IPS:
            ip_good = True
        else:
            self.logger.debug( 'bad ip, `%s`' % flask.request.remote_addr )
        self.logger.debug( 'ip_good, `%s`' % ip_good )
        return ip_good

    def check_auth( self, params ):
        """ Checks auth params; returns boolean.
            Called by validate_request() """
        API_AUTHORIZATION_CODE = unicode( os.environ['bdpyweb__API_AUTHORIZATION_CODE'] )  # for v1
        API_IDENTITY = unicode( os.environ['bdpyweb__API_IDENTITY'] )  # for v1
        auth_good = False
        if params.get( 'api_authorization_code', 'nope' ) == API_AUTHORIZATION_CODE:
            if params.get( 'api_identity', 'nope' ) == API_IDENTITY:
                auth_good = True
        self.logger.debug( 'auth_good, `%s`' % auth_good )
        return auth_good

    # end class EzbHelper


class FormHelper( object ):
    """ Helper functions. """

    def __init__( self, logger ):
        """ Helper functions for app->handle_form() """
        self.logger = logger
        self.logger.debug( 'form_helper initialized' )
        self.defaults = {
            'UNIVERSITY_CODE': unicode( os.environ['bdpyweb__BDPYTEST_UNIVERSITY_CODE'] ),
            'API_URL_ROOT': unicode( os.environ['bdpyweb__BDPYTEST_API_ROOT_URL'] ),
            'PARTNERSHIP_ID': unicode( os.environ['bdpyweb__BDPYTEST_PARTNERSHIP_ID'] ),
            'PICKUP_LOCATION': unicode( os.environ['bdpyweb__BDPYTEST_PICKUP_LOCATION'] ),
            'PATRON_BARCODE': unicode( os.environ['bdpyweb__BDPYTEST_PATRON_BARCODE'] ),
            'AVAILABILITY_API_URL_ROOT': unicode( os.environ['bdpyweb__BDPYTEST_AVAILABILITY_API_URL_ROOT'] )
            }

    ## main functions

    def run_search( self, isbn ):
        """ Hits test-server with search & returns output.
            Called by bdpyweb_app.handle_form_post() """
        bd = BorrowDirect( self.defaults, self.logger )
        bd.run_search( self.defaults['PATRON_BARCODE'], 'ISBN', isbn )
        bdpy_result = bd.search_result
        if bdpy_result.get( 'Item', None ) and bdpy_result['Item'].get( 'AuthorizationId', None ):
            bdpy_result['Item']['AuthorizationId'] = '(hidden)'
        return bdpy_result

    def run_request( self, isbn ):
        """ Hits test-server with request & returns output.
            Called by bdpyweb_app.handle_form_post() """
        time.sleep( 1 )
        bd = BorrowDirect( self.defaults, self.logger )
        bd.run_request_item( self.defaults['PATRON_BARCODE'], 'ISBN', isbn )
        bdpy_result = bd.request_result
        return bdpy_result

    def hit_availability_api( self, isbn ):
        """ Hits hit_availability_api for holdings data.
            Called by bdpyweb_app.handle_form_post() """
        url = '%s/%s/' % ( self.defaults['AVAILABILITY_API_URL_ROOT'], isbn )
        r = requests.get( url )
        dct = r.json()
        items = dct['items']
        for item in items:
            for key in ['is_available', 'requestable', 'barcode', 'callnumber']:
                del item[key]
        return_dct = {
            'title': dct.get( 'title', None ),
            'items': items }
        return return_dct

    def build_response_jsn( self, isbn, search_result, request_result, availability_api_data, start_time ):
        """ Prepares response data.
            Called by bdpyweb_app.handle_form_post() """
        end_time = datetime.datetime.now()
        response_dct = {
            'request': { 'datetime': unicode(start_time), 'isbn': isbn },
            'response': {
                'availability_api_data': availability_api_data,
                'bd_api_testserver_search_result': search_result,
                'bd_api_testserver_request_result': request_result,
                'time_taken': unicode( end_time - start_time ) }
                }
        self.logger.debug( 'response_dct, `%s`' % pprint.pformat(response_dct) )
        return json.dumps( response_dct, sort_keys=True, indent=4 )

    # end class FormHelper


# class EzbHelper( object ):
#     """ Helper functions for app->handle_ezb_v1() """

#     def __init__( self, logger ):
#         self.logger = logger
#         self.logger.debug( 'ezb_helper initialized' )

#     ## main functions (called by bdpyweb_app.py functions)

#     def validate_request( self, params ):
#         """ Checks params, ip, & auth info; returns boolean.
#             Called by bdpyweb_app.handle_v1() """
#         validity = False
#         keys_good = self.check_keys( params )
#         ip_good = self.check_ip()
#         auth_good = self.check_auth( params )
#         if keys_good and ip_good and auth_good:
#             validity = True
#         self.logger.debug( 'validity, `%s`' % validity )
#         return validity

#     def do_lookup( self, params ):
#         """ Runs lookup; returns bdpy output.
#             Called by bdpyweb_app.handle_v1() """
#         defaults = self.load_bdpy_defaults()
#         bd = BorrowDirect( defaults, self.logger )
#         bd.run_request_item( params['user_barcode'], 'ISBN', params['isbn'] )
#         bdpy_result = bd.request_result
#         self.logger.debug( 'bdpy_result, `%s`' % bdpy_result )
#         return bdpy_result

#     def interpret_result( self, bdpy_result ):
#         """ Examines api result and prepares response expected by easyborrow controller.
#             Called by bdpyweb_app.handle_v1()
#             Note: at the moment, it does not appear that the new BD api distinguishes between 'found' and 'requestable'. """
#         return_dct = {
#             'search_result': 'FAILURE', 'bd_confirmation_code': None, 'found': False, 'requestable': False }
#         if 'Request' in bdpy_result.keys():
#             if 'RequestNumber' in bdpy_result['Request'].keys():
#                 return_dct['search_result'] = 'SUCCESS'
#                 return_dct['bd_confirmation_code'] = bdpy_result['Request']['RequestNumber']
#                 return_dct['found'] = True
#                 return_dct['requestable'] = True
#         self.logger.debug( 'interpreted result-dct, `%s`' % pprint.pformat(return_dct) )
#         return return_dct

#     ## helper functions (called by above functions)

#     def load_bdpy_defaults( self ):
#         """ Loads up non-changing bdpy defaults.
#             Called by do_lookup() """
#         defaults = {
#             'UNIVERSITY_CODE': unicode( os.environ['bdpyweb__BDPY_UNIVERSITY_CODE'] ),
#             'API_URL_ROOT': unicode( os.environ['bdpyweb__BDPY_API_ROOT_URL'] ),
#             'PARTNERSHIP_ID': unicode( os.environ['bdpyweb__BDPY_PARTNERSHIP_ID'] ),
#             'PICKUP_LOCATION': unicode( os.environ['bdpyweb__BDPY_PICKUP_LOCATION'] ),
#             }
#         self.logger.debug( 'defaults, `%s`' % defaults )
#         return defaults

#     def check_keys( self, params ):
#         """ Checks required keys; returns boolean.
#             Called by validate_request() """
#         keys_good = False
#         required_keys = [ 'api_authorization_code', 'api_identity', 'isbn',  'user_barcode' ]
#         for required_key in required_keys:
#             if required_key not in params.keys():
#                 break
#             if required_key == required_keys[-1]:
#                 keys_good = True
#         self.logger.debug( 'keys_good, `%s`' % keys_good )
#         return keys_good

#     def check_ip( self ):
#         """ Checks ip; returns boolean.
#             Called by validate_request() """
#         LEGIT_IPS = json.loads( unicode(os.environ['bdpyweb__LEGIT_IPS']))
#         ip_good = False
#         if flask.request.remote_addr in LEGIT_IPS:
#             ip_good = True
#         else:
#             self.logger.debug( 'bad ip, `%s`' % flask.request.remote_addr )
#         self.logger.debug( 'ip_good, `%s`' % ip_good )
#         return ip_good

#     def check_auth( self, params ):
#         """ Checks auth params; returns boolean.
#             Called by validate_request() """
#         API_AUTHORIZATION_CODE = unicode( os.environ['bdpyweb__API_AUTHORIZATION_CODE'] )  # for v1
#         API_IDENTITY = unicode( os.environ['bdpyweb__API_IDENTITY'] )  # for v1
#         auth_good = False
#         if params.get( 'api_authorization_code', 'nope' ) == API_AUTHORIZATION_CODE:
#             if params.get( 'api_identity', 'nope' ) == API_IDENTITY:
#                 auth_good = True
#         self.logger.debug( 'auth_good, `%s`' % auth_good )
#         return auth_good

#     # end class Helper()

