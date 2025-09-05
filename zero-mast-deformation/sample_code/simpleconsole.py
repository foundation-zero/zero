#! /usr/bin/env python
#
#simpleconsole.py
#
#Copyright (c) 2018 by Micron Optics, Inc.  All Rights Reserved
#
"""This will open a simple command console from the command line.
Usage: simpleconsole.py ipaddress
ipaddress is a string and should be enclosed in quotations: eg. "192.168.2.6"
"""
import sys
import hyperion

if len(sys.argv) < 2:
    print("Usage: simpleconsole.py ipaddress")
    exit()

ipAddress = sys.argv[1]

response = hyperion.HCommTCPClient.hyperion_command(ipAddress, '#GetSerialNumber')

print(response.message)

promptString = "hyp:" + response.content.decode() + ">"

command = input(promptString)
while command != "exit":
    if len(command) == 0:
        pass
    elif command[0] != "#":
        print("""Hyperion Commands begin with #.  Use #help for complete list
        of valid commands.  Type "exit" to close the console.""")
    else:
        pCommand = command.partition(" ")
        try:
            response = hyperion.HCommTCPClient.hyperion_command( ipAddress, pCommand[0], pCommand[2])
        except hyperion.HyperionError as e:
            print("Hyperion Error " + e.string)
        else:
            print(response.message)
        
    command = input(promptString)



            

