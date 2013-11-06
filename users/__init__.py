# coding=utf-8
"""This is the main package for the application.
:copyright: (c) 2013 by Tim Sutton
:license: GPLv3, see LICENSE for more details.
"""

import os
import logging

from flask import Flask


def add_handler_once(logger, handler):
    """A helper to add a handler to a logger, ensuring there are no duplicates.

    :param logger: The logger instance.
    :type logger: logging.logger

    :param handler: Hander instance to be added. It will not be
        added if an instance of that Handler subclass already exists.
    :type handler: logging.Handler

    :returns: True if the logging handler was added
    :rtype bool: bool
    """
    class_name = handler.__class__.__name__
    for handler in logger.handlers:
        if handler.__class__.__name__ == class_name:
            return False

    logger.addHandler(handler)
    return True


def setup_logger():
    """Set up our logger with sentry support.
    """
    logger = logging.getLogger('user_map')
    logger.setLevel(logging.DEBUG)
    handler_level = logging.DEBUG
    # create formatter that will be added to the handlers
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    temp_dir = '/tmp'
    # so e.g. jenkins can override log dir.
    if 'USER_MAP_LOGFILE' in os.environ:
        file_name = os.environ['USER_MAP_LOGFILE']
    else:
        file_name = os.path.join(temp_dir, 'user-map.log')
    file_handler = logging.FileHandler(file_name)
    file_handler.setLevel(handler_level)
    # create console handler with a higher log level
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.ERROR)

    try:
        #pylint: disable=F0401
        from raven.handlers.logging import SentryHandler
        # noinspection PyUnresolvedReferences
        from raven import Client
        #pylint: enable=F0401
        client = Client(
            'http://12ef42a1d4394255a2041ac0428e8ef7:'
            '755880e336f54892bc2a65d308019997@sentry.linfiniti.com/6')
        sentry_handler = SentryHandler(client)
        sentry_handler.setFormatter(formatter)
        sentry_handler.setLevel(logging.ERROR)
        add_handler_once(logger, sentry_handler)
        logger.debug('Sentry logging enabled')

    except ImportError:
        logger.debug('Sentry logging disabled. Try pip install raven')

    #Set formatters
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # add the handlers to the logger
    add_handler_once(logger, file_handler)
    add_handler_once(logger, console_handler)


def setup_email_server():
    """Setup email server configuration.
    :return: Configuration of mail server used.
    :rtype: dict
    """
    mail_server = {
        'SERVER': 'smtp.gmail.com',
        'PORT': 587,
        'USE_TLS': False,
        'USE_SSL': True,
        'USERNAME': '',
        'PASSWORD': ''
    }
    return mail_server

setup_logger()
LOGGER = logging.getLogger('user_map')
DB = db_file = os.path.abspath(
    os.path.join(os.path.dirname(__file__), os.path.pardir, 'users.db'))

APP = Flask(__name__)
APP.config['DATABASE'] = DB
APP.config['mail_server'] = setup_email_server()
# Don't import actual view methods themselves - see:
# http://flask.pocoo.org/docs/patterns/packages/#larger-applications
# Also views must be imported AFTER app is created above.
# noinspection PyUnresolvedReferences
import users.views
