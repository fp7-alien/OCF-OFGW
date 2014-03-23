import logging
import time

from daemon import runner
from flask import Flask, json
app = Flask("ofgw_mngt")

@app.route('/of-table')
def get_of_table():
    return json.dumps({'error' : 'no data'})

@app.route('/port-satus')
def get_port_status():
    return json.dumps({'error' : 'no data'})

class App():
    
    def __init__(self):
        self.stdin_path = '/dev/null'
        self.stdout_path = '/dev/tty'
        self.stderr_path = '/dev/tty'
        self.pidfile_path =  '/tmp/ofgw_mngt.pid'
        self.pidfile_timeout = 5
            
    def run(self):
        app.run()


RESTapp = App()
logger = logging.getLogger("ofgw-mngt")
logger.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler = logging.FileHandler("/tmp/ofgw_mngt.log")
handler.setFormatter(formatter)
logger.addHandler(handler)

daemon_runner = runner.DaemonRunner(RESTapp)
daemon_runner.daemon_context.files_preserve=[handler.stream]
daemon_runner.do_action()