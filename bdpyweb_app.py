# -*- coding: utf-8 -*-

import datetime, json, os, pprint
import flask
from bdpyweb_code.utils import log_helper


app = flask.Flask(__name__)
log = log_helper.setup_logger()


@app.route( u'/', methods=['GET'] )  # /bdpyweb/v1/
def root_redirect():
    """ Redirects to versioned url. """
    log.debug( u'- in bdpyweb_code.root_redirect(); starting' )
    return flask.redirect( "./v1/", code=302 )
    # return_dict = {u'a': u'b'}
    # return flask.jsonify( return_dict )


@app.route( u'/v1/', methods=['GET'] )  # /bdpyweb/v1/
def return_json():
    """ Handles post & returns json results. """
    log.debug( u'- in bdpyweb_code.return_json(); starting' )
    return_dict = {u'foo': u'bar'}
    return flask.jsonify( return_dict )




if __name__ == u'__main__':
    if os.getenv( u'DEVBOX' ) == u'true':
        app.run( host=u'0.0.0.0', debug=True )
    else:
        app.run()
