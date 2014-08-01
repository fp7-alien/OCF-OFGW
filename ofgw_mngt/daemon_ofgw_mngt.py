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

from flask import Flask, jsonify, Response
import yaml

from daemon import runner
from ofgw_main import InventoryParser

## Open OFGW MG configuration
config = InventoryParser()

## Import example json response from POX ##
json_data=open('pox_response.json')

data_of = json.load(json_data)
json_data.close()

## Import example port status ##
json_data=open('port_status.json')

data_port = json.load(json_data)
json_data.close()

# Neighbours configuration  file
f_neighbours = open("./neighbours.yaml", 'r')
neighbours = yaml.load(f_neighbours)
f_neighbours.close()


## RESTful service ##
app = Flask("ofgw-mngt")


@app.route('/api/help', methods = ['GET'])
def help():
    """Print available functions."""
    func_list = {}
    for rule in app.url_map.iter_rules():
        if rule.endpoint != 'static':
            func_list[rule.rule] = app.view_functions[rule.endpoint].__doc__
    return jsonify(func_list)

@app.route('/of-table-raw')
def get_of_table_raw():
    """Raw message from POX"""
    resp = json.dumps(data_of)
    return Response(response=resp, status=None, headers=None, mimetype='application/json', content_type=None, direct_passthrough=False)

@app.route('/of-table')
def get_of_table():
    """Processed OF-table dump"""
    resp = json.dumps(data_of['result'])
    return Response(response=resp, status=None, headers=None, mimetype='application/json', content_type=None, direct_passthrough=False)

@app.route('/of-table/dpid/<dpid>')
def show_user_profile(dpid):
    """OF-table dump filtered by DPID"""
    data = data_of['result']
    currentDPID = data['dpid']
    if currentDPID == dpid:
        resp = json.dumps(data)
        return Response(response=resp, status=None, headers=None, mimetype='application/json', content_type=None, direct_passthrough=False)
    else:
        return Response(response=None, status=404, headers=None, mimetype='application/json', content_type=None, direct_passthrough=False)

@app.route('/port-status/id/<id>')
def get_port_status(id):
    """Port status"""
    resp = json.dumps(data_port)
    return Response(response=resp, status=None, headers=None, mimetype='application/json', content_type=None, direct_passthrough=False)

@app.route('/hosts')
def get_hosts():
    """Get hosts under OCF control"""
    hosts = config.getDevicesIDHosts()
    resp = json.dumps(hosts)
    return Response(response=resp, status=None, headers=None, mimetype='application/json', content_type=None, direct_passthrough=False)

@app.route('/neighbours')
def get_neighbours():
    """Get all devices' neighbours"""
    resp = json.dumps(neighbours)
    return Response(response=resp, status=None, headers=None, mimetype='application/json', content_type=None, direct_passthrough=False)

@app.route('/neighbours/dpid/<dpid>')
def get_concrete_neighbours(dpid):
    """Get concrete device neighbours specified by 'dpid' parameter"""
    for device in neighbours:
        c_dpid = neighbours[device]['dpid']
        if dpid in c_dpid:
            resp = json.dumps(neighbours[device]['ports'])
            return Response(response=resp, status=None, headers=None, mimetype='application/json', content_type=None, direct_passthrough=False)
    return Response(response=None, status=404, headers=None, mimetype='application/json', content_type=None, direct_passthrough=False)

@app.route('/neighbours/id/<id>')
def get_concrete_neighbours_id(id):
    """Get concrete device neighbours specified by 'id' parameter"""
    for device in neighbours:
        if id in device:
            resp = json.dumps(neighbours[device]['ports'])
            return Response(response=resp, status=None, headers=None, mimetype='application/json', content_type=None, direct_passthrough=False)
    return Response(response=None, status=404, headers=None, mimetype='application/json', content_type=None, direct_passthrough=False)

## Daemon application ##
class App():
    
    def __init__(self):
        self.stdin_path = '/dev/null'
        self.stdout_path = '/dev/tty'
        self.stderr_path = '/dev/tty'
        self.pidfile_path =  '/tmp/ofgw_mngt.pid'
        self.pidfile_timeout = 5
            
    def run(self):
        # logger.info('Starting RESTful server')
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