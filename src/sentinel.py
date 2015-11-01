""" support sentinel connector. """

# !-*- coding: utf-8 -*-

from redis.sentinel import Sentinel
from redis.sentinel import ConnectionError
from redis.sentinel import MasterNotFoundError
from redis.sentinel import SlaveNotFoundError


def get_session(host, port):
    """ get sentinel session.

    @param host: (str) sentinel host address
    @param port: (int) sentinel port number
    @return: (obj, None) sentinel session, none connection is return None
    """
    try:
        s = Sentinel([(host, port)], socket_timeout=0.1)
    except ConnectionError:
        s = None
    return s


def get_master(session, master_name):
    """ get sentinel master information.

    @param session: (obj) sentinel session
    @return: (tuple) ('host', port) master information
    """
    try:
        m = session.discover_master(master_name)
    except MasterNotFoundError:
        m = None

    return m


def get_slaves(session, master_name):
    """ get relation sentinel master with slaves.

    @param session: (obj) sentinel session
    @return: (list) [('host', port)] slave list
    """
    try:
        svs = session.discover_slaves(master_name)
    except SlaveNotFoundError:
        svs = None

    return svs
