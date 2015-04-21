# -*- coding: utf-8 -*-

import datetime, json, os, pprint
import flask
from bdpyweb_code.utils import log_helper
from flask.ext.basicauth import BasicAuth  # http://flask-basicauth.readthedocs.org/en/latest/


app = flask.Flask(__name__)
app.config[u'BASIC_AUTH_USERNAME'] = unicode( os.environ[u'bdpyweb__BASIC_AUTH_USERNAME'] )
app.config[u'BASIC_AUTH_PASSWORD'] = unicode( os.environ[u'bdpyweb__BASIC_AUTH_PASSWORD'] )
basic_auth = BasicAuth( app )
log = log_helper.setup_logger()


@app.route( u'/', methods=[u'GET'] )  # /bdpyweb/v1/
def root_redirect():
    """ Redirects to readme. """
    log.debug( u'- in bdpyweb_code.root_redirect(); starting' )
    return flask.redirect( u'https://github.com/birkin/bdpyweb_code/blob/master/README.md', code=303 )


@app.route( u'/v1/', methods=[u'GET'] )  # /bdpyweb/v1/
@basic_auth.required
def return_json():
    """ Handles post & returns json results. """
    log.debug( u'- in bdpyweb_code.return_json(); starting' )
    return_dict = { u'foo': u'bar' }
    return flask.jsonify( return_dict )




if __name__ == u'__main__':
    if os.getenv( u'DEVBOX' ) == u'true':
        app.run( host=u'0.0.0.0', debug=True )
    else:
        app.run()
