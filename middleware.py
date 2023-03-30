import asyncio
from bleak import BleakClient, BleakError
import socket
import platform
from datetime import datetime
import threading   # for the UDP listener
import csv
import queue
#import pymysql as sql

# Settings
device_used = 2  # 1 or 2 depending on which device you are using
sql_used = False
trusted_conn = True
os_name = platform.system()  # get the operating system name
disonnected_event = asyncio.Event()  # create an event to handle disconnections
disonnected_event.clear()  # clear the event


# Variables


if sql_used:
    db = sql.connect(
        host="localhost",
        user="user",
        passwd="password",
        database="database"
    )
    cursor = db.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS imu_data (quat0_w, quat0_x, quat0_y, quat0_z, quat01_w, quat1_x, quat1_y, quat1_z, \
                    quat2_w, quat2_x, quat2_y, quat2_z, acc0_x, acc0_y, acc0_z, acc1_x, acc1_y, acc1_z, acc2_x, acc2_y, acc2_z, timestamp TINYTEXT)")



if os_name == 'Windows':
    if device_used == 1:
        DEVICE_ADDRESS = "78:21:84:8A:14:F2"
    elif device_used == 2:
        DEVICE_ADDRESS = "78:21:84:8B:55:5A"
elif os_name == 'Darwin':
    if device_used == 1:
        DEVICE_ADDRESS = "0E1CA921-BE69-8FEA-9711-91E4997E8BD4"
    elif device_used == 2:
        DEVICE_ADDRESS = "BF7B588A-F102-F7EF-5FC2-34AB0135135D"




# UUIDs for the service and characteristics that contain the data

SERVICE_UUID = "bd0f56c6-a403-4d3a-86ba-6fed11ce8473"
CHARACTERISTIC_UUID = "1fe90638-437c-490c-ad92-bda3b9423bab"
DESCRIPTOR_HANDLE = "IMU_data"
UDP_PORT_SEND = 12345
UDP_PORT_LISTEN = 12345
UDP_ADDRESS = '127.0.0.1'



data_queue = queue.Queue()  # create a queue to store the data
freq_counter = 0  # used to count the number of times the data handler is called
prev_time = datetime.now()  # used to calculate the frequency of the data handler


def data_handler(uuid, data):
    global prev_time
    curr_time = datetime.now()
    #frequency = 1 / (curr_time - prev_time).total_seconds()

   
    prev_time = curr_time
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # create UDP socket

    try:  # try to decode the data, if it fails, throw exception
        data_str = data.decode('utf-8')  # convert the data to a string
        timestamp = datetime.now()  # get the current time and date down to the microsecond

        if data_str.endswith(']') and (data_str.startswith('[') or data_str[0] == '\x00'):
            if data_str[0] == '\x00':
                data_str = data_str[:-1]  # remove the last character
            elif data_str.startswith('['):
                # remove the first and last character
                data_str = data_str[1:-1]
            print(data_str)   
            data_str += ',' + str(timestamp)  # add the timestamp to the end of the string
            sock.sendto(bytes(data_str, "utf-8"), (UDP_ADDRESS, UDP_PORT_SEND))
        
            data_list = data_str.split(',')
            
        else:
            print("ERROR")   

    except UnicodeDecodeError:
        print("UNICODE ERROR")

# indefinitely try to connect to the device and read the data

def udp_listener():
    sock2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
    sock2.bind((UDP_ADDRESS, UDP_PORT_LISTEN))
    
    while True:
        bytedata = sock2.recv(1024)
        f = open("output.csv", "a", newline='')
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

def disconnected_callback(client):
    print("Disconnected")
    disonnected_event.set()

    


async def main():
    
    # try to connect to device and automatically reconnect if connection is lost
    # making sure that the nofification is only started once 
    while True:
        client = BleakClient(DEVICE_ADDRESS, disconnected_callback=disconnected_callback, timeout=1000)
        print("Conneting")
        await client.connect()
        print("Connected at:", datetime.now())

        while True:
            print("Notification started")
            await client.start_notify(CHARACTERISTIC_UUID, data_handler)
            
        
            await disonnected_event.wait()

            disonnected_event.clear()
            
            print("Client disconnected at: ", datetime.now())
            break


            
    


thread = threading.Thread(target=udp_listener)
thread.start()



# Run the coroutine in the event loop

asyncio.run(main())
