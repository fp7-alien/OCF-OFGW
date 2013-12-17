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
        if group != None:
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
                


def parseGroupConfig(inventory_conf="./inventory.conf", groups_conf="./groups.yaml"):
    conf_invent = open(groups_conf, 'r')
    return yaml.load(conf_invent)


if __name__ == '__main__':
    # if len(sys.argv) < 1:
    #     usage();

    parser = argparse.ArgumentParser(description="OFGW management script")
    # group = parser.add_mutually_exclusive_group()
    # parser.add_argument("list",
    #                     help="Get list of available devices",
    #                     action="store_true")
    # parser.add_argument("reboot",
    #                     help="Reboot the selected device",
    #                     action="store_true")
    # parser.add_argument("reset",
    #                     help="Restore the factory settings on device",
    #                     action="store_true")
    parser.add_argument("command",
                        choices=["list", "reboot", "reset", "config"],
                        help="Management action")
    # parser.add_argument("DEVICE_ID",
    #                     help="Device identifier",
    #                     action="store_const")
    parser.add_argument("-s", "--status",
                        help="Get device status",
                        action="store_true")
    args = parser.parse_args()
    command = args.command
    
    if command == "list":
        print "Listing devices...\n"
    elif command == "reboot":
        print "Device reboot initialized...\n"
    elif command == "reset":
        print "Reset device to factory setting initialized...\n"
    elif command == "config":
        print "Parsing the configuration...\n"
        print "Group configuration\n------------------"
        print parseGroupConfig()
        print "\nHost parameters configuration\n---------------------------"
        parser = InventoryParser()
        print parser.getParams('group1')

    # print args.accumulate(args.integers)
