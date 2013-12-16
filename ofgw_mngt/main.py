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
import ConfigParser


def parseConfig(inventory_conf="./inventory.ini", groups_conf="./groups.yaml"):
    conf_invent = open(groups_conf, 'r')
    print yaml.load(conf_invent)

    # Config = MyParser()
    parser = ConfigParser.ConfigParser()
    parser.read(inventory_conf)
    for section_name in parser.sections():
        print 'Section:', section_name
        print '  Options:', parser.options(section_name)
        for name, value in parser.items(section_name):
            print '  %s = %s' % (name, value)
        print

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
        parseConfig()

    # print args.accumulate(args.integers)
