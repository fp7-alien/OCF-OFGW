#!/usr/bin/python
#-*- coding: utf-8 -*-
"""
OFGW Management Module
This module is a part of OFGW that is an extension to
OFELIA Control Framework. It contains CLI tool for providing management
actions on non-OpenFlow capatible devices.
"""

import sys
import argparse
import yaml

class InventoryParser(object):
    """Inventory configuration parser"""
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


def parseGroupConfig(inventory_conf="./inventory.conf", groups_conf="./groups.yaml"):
    conf_invent = open(groups_conf, 'r')
    return yaml.load(conf_invent)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="OFGW management script")

    subparsers = parser.add_subparsers(help='Management command', dest="command")

    # List parser
    parser_list = subparsers.add_parser('list', help='List all devices')
    print parser_list

    # Reboot parser
    parser_reboot = subparsers.add_parser('reboot', help='Reboot the device [DEVICE_ID]')
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
    
    args = parser.parse_args()

    command = args.command
       
    
    if command == "list":
        print "Listing devices...\n"
    elif command == "reboot":
        print "Device reboot initialized...\n"
    elif command == "factory-reset":
        print "Reset device to factory setting initialized...\n"
    elif command == "config":
        print "Parsing the configuration...\n"
        if groupsBool:           
            print parseGroupConfig()
            sys.exit()
        else:
            print "Group configuration\n------------------"
            print parseGroupConfig()
            print "\nHost parameters configuration\n---------------------------"
            parser = InventoryParser()
            print parser.getParams(group)

