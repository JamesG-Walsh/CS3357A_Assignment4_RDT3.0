# James Walsh   250 481 718
# CS3357A       Assignment 3
# Python 3.5.2

# Sends data to a server by implementing a reliable data transfer protocol

import binascii
import socket
import struct
import sys
import hashlib

UDP_IP = "127.0.0.1"
UDP_PORT = 5005

print("UDP target IP:", UDP_IP)
print("UDP target port:", UDP_PORT)

payloads = [b'NCC-1701', b'NCC-1664', b'NCC-1017']

seqNum = 0  # tracks the state of the client

for pl in payloads:
    # Create the Checksum
    values = (0, seqNum, pl)
    UDP_Data = struct.Struct('I I 8s')
    packed_data = UDP_Data.pack(*values)
    chkSum = bytes(hashlib.md5(packed_data).hexdigest(), encoding="UTF-8")

    # Build the UDP Packet
    values = (0, seqNum, pl, chkSum)
    UDP_Packet_Data = struct.Struct('I I 8s 32s')
    UDP_Packet = UDP_Packet_Data.pack(*values)

    packetAcknowledged = False
    while not packetAcknowledged:  # loop until packet is successfully acknowledged
        try:
            print("\n\nSending message:\t", values)
            print("Sending to:\t\t\t", (UDP_IP, UDP_PORT))
            sock = socket.socket(socket.AF_INET,  # Internet
                         socket.SOCK_DGRAM)  # UDP
            sock.sendto(UDP_Packet, (UDP_IP, UDP_PORT))  # Send the UDP Packet
            sock.settimeout(9)  # set the timer

            ackData, recAddr = sock.recvfrom(1024)  # receive the ACK. buffer size is 1024 bytes.
            ACK_UDP_Packet = UDP_Packet_Data.unpack(ackData)
            print("\nreceived from:\t\t", recAddr)
            print("received message:\t", ACK_UDP_Packet)

            ackValues = (ACK_UDP_Packet[0], ACK_UDP_Packet[1], ACK_UDP_Packet[2])
            packer = struct.Struct('I I 8s')
            packed_ackData = packer.pack(*ackValues)
            ackChkSum = bytes(hashlib.md5(packed_ackData).hexdigest(), encoding="UTF-8")  # generate checkSum from the ACK that was received

            if (ACK_UDP_Packet[3] == ackChkSum) and (ACK_UDP_Packet[1] == seqNum):  # packet is not corrupt and sequence num is correct
                print('CheckSum is Correct')
                print('Sequence Number is correct.')
                seqNum = ((seqNum + 1) % 2)  # increment the sequence number.
                packetAcknowledged = True  # ends inner loop.  next packet will be sent in next iteration of outer loop
            else:
                if ackChkSum != ACK_UDP_Packet[3]:
                    print('Checksums do not match. Packet corrupt.')
                if ACK_UDP_Packet[1] != seqNum:
                    print('Sequence Number is incorrect')
                sock.sendto(UDP_Packet, (UDP_IP, UDP_PORT))  # retransmit packet. end of inner loop.
        except socket.timeout:
            print("socket timeout.  retransmitting")
