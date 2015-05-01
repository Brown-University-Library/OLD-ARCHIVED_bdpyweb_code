# -*- coding: utf-8 -*-

import datetime, json, os, pprint
import flask
from bdpyweb_code.utils import log_helper
from flask import render_template
from flask.ext.basicauth import BasicAuth  # http://flask-basicauth.readthedocs.org/en/latest/
from utils.app_helper import Helper


app = flask.Flask(__name__)
app.config[u'BASIC_AUTH_USERNAME'] = unicode( os.environ[u'bdpyweb__BASIC_AUTH_USERNAME'] )
app.config[u'BASIC_AUTH_PASSWORD'] = unicode( os.environ[u'bdpyweb__BASIC_AUTH_PASSWORD'] )
app.secret_key = os.urandom(24)
basic_auth = BasicAuth( app )
logger = log_helper.setup_logger()
ezb_helper = EzbHelper( logger )
form_helper = FormHelper( logger )


@app.route( u'/', methods=[u'GET'] )  # /bdpyweb
def root_redirect():
    """ Redirects to readme. """
    logger.debug( u'starting' )
    return flask.redirect( u'https://github.com/birkin/bdpyweb_code/blob/master/README.md', code=303 )


@app.route( u'/v1', methods=[u'POST'] )  # /bdpyweb/v1/
def handle_ezb_v1():
    """ Handles post from easyborrow & returns json results. """
    logger.debug( u'starting' )
    if ezb_helper.validate_request( flask.request.form ) == False:
        logger.info( u'request invalid, returning 400' )
        flask.abort( 400 )  # `Bad Request`
    result_data = ezb_helper.do_lookup( flask.request.form )
    interpreted_response_dct = ezb_helper.interpret_result( result_data )
    logger.debug( u'returning response' )
    return flask.jsonify( interpreted_response_dct )


@app.route( u'/form/', methods=[u'GET'] )  # /bdpyweb/form/
@basic_auth.required
def handle_form_get():
    """ Displays isbn form on get. """
    logger.debug( u'starting' )
    logger.debug( u'session keys(), `%s`' % flask.session.keys() )
    isbn = flask.session.get( u'isbn', None )
    return render_template( 'form.html', isbn=isbn )


@app.route( u'/form_handler/', methods=[u'POST'] )  # /bdpyweb/form_handler/
def handle_form_post():
    """ Runs lookup, stores json to session, and redirects back to the form-page with a GET. """
    logger.debug( u'starting' )
    isbn = flask.request.form[u'isbn']
    logger.debug( u'isbn, `%s`' % isbn )
    flask.session[u'isbn'] = isbn
    search_result = form_helper.run_search( isbn )
    request_result = form_helper.run_request( isbn )
    repsonse_dct = form_helper.build_response_dct( isbn, search_result, request_result )
    jsn = json.dumps( repsonse_dct, sort_keys=True, indent=2 )
    flask.session[u'jsn'] = jsn
    return flask.redirect( u'/bdpyweb/form/' )




if __name__ == u'__main__':
    if os.getenv( u'DEVBOX' ) == u'true':
        app.run( host=u'0.0.0.0', debug=True )
    else:
        app.run()
