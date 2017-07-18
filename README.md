Elastic search with logstash Wacher
===================================

이 프로그램은 logstash의 Input으로 Redis를 가지는 환경에서 Redis가 Failover 했을 때 logstash의 input값을 Redis의 Master로 변경한 후 재시작해주는 유틸성 프로그램이다.
이 프로그램은 sentinel 3개와 redis master와 slave 두개로 구성한 환경. 그리고 이 redis cluster를 바라보고 input으로 가져오는 logstash master, slave 구성에서 redis master가 down되어 slave로 바뀌면 rlwatcher가 sentinel로 부터 주기적으로 확인해서 logstash의 input host값을 현재 redis master 값으로 변경한후 logstash를 재시작한다. 

>This program is a utility program that changes the input value of logstash to Redis Master when Redis fails over in the environment where Redis is input as logstash input.
>This program consists of three sentinel, redis master and slave environment. If the redis master is down and converted to slave in the master/slave configuration, the rlwatcher checks periodically from the sentinel, changes the input host value of logstash to the current redis master value, Restart.



Pre Require
------------
Python 3.4.x or 2.7.x


Runtime Environments
--------------------
  - OS: Windows7 x64, Linux x64
  - Python: x64 (2.7.x, 3.4.x)


Depend on Python Packages
-------------------------
requirement.txt 파일 참조

Usage
-----
사용법은 다음과 같다:

```bash
$ python3 dm.py --help
Usage: dm.py [OPTIONS] CONF_PATH

  command line interface.

Options:
  -d, --debug    debug mode
  -s, --service  service mode
  --help         Show this message and exit.
```


 - -d, --debug: 디버그 모드로 실행. 처리 흐름에 따라 관련 정보를 노출 한다.
 - -s, --service: 서비스 모드로 실행. 데몬으로 띄운다. (Run in service mode. as a daemon)
 - CONF_PATH: configuration 파일의 경로와 파일 이름을 **반드시** 입력해야한다. (You must enter the path and file name of the configuration file.)


 Configuration
 -------------
 환경 설정 구성에 대해 알아보겠다. 환경 설정은 json format으로 된 text 파일이며 각 항목은 다음과 같다.
 >Let's take a look at configuring preferences. The environment setting is a text file in json format, and each item is as follows.

  - saved_conf_filename: 지정된 logstash의 환경 설정파일을 교체할 파일이다. 즉, redis가 failover가 되면 master 정보가 바뀌기 때문에 그 바뀐, 적용할 logstash의 설정파일이다. `conf_path`에 지정된 환경설정 파일을 기반으로 수정된다. (This is the file to replace the configuration file of the specified logstash. That is, when redis fails over, it changes the master information, so it is a configuration file of the logstash to be changed. It is modified based on the configuration file specified in `conf_path`.)
  - log_file: 이 프로그램이 동작하면 log를 남기기 위한 파일이다. **service mode**에서만 동작한다. (It is a file to log when this program runs. It only works in ** service mode **.)
  - period: 이 프로그램이 주기적으로 검사하는 시간을 설정한다. 초단위이다. (Set the time period for this program to periodically check. In seconds.)
  - logstash: logstash 관련 설정들이다. 
      + sentinel_master: sentinel에 등록된 master 식별 이름을 설정해야한다.
      + sentinel: sentinel 목록들을 설정한다. 이 프로그램은 랜덤으로 물어본다.
      + ssh: 이 프로그램이 logstash와 같은 공간이 아닌 원격지에 있을 때 logstash 머신에 ssh를 통해 처리하기 위한 정보이다.
          * host: ssh host
          * port: ssh port
          * user: ssh user
          * id_file: ssh id file
      + conf_path: target logstash의 환경 설정 파일 경로


Example
-------
Daemon으로 동작시키는 방법과 Crontab에 의존해 동작시키는 방법 두가지가 있다.
Daemon으로 동작시킬때는 -s 옵션을 주면 되며, 이 때 반복 주기는 환경설정의 `period`의 시간 간격으로 반복된다. 

> There are two ways to run as a Daemon and depending on Crontab.
> When running as a Daemon, you can use the -s option, and the repetition period is repeated in the `period` time interval of the environment setting.

```bash
$ python dm.py -s ../conf_json
```

Note! 만일 crontab으로 처리할 경우 별도의 로그 파일을 생성하지 않기 때문에 redirection 을 통해서 따로 저장해야한다.
> Note! If crontab does not generate a separate log file, it must be saved separately through redirection.

License
=======

MIT
