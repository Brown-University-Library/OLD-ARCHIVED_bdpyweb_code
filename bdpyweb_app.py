# -*- coding: utf-8 -*-

import datetime, json, os, pprint
import flask
from bdpyweb_code.utils import log_helper
from flask.ext.basicauth import BasicAuth  # http://flask-basicauth.readthedocs.org/en/latest/
from flask.views import MethodView
from utils.app_helper import Helper



app = flask.Flask(__name__)
app.config[u'BASIC_AUTH_USERNAME'] = unicode( os.environ[u'bdpyweb__BASIC_AUTH_USERNAME'] )
app.config[u'BASIC_AUTH_PASSWORD'] = unicode( os.environ[u'bdpyweb__BASIC_AUTH_PASSWORD'] )
basic_auth = BasicAuth( app )
logger = log_helper.setup_logger()
hlpr = Helper( logger )


@app.route( u'/', methods=[u'GET'] )  # /bdpyweb
def root_redirect():
    """ Redirects to readme. """
    logger.debug( u'starting' )
    return flask.redirect( u'https://github.com/birkin/bdpyweb_code/blob/master/README.md', code=303 )


@app.route( u'/v1', methods=[u'POST'] )  # /bdpyweb/v1/
def handle_ezb_v1():
    """ Handles post from easyborrow & returns json results. """
    logger.debug( u'starting' )
    if hlpr.validate_request( flask.request.form ) == False:
        logger.info( u'request invalid, returning 400' )
        flask.abort( 400 )  # `Bad Request`
    result_data = hlpr.do_lookup( flask.request.form )
    interpreted_response_dct = hlpr.interpret_result( result_data )
    logger.debug( u'returning response' )
    return flask.jsonify( interpreted_response_dct )


@app.route( u'/form/', methods=[u'GET'] )  # /bdpyweb/form/
@basic_auth.required
def handle_form_get():
    """ Displays form on get, and outputs json on post. """
    logger.debug( u'starting' )
    return_dict = { u'foo': u'bar' }
    return flask.jsonify( return_dict )

@app.route( u'/form_handler/', methods=[u'POST'] )  # /bdpyweb/form_handler/
def handle_form_post():
    """ Displays form on get, and outputs json on post. """
    logger.debug( u'starting' )

    return_dict = { u'fooo': u'barr' }
    return flask.jsonify( return_dict )




if __name__ == u'__main__':
    if os.getenv( u'DEVBOX' ) == u'true':
        app.run( host=u'0.0.0.0', debug=True )
    else:
        app.run()
