# -*- coding: utf-8 -*-

from __future__ import unicode_literals

"""
Handles log setup.
Assumes system's logrotate.
"""

import logging, os


def setup_logger():
    """ Returns a logger to write to a file.
        Called by bdpyweb_app.py """
    LOG_DIR = unicode( os.environ.get('bdpyweb__LOG_DIR') )
    LOG_LEVEL = unicode( os.environ.get('bdpyweb__LOG_LEVEL') )
    filename = '%s/bdpyweb.log' % LOG_DIR
    formatter = logging.Formatter( '[%(asctime)s] %(levelname)s | %(module)s->%(funcName)s() | ln %(lineno)d | %(message)s' )
    logger = logging.getLogger( __name__ )
    level_dict = { 'debug': logging.DEBUG, 'info':logging.INFO }
    logger.setLevel( level_dict[LOG_LEVEL] )
    file_handler = logging.FileHandler( filename )
    file_handler.setFormatter( formatter )
    logger.addHandler( file_handler )
    return logger
