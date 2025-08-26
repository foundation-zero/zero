# Simple Python 3.x Sample for receiving CAN Frames via IP / UDP to PEAK-System Gateway 
# (c) 2022 PEAK-System technik GmbH
# This is a SAMPLE - it is NOT optimzed - it is for training - we are no Python Gurus...
# Author: U.W.
# www.peak-system.com

from ctypes.wintypes import BYTE
import socket
from turtle import end_fill

# change for your need 
localIP     = "192.168.0.2"
localPort   = 55001
# buffer for payload in IP Frame
bufferSize  = 1024
DLC_to_LEN = [0,1,2,3,4,5,6,7,8,12,16,20,24,32,48,64]

##########################################################################################
# Simple function to decode first CAN Frame in package - need to be extend for your need #
# not included until now is the support of multple CAN Frames in one package             #
# (check package size in Byte 1/2)                                                       #
##########################################################################################

def Decode_CAN_IP_Data( message ):
	# Check type of CAN Frame - here done by directly check he single byte of IP Frame
	if message[3] == 0x80 :
		print ("CAN 2.0a/b Frame ", end=''  )
	elif message[3] == 0x81 :
		print ("CAN 2.0a/b Frame with CRC ", end=''  )
	elif message[3] == 0x90 :
		print ("CAN FD Frame ", end=''  )
	elif message[3] == 0x91 :
		print ("CAN FD Frame with CRC ", end=''  )		
	else:
		print ("no CAN Frame" )
		return
	
	# Get the CAN Msg Flags (Ext. dat Lenght , Bit Rate Switch, Error State Indicator, Ext. ID )
	# here done by converting the 2 bytes to a int Value...Big Endian, unsigned
	CAN_MSG_FLAG = int.from_bytes(message[22:24],byteorder='big', signed=False) # Byte 22 and 23
	if CAN_MSG_FLAG & 0x40 :
		print ("Error State Indicator set ", end='')

	if CAN_MSG_FLAG & 0x20 : 
		print ("Bit Rate Switch aktive ", end='')

	if CAN_MSG_FLAG & 0x10 : 
		print ("Frame use Extended Data Lenght ", end='')		
	
		
	# Get the CAN-ID Field (inkl. the MSG Type Info)
	CAN_ID_NUM  = int.from_bytes(message[24:28],byteorder='big', signed=False) # Byte 24 to 27
	# Get Bit 29 to 31 only  --> RTR / EXT
	CAN_MSG_Type = CAN_ID_NUM & 0xC0000000 # Mask it 
	CAN_MSG_Type = CAN_MSG_Type >> 24 # Shift it 

	if CAN_MSG_Type & 0x80 : 
		print ("Ext 29 Bit")			
	else: 
		print ("Std 11 Bit")

	if CAN_MSG_Type & 0x40 : 
		print ("RTR")	
	
	# Mask Out the Bit 29 to 31 --> RTR / EXT
	CAN_ID_NUM = CAN_ID_NUM & 0x3FFFFFFF 
	print("CAN ID: " + "0x" + '{:x}'.format(CAN_ID_NUM) + " ", end='')

	# Get the DLC 
	DLC = message[21] # place of the DLC Information
	print("CAN DLC: " + format(DLC) +" ", end='')
	
	# using CAN FD DLC is NOT Lenght - convert it first - if less / eq 8 - keep it as it is...!
	LEN = DLC_to_LEN[DLC]
	if LEN>8: # only if we use CAN-FD and receive a DLC >8 teh D>LC is not the Length
		print("CAN Data Byte counter: " + format(LEN), end='')
	
	# Loop to all available Data and print (max. 8 DB in a row)
	i=1
	print("\nData Bytes: ")
	while (i <= LEN):
		print("DB[" + '{:02d}'.format(i-1) + "]:" + "0x" + '{:02X}'.format(message[27+i]) + " ", end='' ) #27+1 --> Place of DB0
		if (i % 8) == 0 : # limit to max 8 DB in one row
			print("")
		i = i + 1

	print("\n------------------------------------------------------------------------------\n")
	
	

##########
# main...
##########

# Create a datagram socket
UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

# Bind to address and ip
UDPServerSocket.bind((localIP, localPort))
print("UDP server up and listening")

# Listen for incoming datagrams
while(True):
	# get the Data Package
	bytesAddressPair = UDPServerSocket.recvfrom(bufferSize)
	message = bytesAddressPair[0]
	address = bytesAddressPair[1]
	clientMsg = "Data from Gateway:{}".format(message)
	clientIP  = "Gateway IP Address:{}".format(address[0])
	clientPort  = "Port:{}".format(address[1])
	print(clientIP + " " + clientPort)
	# call the Package decoder.....
	Decode_CAN_IP_Data(message)
	# ...do what you want / need 
	# print(clientMsg)
    # or sending a reply to client
    # UDPServerSocket.sendto(bytesToSend, address)


