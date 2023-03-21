import asyncio
import socket
from datetime import datetime 


UDP_PORT = 12347
UDP_ADDRESS = '127.0.0.1'


for int in range(0, 1000):
    timestamp = datetime.now()
    string = "0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,{},true,false".format(timestamp)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # create UDP sock
    sock.sendto(bytes(string, "utf-8"), (UDP_ADDRESS, UDP_PORT))
