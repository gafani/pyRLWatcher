""" logger. """

# !-*-coding: utf-8 -*-

import logging
import logging.handlers


log_fmt = logging.Formatter(
    '%(asctime)s [%(levelname)s]: %(message)s')
logger = logging.getLogger('mylogger')

# file_handler = logging.handlers.RotatingFileHandler(DEF_LOG_FILE,
#                                                     maxBytes=MAX_LOG_FILESIZE,
#                                                     backupCount=10)
stream_handler = logging.StreamHandler()

# file_handler.setFormatter(log_fmt)
stream_handler.setFormatter(log_fmt)

# logger.addHandler(file_handler)
logger.addHandler(stream_handler)

DEBUG_MODE = False


def d(msg):
    if DEBUG_MODE:
        logger.setLevel(logging.DEBUG)
        logger.debug(msg)


def w(msg):
    logger.setLevel(logging.WARNING)
    logger.warning(msg)


def i(msg):
    logger.setLevel(logging.INFO)
    logger.info(msg)


def e(msg):
    logger.setLevel(logging.ERROR)
    logger.error(msg)
