""" logstash ssh app. """

# !-*- coding: utf-8 -*-

import sys
import re
import codecs
import json

import subprocess as sp

import logger

DEF_LOCAL = 'local'
DEF_REMOTE = 'remote'

# GLOBAL
ssh_host = '127.0.0.1'
ssh_port = None
ssh_id_file = None
ssh_user = None
conf_path = 'logstash.conf'
src_path = None
conf = None

master = None

# log = logging.getLogger('mylogger')
# log.setLevel(logging.INFO)


def __get_location():
    """ get location.

    @return: (str) location string 'local' or 'remote'
    """
    global ssh_host

    lc = ['local', '127.0.0.1']

    if ssh_host.lower() in lc:
        location = DEF_LOCAL
    else:
        location = DEF_REMOTE

    return location


def __get_ssh_command():
    """ get ssh command.

    @return: ssh command
    """
    global ssh_host, ssh_port, ssh_id_file, ssh_user

    stack = ['ssh']
    if ssh_user is None:
        fmt = '{0}'.format(ssh_host)
        stack.append(fmt)
    else:
        fmt = '{0}@{1}'.format(ssh_user, ssh_host)
        stack.append(fmt)

    if ssh_port is not None:
        fmt = '-P {0}'.format(ssh_port)
        stack.append(fmt)

    if ssh_id_file is not None:
        fmt = '-i {0}'.format(ssh_id_file)
        stack.append(fmt)

    return " ".join(stack)


def __get_scp_command():
    """ get scp command.

    @return: scp command
    """
    global ssh_host, ssh_port, ssh_id_file, ssh_user, conf_path, src_path

    'scp -i id_file file_path user@domain:dest path'

    stack = ['scp']

    if ssh_id_file is not None:
        fmt = '-i {0}'.format(ssh_id_file)
        stack.append(fmt)

    if ssh_port is not None:
        fmt = '-P {0}'.format(ssh_port)
        stack.append(fmt)

    if src_path is not None:
        fmt = '{0}'.format(src_path)
        stack.append(fmt)

    if ssh_user is None:
        fmt = '{0}:{1}'.format(ssh_host, conf_path)
        stack.append(fmt)
    else:
        fmt = '{0}@{1}:{2}'.format(ssh_user, ssh_host, conf_path)
        stack.append(fmt)

    return " ".join(stack)


def __get_host_info():
    """ get host information.

    @return: (list) [(host, port), ...] for redis
    """
    global conf

    hp = r'input.+?[{].+?redis.+?[{].+?host.+?=>.+?"(.+?)".+?\n'
    hosts = re.findall(hp, conf, re.S)
    logger.d("current redis hosts: " + str(hosts))

    pp = r'input.+?[{].+?redis.+?[{].+?port.+?=>.+?(\d{1,5}).+?\n'
    ports = re.findall(pp, conf, re.S)
    logger.d("current redis ports: " + str(ports))

    if len(hosts) != len(ports):
        logger.w('different count hosts and ports')
        return []

    ips = []
    for i in range(len(hosts)):
        ips.append((hosts[i], int(ports[i])))

    return ips


def __change_config(redis_info, master_info):
    """ change configuration.

    @param redis_info: (tuple) (host, port) for redis of logstash conf
    @param master_info: (tuple) (hist, port) for redis of master
    @return: (str) chagned configuration
    """
    global conf

    convert = None
    if redis_info != master_info:
        logger.i("Change {0} to {1}".format(redis_info, master_info))
        hp = r'(input.+?[{].+?redis.+?[{].+?host.+?=>.+?)"?' \
             + redis_info[0] + r'"?(.+?[}])'
        rp = r'\1"' + master_info[0] + r'"\2'
        convert = re.sub(hp, rp, conf, flags=re.S)

        hp = r'(input.+?[{].+?redis.+?[{].+?port.+?=>.+?)"?' \
             + str(redis_info[1]) + r'"?(.+?[}])'
        rp = r'\1"'+str(master_info[1])+r'"\2'
        convert = re.sub(hp, rp, convert, flags=re.S)

    return convert


def __get_configuration():
    """ get configuration of logstash.

    @return: (str) configuration contents
    """
    global ssh_host, ssh_port, ssh_id_file, conf_path

    location = __get_location()
    logger.d("logstash:__get_configuration:location: {0}".format(location))

    cmd_list = []

    if location == DEF_REMOTE:
        tmp = __get_ssh_command()
        cmd_list.append(tmp)

    tmp = 'cat {0}'.format(conf_path)
    cmd_list.append(tmp)

    cmd = " ".join(cmd_list)
    logger.d('CMD: %s' % cmd)

    o = None
    if cmd != '':
        try:
            logger.d("logstash:__get_configuration:try")
            if sys.version_info < (3,):
                o = sp.check_output(cmd_list, shell=True)
            else:
                o = sp.getoutput(cmd)

        except:
            logger.w("logstash:__get_configuration:except")
            logger.w(sys.exc_info()[0])

    return o


def __set_configuration(filename):
    """ set configuration of logstash at path. """

    global conf_path, src_path

    location = __get_location()

    if location == DEF_REMOTE:
        cmd = __get_scp_command()

    if location == DEF_LOCAL:
        cmd = 'cp -f {0} {1}'.format(src_path, conf_path)

    logger.d('CMD: %s' % cmd)

    try:
        if sys.version_info < (3,):
            o = sp.check_output(cmd, shell=True)
        else:
            sp.getoutput(cmd)
    except:
        logger.w(sys.exc_info()[0])


def __restart():
    """ restart logstash.

    @return: result string
    """
    global ssh_host, ssh_port

    location = __get_location()

    cmd_list = []

    if location == DEF_REMOTE:
        tmp = __get_ssh_command()
        cmd_list.append(tmp)

    tmp = 'service logstash restart'
    cmd_list.append(tmp)

    cmd = ' '.join(cmd_list)
    logger.d('CMD: %s' % cmd)

    try:
        if sys.version_info < (3,):
            o = sp.check_output(cmd, shell=True)
        else:
            o = sp.getoutput(cmd)
    except:
        logger.w(sys.exc_info()[0])
    return o


def process(debug_mode):
    """ process. """
    global conf, src_path

    logger.DEBUG_MODE = debug_mode

    conf = __get_configuration()
    logger.d("configuration: " + json.dumps(conf))

    redis_info = __get_host_info()
    logger.d("redis info: {0}".format(str(redis_info)))

    for i in redis_info:
        chg_conf = __change_config(i, master)

        if chg_conf is not None:
            f = codecs.open(src_path, 'wb', encoding='utf-8')
            f.write(chg_conf)
            f.close()
            __set_configuration(src_path)
            o = __restart()
            logger.i(o)


if __name__ == '__main__':
    ssh_host = "10.1.1.200"
    conf_path = '/etc/logstash/conf.d/01-redis-input.conf'
    src_path = './test.conf'
    master = ("127.0.0.1", 6380)

    process(True)
