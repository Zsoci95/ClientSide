import asyncio
from bleak import BleakClient, BleakError
import socket
import platform
from datetime import datetime
import threading   # for the UDP listener
import csv
import queue

# Settings
device_used = 2  # 1 or 2 depending on which device you are using
sql_used = False
trusted_conn = True
os_name = platform.system()  # get the operating system name
disonnected_event = asyncio.Event()  # create an event to handle disconnections
disonnected_event.clear()  # clear the event


# Variables
if trusted_conn:  # replace with correct variables
    cnxn_str = ("Driver={SQL Server Native Client 11.0};"
                "Server=USXXX00345,67800;"
                "Database=DB02;"
                "Trusted_Connection=yes;")
else:
    conn_str = ("Driver={SQL Server Native Client 11.0};"
                "Server=USXXX00345,67800;"
                "Database=DB02;"
                "UID=Alex;"
                "PWD=Alex123;")



if sql_used:
    import pyodbc
    conn = pyodbc.connect(conn_str)  # create connection to SQL server
    cursor = conn.cursor()  # create cursor to execute SQL commands

    # Check if imu_data table exists, if not create it
    cursor.execute('''IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='imu_data' and xtype='U') 
    CREATE TABLE imu_data (timestamp TINYTEXT, quat0_w FLOAT, quat0_x FLOAT, quat0_y FLOAT, quat0_z FLOAT, 
    quat1_w FLOAT, quat1_x FLOAT, quat1_y FLOAT, quat1_z FLOAT, quat2_w FLOAT, quat2_x FLOAT, quat2_y FLOAT, quat2_z FLOAT, 
    accel0_x FLOAT, accel0_y FLOAT, accel0_z FLOAT, accel1_x FLOAT, accel1_y FLOAT, accel1_z FLOAT, accel2_x FLOAT, accel2_y FLOAT, accel2_z FLOAT)''')


if os_name == 'Windows':
    if device_used == 1:
        DEVICE_ADDRESS = "78:21:84:8A:14:F2"
    elif device_used == 2:
        DEVICE_ADDRESS = "78:21:84:8B:55:5A"
elif os_name == 'Darwin':
    if device_used == 1:
        DEVICE_ADDRESS = "F5A6EF50-BF44-B5DB-3BD0-0432180F23FF"
    elif device_used == 2:
        DEVICE_ADDRESS = "BF7B588A-F102-F7EF-5FC2-34AB0135135D"

prev_time = datetime.now()


# UUIDs for the service and characteristics that contain the data

SERVICE_UUID = "bd0f56c6-a403-4d3a-86ba-6fed11ce8473"
CHARACTERISTIC_UUID = "1fe90638-437c-490c-ad92-bda3b9423bab"
DESCRIPTOR_HANDLE = "IMU_data"
UDP_PORT_SEND = 12345
UDP_PORT_LISTEN = 12347
UDP_ADDRESS = '127.0.0.1'



data_queue = queue.Queue()  # create a queue to store the data
freq_counter = 0  # used to count the number of times the data handler is called
prev_time = datetime.now()  # used to calculate the frequency of the data handler


def data_handler(uuid, data):
    global prev_time
    curr_time = datetime.now()
    frequency = 1 / (curr_time - prev_time).total_seconds()

   
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
        try:
            data_str = bytedata.decode('utf-8')
            data_split = data_str.split(',')
            if data_split[22] == "True": 
                data_queue.put(data_split)
                while not data_queue.empty():
                    with open("output.csv", "a") as f:
                        writer = csv.writer(f)
                        writer.writerow(data_queue.get())
        except UnicodeDecodeError as e:
            print(e)

def disconnected_callback(client):
    print("Disconnected")
    disonnected_event.set()

    


async def main():
    is_notifying = False # used to make sure that the notification is only started once
    
    # try to connect to device and automatically reconnect if connection is lost
    # making sure that the nofification is only started once 
    while True:
        client = BleakClient(DEVICE_ADDRESS, disconnected_callback=disconnected_callback)
        try:
            if not client.is_connected:
                print("Connecting")
                await client.connect()
                print("Connected")
            
            await asyncio.sleep(1)
            if not is_notifying and client.is_connected:
                print("Starting notification")
                try:
                    is_notifying = True
                    print("Notification started")
                    await client.start_notify(CHARACTERISTIC_UUID, data_handler)
                except Exception as e:
                    print(e)

            
            await disonnected_event.wait()
            is_notifying = False 
            disonnected_event.clear()

            #delete the client object
            #del client
            await asyncio.sleep(6)
            

            
            
        except Exception as e:
            print(e)



thread = threading.Thread(target=udp_listener)
thread.start()



# Run the coroutine in the event loop

asyncio.run(main())
