""" RL Wachter. """

# !-*-coding: utf-8 -*-

# #############################################################################
# Built-in
# #############################################################################
import codecs
import os
import sys
import json
import re
import time
from datetime import datetime
import random

# #############################################################################
# Thrid party
# #############################################################################
try:
    import jsontree
except:
    from utils import jsontree


# #############################################################################
# Inline
# #############################################################################
import sentinel
import logstash
import logger

# #############################################################################
# User Definitaion
# #############################################################################
VER = (0, 0, 1)

DEF_LOG_FILE = './RL_Watcher.log'
DEF_CONF_FILE = '../conf.json'

DEF_LOGSTASH = 'logstash'
DEF_SSH = 'ssh'
DEF_CONF_PATH = 'conf_path'

DEF_HOST = 'host'
DEF_PORT = 'port'

DEF_MASTER_ID = 'mymaster'
DEF_DEBUG_MODE = False

MAX_LOG_FILESIZE = 1024 * 1024 * 10   ## 10MB
CONF = None


def read_configuration_file(file_name):
    """ open configuration file.

    @param file_name: (str) configuration file name
    @return (json object) environment
    """
    logger.d("[read_configuration_file prcoess]")
    logger.d("filename -> %s" % file_name)

    try:
        fp = codecs.open(file_name, mode='rb', encoding='utf-8')
        c = fp.read()
        fp.close()
    except:
        print("Error: ", sys.exc_info()[0])
    jo = jsontree.loads(c, encoding='utf-8')

    return jo


def chagne_logstash_conf(master_ip, master_port):
    """ chagne logstash configuration.

    @param master_ip: (str) redis master ip.
    @param master_port: (str) redis master port.
    """
    global CONF, DEF_DEBUG_MODE

    logger.d("[change_logstash_conf prcoess]")

    cls = CONF.logstash

    # ### Init Logstash
    ssh = cls.ssh

    host = ssh['host']
    conf_path = cls.conf_path
    filename = CONF.saved_conf_filename
    logstash.src_path = filename
    logstash.master = (master_ip, master_port)

    if cls.ssh.id_file is not None or cls.ssh.id_file != "":
        ssh_id_filename = cls.ssh.id_file
        if ssh_id_filename == '':
            logstash.ssh_id_file = None
        else:
            logstash.ssh_id_file = ssh_id_filename

    if ssh.user is not None:
        ssh_user = ssh.user
        if ssh_user == '':
            logstash.ssh_user = None
        else:
            logstash.ssh_user = ssh_user

    logstash.ssh_host = host
    logstash.conf_path = conf_path

    logstash.process(DEF_DEBUG_MODE)


def load_configuration():
    """ load configuration. """
    global CONF

    CONF = read_configuration_file(DEF_CONF_FILE)
    logger.d("app.py:load_configuration:CONF: {0}".format(CONF))

    # Validation Configuration values
    if CONF.saved_conf_filename is None:
        CONF.saved_conf_filename = './changed_logstash.conf'

    if CONF.log_file is None or not len(CONF.log_file):
        CONF.log_file = './rl_watcher.log'

    if CONF.period is None:
        CONF.period = 60

    if CONF.logstash is None or not len(CONF.logstash):
        return 1
    else:
        if CONF.logstash.sentinel is None or not len(CONF.logstash.sentiel):
            return 2
        if CONF.logstash.ssh is None or not len(CONF.logstash.sentinel):
            CONF.logstash.ssh.host = "127.0.0.1"
            CONF.logstash.ssh.port = 22

    if CONF.conf_path is None or len(CONF.conf_path):
        CONF.conf_path = '/etc/logstash/conf.d/logstash.conf'

    logger.d("complete %s configuration" % DEF_CONF_FILE)


def main(debug_mode, repeat):
    """ main process. """
    global CONF, DEF_DEBUG_MODE

    DEF_DEBUG_MODE = debug_mode

    logger.DEBUG_MODE = debug_mode
    load_configuration()
    logstash = CONF.logstash
    sentinel_num = len(logstash.sentinel)

    if logstash.sentinel_master is not None:
        DEF_MASTER_ID = logstash.sentinel_master

    while True:
        logger.d("")
        logger.d("=" * 80)
        logger.d("[Loop Watch] Start")
        logger.d("-" * 80)
        i = logstash.sentinel[random.randint(0, sentinel_num-1)]
        logger.d("sentinel info: {0}".format(i))
        s = sentinel.get_session(i.host, i.port)
        logger.d("sentinel session: {0}".format(s))
        m = sentinel.get_master(s, DEF_MASTER_ID)
        logger.d("master info: {0}".format(m))

        # ### Change logstash configuration
        if m is not None:
            chagne_logstash_conf(m[0], m[1])
        else:
            logger.w("Check Master Name or Slave Failed")

        if repeat:
            time.sleep(float(CONF.period))
        else:
            break
        logger.d("-" * 80)
        logger.d("[Loop Watch] End")


if __name__ == '__main__':
    # print(sys.path)
    # print(os.path.dirname(os.path.realpath(__file__)))
    main(True)

    sample = """
input {
    redis {
        host => "stg-dasp-redis001"
        port => 6379
        password => "diotekredisservice"
        data_type => "list"
        key => "dasp-api-log"
        codec => json
        type => "dasp-api-log"
    }

    redis {
        host => "stg-dasp-redis002"
        port => 6379
        password => "diotekredisservice"
        data_type => "list"
        key => "dasp-tts-log"
        codec => json
        type => "dasp-tts-log"
    }
}

filter {
    json {
        source => "message"
    }
    mutate {
        remove => ["mRequestNum", "mHeaderMap.Authentication-key", "mHeaderMap.Authentication-secret"]
    }
}

output {
     stdout {
        codec => rubydebug codec => json
     }

     if [type] == "dasp-api-log" {
        elasticsearch {
            host => "localhost"
            port => 9300
            index => "dasp-api-index-%{+YYYY-MM}"
            index_type => "dasp-api-log"
            cluster => "dasp-es-cluster"
            node_name => "dasp-es-1"
        }
    }
    if [type] == "dasp-tts-log" {
        elasticsearch {
            host => "localhost"
            port => 9300
            index => "dasp-api-index-%{+YYYY-MM}"
            index_type => "dasp-tts-log"
            cluster => "dasp-es-cluster"
            node_name => "dasp-es1"
            template_overwrite => true
        }
    }
}

    """
    # ips = re.findall('.+?redis.+?host.+?=>(.+?)\\n.+?port.+?=>(.+?)\\n.+?}', sample, re.S)
    # for i, item in enumerate(ips):
    #     ips[i] = (item[0].strip(), item[1].strip())
    # print(ips)

    # convert = re.sub(
    #     '(redis.+?{.+?host.+?=>.+?)stg-dasp-redis001(.+?\\n.+?port.+?=>.+?)6379(.+?\\n.+?})',
    #     r'\1test\2"6800"\3',
    #     sample,
    #     flags=re.S)
    # print(convert)

    # convert = re.sub(
    #         '(input.+?redis.+?{.+?host.+?=>.+?)stg-dasp-redis001(.+?})',
    #         r'\1test007\2',
    #         sample,
    #         flags=re.S
    #     )
    # print(convert)
