#!/usr/bin/python
#-*- coding: utf-8 -*-
"""
OFGW Management Module
This module is a part of OFGW that is an extension to
OFELIA Control Framework. It contains a RESTful service for getting status of managed devices.
"""

import logging
import time

import json

from daemon import runner
from flask import Flask
from flask import Response

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
    resp = json.dumps(data_of)
    return Response(response=resp, status=None, headers=None, mimetype='application/json', content_type=None, direct_passthrough=False)

# Processed OF-table dump
@app.route('/of-table')
def get_of_table():
    logger.debug('Test')
    resp = json.dumps(data_of['result'])
    return Response(response=resp, status=None, headers=None, mimetype='application/json', content_type=None, direct_passthrough=False)

# OF-table dump filtered by DPID 
@app.route('/of-table/dpid/<dpid>')
def show_user_profile(dpid):
    data = data_of['result']
    currentDPID = data['dpid']
    app.logger.info('test')
    if currentDPID == dpid:
        resp = json.dumps(data)
        return Response(response=resp, status=None, headers=None, mimetype='application/json', content_type=None, direct_passthrough=False)
    else:
        return Response(response=None, status=404, headers=None, mimetype='application/json', content_type=None, direct_passthrough=False)

# Port status
@app.route('/port-status')
def get_port_status():
    resp = json.dumps(data_port)
    return Response(response=resp, status=None, headers=None, mimetype='application/json', content_type=None, direct_passthrough=False)

## Daemon application ##
class App():
    
    def __init__(self):
        self.stdin_path = '/dev/null'
        self.stdout_path = '/dev/tty'
        self.stderr_path = '/dev/tty'
        self.pidfile_path =  '/tmp/ofgw_mngt.pid'
        self.pidfile_timeout = 5
            
    def run(self):
        logger.info('Starting RESTful server')
        app.debug = False
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