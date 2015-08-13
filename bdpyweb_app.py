# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import datetime, json, os, pprint
import flask
from bdpyweb_code.utils import log_helper
from flask import render_template
from flask.ext.basicauth import BasicAuth  # http://flask-basicauth.readthedocs.org/en/latest/
from utils.app_helper import EzbHelper, FormHelper


app = flask.Flask(__name__)
app.config['BASIC_AUTH_USERNAME'] = unicode( os.environ['bdpyweb__BASIC_AUTH_USERNAME'] )
app.config['BASIC_AUTH_PASSWORD'] = unicode( os.environ['bdpyweb__BASIC_AUTH_PASSWORD'] )
app.secret_key = unicode( os.environ['bdpyweb__SECRET_KEY'] )
basic_auth = BasicAuth( app )
logger = log_helper.setup_logger()
ezb_helper = EzbHelper( logger )
# form_helper = FormHelper( logger )


@app.route( '/', methods=['GET'] )  # /bdpyweb
def root_redirect():
    """ Redirects to readme. """
    logger.debug( 'starting' )
    return flask.redirect( 'https://github.com/birkin/bdpyweb_code/blob/master/README.md', code=303 )


@app.route( '/v1', methods=['POST'] )  # /bdpyweb/v1/
def handle_ezb_v1():
    """ Handles post from easyborrow & returns json results. """
    logger.debug( 'starting' )
    if ezb_helper.validate_request( flask.request.form ) == False:
        logger.info( 'request invalid, returning 400' )
        flask.abort( 400 )  # `Bad Request`
    result_data = ezb_helper.do_lookup( flask.request.form )
    interpreted_response_dct = ezb_helper.interpret_result( result_data )
    logger.debug( 'returning response' )
    return flask.jsonify( interpreted_response_dct )


@app.route( '/form/', methods=['GET'] )  # /bdpyweb/form/
@basic_auth.required
def handle_form_get():
    """ Displays isbn form on get. """
    logger.debug( 'starting' )
    logger.debug( 'session keys(), `%s`' % flask.session.keys() )
    isbn = flask.session.get( 'isbn', None )
    result_jsn = flask.session.get( 'result_jsn' )
    # return render_template( 'form.html', data={'result_jsn': result_jsn, 'isbn': isbn} )
    return flask.jsonify( {'message': "form temporarily disabled because BorrowDirect has temporarily disabled it's api test-url"} )


@app.route( '/form_handler/', methods=['POST'] )  # /bdpyweb/form_handler/
def handle_form_post():
    """ Runs lookup, stores json to session, and redirects back to the form-page with a GET. """
    now = datetime.datetime.now()
    logger.debug( 'starting' )
    isbn = flask.request.form['isbn']
    flask.session['isbn'] = isbn
    search_result = form_helper.run_search( isbn )
    request_result = form_helper.run_request( isbn )
    availability_api_data = form_helper.hit_availability_api( isbn )
    response_jsn = form_helper.build_response_jsn( isbn, search_result, request_result, availability_api_data, now )
    flask.session['result_jsn'] = response_jsn
    flask.session.modified = True
    return flask.redirect( '/bdpyweb/form/' )




if __name__ == '__main__':
    if os.getenv( 'DEVBOX' ) == 'true':
        app.run( host='0.0.0.0', debug=True )
    else:
        app.run()
