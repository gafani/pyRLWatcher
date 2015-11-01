""" flask. """

# !-*- coding: utf-8-*-

import daemon
from flask import Flask

import app as watcher

app = Flask(__name__)


@app.route("/")
def run():
    """ run. """

@app.route("/api/conf/reloaded")
def reloaded():
    """ reloaded. """
    watcher.load_configuration()
    return "completed reload configuration"


def start():
    """ start. """
    watcher.main()



if __name__ == '__main__':
    app.run(port=8487, threaded=True)
    watcher.main()

