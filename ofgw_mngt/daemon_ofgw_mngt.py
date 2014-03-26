import logging
import time

import json

from daemon import runner
from flask import Flask

## Import example json response from POX ##
json_data=open('pox_response.json')

data_of = json.load(json_data)
json_data.close()

## Import example port status ##
json_data=open('port_status.json')

data_port = json.load(json_data)
json_data.close()

## RESTful service ##
app = Flask("ofgw-mngt")

# Raw message from POX
@app.route('/of-table-raw')
def get_of_table_raw():
    return json.dumps(data_of)

# Processed message
@app.route('/of-table')
def get_of_table():
    return json.dumps(data_of['result'])

# Port status
@app.route('/port-status')
def get_port_status():
    return json.dumps(data_port)

## Daemon application ##
class App():
    
    def __init__(self):
        self.stdin_path = '/dev/null'
        self.stdout_path = '/dev/tty'
        self.stderr_path = '/dev/tty'
        self.pidfile_path =  '/tmp/ofgw_mngt.pid'
        self.pidfile_timeout = 5
            
    def run(self):
        app.logger.debug('Starting RESTful server')
        app.run()


RESTapp = App()
logger = logging.getLogger("ofgw-mngt")
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

handler = logging.FileHandler("/tmp/ofgw_mngt.log")
handler.setFormatter(formatter)
logger.addHandler(handler)


daemon_runner = runner.DaemonRunner(RESTapp)
daemon_runner.daemon_context.files_preserve=[handler.stream]
daemon_runner.do_action()