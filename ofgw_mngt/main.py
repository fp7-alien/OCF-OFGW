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

def usage():
    print "USAGE: main.py <config_dir>"
    sys.exit(1);

if __name__ == '__main__':
    # if len(sys.argv) < 1:
    #     usage();
    parser = argparse.ArgumentParser(description="OFGW management script")
    parser.add_argument("command",
                        choices=["list", "reboot", "reset"],
                        help="Management action")
    parser.add_argument("DEVICE_ID", help="Device identifier")
    parser.add_argument("-s", "--status",
                        help="Get device status",
                        action="store_true")
    args = parser.parse_args()
    # print args.accumulate(args.integers)
