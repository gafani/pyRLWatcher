""" Daemon. """

# !-*-coding: utf-8 -*-

# Built-in
import os
import signal
import sys
import time
import optparse
import signal
import codecs

# Third party
import daemon
import click

# import app.main
from app import main
from app import DEF_CONF_FILE
from app import DEF_MASTER_ID

try:
    import jsontree
except:
    from utils import jsontree

import logger


# User define
DEF_PID_FILE = './rlwather.pid'
# DEF_LOG_FILE = './rlwather.log'
DEF_WORKDIR = os.getcwd()
DEF_UMASK = 0o002


def daemonize(debug, conf_path, log_file):
    """ daemonize. """
    ctx = daemon.DaemonContext(
            working_directory=DEF_WORKDIR,
            umask=DEF_UMASK,
            stdout=log_file,
            stderr=log_file,
            # pidfile=lockfile.FileLock(DEF_PID_FILE),
        )

    with ctx:
        main(debug, True)


@click.command()
@click.option('--debug', '-d', is_flag=True,  help='debug mode')
@click.option('--service', '-s', is_flag=True, help='service mode')
@click.argument('conf_path', type=click.Path(exists=True))
def cli(debug, service, conf_path):
    """ command line interface. """
    DEF_CONF_FILE = conf_path

    fp = codecs.open(DEF_CONF_FILE, 'rb', encoding='utf-8')
    conf_contents = fp.read()
    fp.close()

    cf = jsontree.loads(conf_contents, encoding="utf-8")

    logger.d("log filename: {0}".format(cf.log_file))
    if cf.log_file is not None:
        log_file = open(cf.log_file, 'w')

    if service:
        daemonize(debug, conf_path, log_file)
    else:
        main(debug, False)


if __name__ == '__main__':
    # daemonize()
    cli()
