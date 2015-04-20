# -*- coding: utf-8 -*-

import datetime, json, os, pprint
import flask
from bdpyweb_app.utils import logger_setup


app = flask.Flask(__name__)
log = logger_setup.setup_logger()


@app.route( u'/v1/', methods=['GET'] )  # /bdpyweb/v1/
def return_json():
    """ Submits search or request & returns json results. """
    log.debug( u'- in bdpyweb_app.return_json(); starting' )
    return_dict[u'foo'] = u'bar'
    return flask.jsonify( return_dict )




if __name__ == u'__main__':
    if os.getenv( u'DEVBOX' ) == u'true':
        app.run( host=u'0.0.0.0', debug=True )
    else:
        app.run()
