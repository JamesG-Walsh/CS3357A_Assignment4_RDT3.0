# James Walsh   250 481 718
# CS3357A       Assignment 3
# Python 3.5.2

# Receives data from a client by implementing a reliable data transfer protocol

# import binascii
import socket
import struct
# import sys
import hashlib

UDP_IP = "127.0.0.1"
UDP_PORT = 5005
unpacker = struct.Struct('I I 8s 32s')

# Create the socket and listen
sock = socket.socket(socket.AF_INET,  # Internet
                     socket.SOCK_DGRAM)  # UDP
sock.bind((UDP_IP, UDP_PORT))

expectedSeq = 0  # variable that tracks the state

deliveredData = []

print('Ready to receive data')
while True:
    # Receive Data
    data, senderAddr = sock.recvfrom(1024)  # buffer size is 1024 bytes
    UDP_Packet = unpacker.unpack(data)
    print("\nreceived from:", senderAddr)
    print("received message:", UDP_Packet)

    values = (UDP_Packet[0], UDP_Packet[1], UDP_Packet[2])
    packer = struct.Struct('I I 8s')
    packed_data = packer.pack(*values)
    chkSum = bytes(hashlib.md5(packed_data).hexdigest(), encoding="UTF-8")  # Create the Checksum for comparison

    # Compare Checksums to test for corrupt data
    ackSeqNum = UDP_Packet[1]
    if UDP_Packet[3] == chkSum:  # packet is not corrupt
        print('CheckSum is correct')
        if UDP_Packet[1] == expectedSeq:  # packet has correct seq num
            print('Sequence Number is correct.')
            deliveredData.append(UDP_Packet[2].decode("utf-8"))  # deliver data to the destination
            expectedSeq = ((expectedSeq + 1) % 2)  # increment the sequence number
            print('Delivered Data:', deliveredData)
        else:
            print('Sequence number is incorrect.')  # no action necessary here.  the ack packet will be constructed from the flipped seq num.
    else:
        print('Checksums Do Not Match, Packet Corrupt')
        ackSeqNum = ((expectedSeq + 1) % 2)  # this ensures that the sequence number that is sent in the ACK will be opposite what was expected

    ackValues = (1, ackSeqNum, b'ACK Data')  # ackSeqNum will different than what was received if the packet was corrupt or the sequence number was unexpected
    ACK_UDP_Data = struct.Struct('I I 8s')
    packed_data = ACK_UDP_Data.pack(*ackValues)
    ackChkSum = bytes(hashlib.md5(packed_data).hexdigest(), encoding="UTF-8")  # generate checksum for the ACK

    ackValuesF = (1, ackSeqNum, b'ACK Data', ackChkSum)
    ACK_UDP_Packet_Data = struct.Struct('I I 8s 32s')
    ACK_UDP_Packet = ACK_UDP_Packet_Data.pack(*ackValuesF)  # create the ACK packet

    sock.sendto(ACK_UDP_Packet, senderAddr)
    print("\nsent to:", senderAddr)
    print("sent message:", ackValuesF)  # end of while loop

# end of script
