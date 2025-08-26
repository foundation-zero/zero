# Simple Python 3.x Sample for sending CAN Frames via IP / UDP to PEAK-System Gateway 
# (c) 2022 PEAK-System technik GmbH
# This is a SAMPLE - it is NOT optimzed - it is for training - we are no Python Gurus...
# Author: U.W.
# www.peak-system.com

import socket
import time

# UDP Communication 
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Target IP of Gateway
ip = "192.168.0.30"

# used Port  (Check Route on Gateway for IP and PORT )
port = 55002

# a CAN Frame ID= 0x000C1234,Type=ext ,Length=8,Data= 8F 8E B8 0C 00 00 00 00 
# See Developer Doku for Data Structure
msg_list = [0x00, 0x24, 0x00, 0x80, 0x9d, 0x7c, 0x3c,0xd5,0xf0,0x73,0xae,0x00,0x35,0xba,0x5e,0xf3,0x00,0x05,0x40,0x50,0x00,0x08,0x00,0x02,0x80,0x0c,0x12,0x34,0x8f,0x8e,0xb8,0x0c,0x00,0x00,0x00,0x00]

# need to be converted to send
# nachricht = bytes(msg_list)

# or chage parts of the frame for your need...

# Change here the needed Information / Data
# See Developer Doku for Data Structure

# Pos 21 = DLC
msg_list[21] = 0x08

# POS 33 = Std-ID 0x00 RTR 0x01 Ext-ID 0x02 
msg_list[22:23] = 0x00, 0x00  

# Pos 24/27 = ID and RTR / Ext.
msg_list[24:27] = 0x00, 0x00, 0x02, 0x30

# Pos 28 - 35 = up to 8 Data Bytes
msg_list[28:35] = 0x45, 0x21, 0x34, 0x67, 0x98, 0x1d, 0x3f, 0xff	# DB01 to DB08

# Result is : ID 0x230, Std ID, LEN 8, Data Bytes 0x45 0x21 0x34 0x57 0x98 0x01d 0x3f 0xff 

# Transform 
nachricht = bytes(msg_list)
# and simply send it  ...as often as you want ...use a loop...

print("Send CAN Frames via UDP Socket")
print("Target IP: " + format(ip) + "  Port: " + format(port) + " ")

while True:
	s.sendto(nachricht, (ip, port)) # send Data via UDP
	time.sleep(0.25) #wait 250ms 
	# to Stop press Ctrl-C
	continue	
	
	
# close connection
s.close()


