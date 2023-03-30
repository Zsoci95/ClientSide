import socket
from datetime import datetime 
import queue
import csv 

listen_python = True # True if listening to the port which python is sending to, False if listening to the port which the C# program is sending to


if listen_python:
    UDP_PORT_LISTEN = 12345
else:
    UDP_PORT_LISTEN = 12347

UDP_ADDRESS = '127.0.0.1'
data_queue  = queue.Queue() # create a queue to store the data

def udp_listener(filename, udp_address, udp_port_listen):
    sock2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
    sock2.bind((udp_address, udp_port_listen))
    
    while True:
        bytedata = sock2.recv(1024)
        f = open(filename, "a", newline='')
        #if the file is empty, write the header 
        if f.tell() == 0:
            writer = csv.writer(f)
            writer.writerow(["quat0_w", "quat0_x", "quat0_y", "quat0_z", "quat01_w", "quat1_x", "quat1_y", "quat1_z", \
                    "quat2_w", "quat2_x", "quat2_y", "quat2_z", "acc0_x", "acc0_y", "acc0_z", "acc1_x", "acc1_y", "acc1_z", "acc2_x", "acc2_y", "acc2_z", "timestamp"])
        try:
            data_str = bytedata.decode('utf-8')
            data_split = data_str.split(',')
            if True: 
                data_queue.put(data_split)
                while not data_queue.empty():
                    writer = csv.writer(f)
                    writer.writerow(data_queue.get())
                f.close()
        except UnicodeDecodeError as e:
            print(e)

if __name__ == "__main__":
    if listen_python:
        filename = "output_python.csv"
    else:
        filename = "output_csharp.csv"
    
    udp_listener(filename, UDP_ADDRESS, UDP_PORT_LISTEN)