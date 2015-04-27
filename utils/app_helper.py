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

    # end class Helper()
