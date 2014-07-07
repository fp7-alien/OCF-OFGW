#!/usr/bin/python
#-*- coding: utf-8 -*-
"""
OFGW Management Module
This module is a part of OFGW that is an extension to
OFELIA Control Framework. It implements CLI tool for providing management
actions on non-OpenFlow capable devices.
"""

import sys
import argcomplete, argparse
import yaml
from utils import cuisine
import texttable as tt
import re

# Import hw-specific plugins
from plugins import *

class InventoryParser(object):
    """
    Inventory configuration parser
    """
    def __init__(self, filename="./inventory.conf"):
        
        self.groups = []
        self.params={}
        with open(filename) as fh:
            self.lines = fh.readlines()
        self.getGroups()
        self.getParams()
    
    def getGroups(self):
        for line in self.lines:
            line = line.split("#")[0].strip()
            if line.startswith("[") and line.endswith("]"):
                group = line.strip("[]")
                self.groups.append(group)
        return self.groups

    def getParams(self, group=None):
        currentGroup=""
        d = {}
        if group == None:
            for line in self.lines:
                line = line.split("#")[0].strip()
                if line.startswith("[") and line.endswith("]"):
                    currentGroup = line.strip("[]")
                    d[currentGroup] = []
                elif line != "":
                    t = []
                    params = line.split(" ")
                    for param in params:
                        if param != "":
                            param = param.split("=")
                            key = param[0]
                            value = param[1]
                            t.append({key:value})
                    d[currentGroup].append(t)

            self.params = d
            return self.params
        else:
            return self.params[group]

    def getDevicesHosts(self, groupParam=None):
        """
        Returns: [Host]
        @params: groupParam (str) - filter on group type
        """
        devsIP = []
        for group in self.params:
            if group == groupParam or groupParam == None:
                for param in self.params[group]:
                    for paramSpec in param:
                        if 'host' in paramSpec:
                            devsIP.append(paramSpec['host'])

        return devsIP

    def getDevicesGroupHost(self, groupParam=None):
        """
        Returns: {Host:Group}
        @params: groupParam (str) - filter on group type
        """
        devsGroupIP = {}
        for group in self.params:
            if group == groupParam or groupParam == None:
                for param in self.params[group]:
                    for paramSpec in param:
                        if 'host' in paramSpec:
                            devsGroupIP[paramSpec['host']] = group

        return devsGroupIP  

    def getDevicesIDHosts(self, groupParam=None):
        """
        Returns: [{ID:Host}]
        @params: groupParam (str) - filter on group type
        """
        deviceIDHost = []
        for group in self.params:
            if group == groupParam or groupParam == None:
                for param in self.params[group]:
                    host = ""
                    ident = ""
                    for paramSpec in param:
                        if 'host' in paramSpec:
                            host = paramSpec['host']
                        elif 'id' in paramSpec:
                            ident = paramSpec['id']  
                    paramPair = {ident:host}
                    deviceIDHost.append(paramPair)
        return deviceIDHost

    def getDevicesConcreteIDHosts(self, id=None):
        """
        Returns: Host
        @params: listIDHost (list) - list [{ID:Host}]
                 id (str) - hardware ID
        """
        listIDHost = self.getDevicesIDHosts()
        for host in listIDHost:
            if id in host.keys():
                return host[id]

    def getDevicesParam(self, id=None, param=None):
        """
        Returns: {Params}
        @params: id (str) - hardware ID
        """
        params = {}
        for group in self.params:
            for param_test in self.params[group]:
                for param_conc in param_test:
                    if 'id' in param_conc and id in param_conc['id']:
                        params = param_test
        for param_i in params:
            if param in param_i:
                return param_i[param]


    def getDevicesConcreteGroupHost(self, host=None):
        """
        Returns: Group
        @params: Host (str) - Host IP
        """
        listGroupHost = self.getDevicesGroupHost()
        return listGroupHost[host]

    def getNeighbors(self, id=None):
        """
        Returns: Neighbors
        @params: id (str) - hardware ID
        UGLY coding
        """
        neighbors = []
        for group in self.params:
            for param in self.params[group]:
                for paramSpec in param:
                    if 'id' in paramSpec:
                        if id in paramSpec['id']:
                            for paramSpec in param:
                                if 'neighbors' in paramSpec:
                                    for single_neighbor in paramSpec['neighbors'].split(';'):
                                        neighbors.append(single_neighbor)
        return neighbors


def parseGroupConfig(groups_conf="./groups.yaml"):
    """
    Device groups configuration parser
    """
    conf_invent = open(groups_conf, 'r')
    return yaml.load(conf_invent)

### TODO: Add values validation
def plugin(f):
    """
    Decorator for hw plugin
    It recognizes the proper plugin depending
    on the inventory configuration, groups configuration
    and specific hardware ID
    """
    def new_f(id):
        print "Entering", f.__name__
        ip = config.getDevicesConcreteIDHosts(id)
        hwGroup = config.getDevicesConcreteGroupHost(ip)
        hwGroup = globals()[hwGroup]
        hw = hwGroup.hwConfig(ip, config, id)
        print "Exited", f.__name__
    return new_f

### TODO: Fill functions
@plugin
def reboot(id):
    hw.reboot()

@plugin
def reset(id):
    hw.reset()

@plugin
def showPorts(id):
    print hw.showPorts(id)

def showOF():
    print "\nOpenFlow configuration\n-------------------"
    print "TODO\n"

def showTables():
    print "\nOpenFlow tables\n---------------"
    print "TODO\n"

def showNeighbors(id):
    print "\nDevice neighbors\n----------------"
    print config.getNeighbors(id)

def showSummary():
    print "\nDevice summary\n--------------"
    print "TODO\n"
#####################

def showConfig():
    print "\nGroup configuration\n------------------"
    print groups_config
    print "\nHost parameters configuration\n---------------------------"
    print config.getParams()
    print "\n"
    

def showUsers():
    cuisine.mode_local()
    tab = tt.Texttable()
    print "\nUsers\n-----"
    CMD = "cat /etc/passwd | grep \"/home\" | grep -v \"false\" |cut -d: -f1"
    users = cuisine.run_local(CMD)

    header = ['User', 'Active experiment']
    tab.header(header)

    for user in users.split("\n"):
        row = [user, 'No']  #TODO: Add active experiment status
        tab.add_row(row)
    s = tab.draw()
    print s

def listDevices(checkStatus):
    """
    Returns a graphical table with devices list
    @params: checkStatus (boolean) - if True check the device status
    """
    devs = config.getDevicesIDHosts()
    groupSearch = config.getDevicesGroupHost()
    cuisine.mode_local()
    tab = tt.Texttable()

    if checkStatus:
        
        header = ['ID', 'Host', 'Device type', 'Status', 'Ping time']
        tab.header(header)
        print "Listing devices... Checking status...\n"

        for dev in devs:
            ident = dev.keys()[0]
            host = dev[ident]
            devType = groupSearch[host]
            status = "UP"
            ping_avg = "---"
            delay = cuisine.run_local("ping -c 1 -w 1 " + host)    #TODO: Add ping timout param to local config
            match = re.search('(\d*)% packet loss', delay)
            pkt_loss = match.group(1)
            if pkt_loss=="100":
                status = "DOWN"
            else:
                status="UP"
                match = re.search('([\d]*\.[\d]*)/([\d]*\.[\d]*)/([\d]*\.[\d]*)/([\d]*\.[\d]*)', delay)
                ping_avg = match.group(2) + " ms"

            row = [ident, host, devType, status, ping_avg]
            tab.add_row(row)
    else:
        header = ['ID', 'Host', 'Device type']
        tab.header(header)
        print "Listing devices... Checking status...\n"
        for dev in devs:
            ident = dev.keys()[0]
            host = dev[ident]
            devType = groupSearch[host]
            row = [ident, host, devType]
            tab.add_row(row)

    s = tab.draw()
    print s


if __name__ == '__main__':
    # plugins.netfpga.run()
    config = InventoryParser()
    groups_config = parseGroupConfig()

    parser = argparse.ArgumentParser(description="OFGW management script")

    subparsers = parser.add_subparsers(help='Management command', dest="command")

    # List parser
    parser_list = subparsers.add_parser('list', help='List all devices')
    parser_list.add_argument("--status",
                        action="store_true",
                        help="Show device status")

    # Reboot parser
    parser_reboot = subparsers.add_parser('reboot', help='Reboot the device {DEVICE_ID}')
    parser_reboot.add_argument("DEVICE_ID",
                        help="Device identifier")

    # Factory-reset parser
    parser_fact_reset = subparsers.add_parser('fact-reset', help='Reset the device and restory the factory settings {DEVICE_ID}')
    parser_fact_reset.add_argument("DEVICE_ID",
                        help="Device identifier")

    # Show parser
    parser_show = subparsers.add_parser('show', help='Show the device configuration/status {DEVICE_ID} [--ports, --of, --tables, --neighbors]')
    parser_show.add_argument("DEVICE_ID",
                        help="Device identifier")
    parser_show.add_argument("--all",
                        action="store_true",
                        help="Show all configuration - DEFAULT parameter")
    parser_show.add_argument("--ports",
                        action="store_true",
                        help="Show port status")
    parser_show.add_argument("--of",
                        action="store_true",
                        help="Show OpenFlow configuration")
    parser_show.add_argument("--tables",
                        action="store_true",
                        help="Show OpenFlow tables dump")
    parser_show.add_argument("--neighbors",
                        action="store_true",
                        help="Show device's neighbors")
    
   # Admin parser
    parser_admin = subparsers.add_parser('admin', help='OFGW administrator tools')
    parser_admin.add_argument("admin_opt",
                    choices=['config', 'users', 'all'],
                    default="all",
                    nargs='?',
                    help="Show configurartion group")

    argcomplete.autocomplete(parser)
    args = parser.parse_args()

    command = args.command
        
    if command == "list":
        listDevices(checkStatus=args.status)

    elif command == "reboot":
        print "Device reboot initialized...\n"
        reboot(args.DEVICE_ID)

    elif command == "fact-reset":
        print "Reset device to factory setting initialized...\n"
        reset(args.DEVICE_ID)

    elif command == "show":
        print "Getting data from device...\n"
        if args.all:
            showPorts(args.DEVICE_ID)
            showOF()
            showTables()
            showNeighbors()

        elif args.ports:
            showPorts(args.DEVICE_ID)

        elif args.of:
            showOF()

        elif args.tables:
            showTables()

        elif args.neighbors:
            showNeighbors(args.DEVICE_ID)

        else:
            showSummary()

    elif command == "admin":
        admin_opt = args.admin_opt
        if admin_opt == "config":           
            showConfig()

        elif admin_opt == "users":
            showUsers()

        elif admin_opt == "all":
            showConfig()
            showUsers()

