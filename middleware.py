#!/usr/bin/env python3
import asyncio
from bleak import BleakClient, BleakError 
import socket
import platform 

device_used = 2

os_name = platform.system() 
if os_name == 'Windows':
    if device_used == 1:
        DEVICE_ADDRESS = "78:21:84:8A:14:F2" 
    elif device_used == 2:
        DEVICE_ADDRESS = "78:21:84:8B:55:5A"
elif os_name == 'Darwin':
    if device_used == 1:
        DEVICE_ADDRESS = "F5A6EF50-BF44-B5DB-3BD0-0432180F23FF"
    elif device_used == 2:
        DEVICE_ADDRESS = "D5F439C0-144F-7A8D-CD57-9625EF92E024"



# UUIDs for the service and characteristics that contain the data

SERVICE_UUID = "bd0f56c6-a403-4d3a-86ba-6fed11ce8473"
CHARACTERISTIC_UUID = "1fe90638-437c-490c-ad92-bda3b9423bab"
UDP_PORT = 12345
UDP_ADDRESS = '127.0.0.1'
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#sock.bind((UDP_ADDRESS, UDP_PORT))

async def data_handler(data): 
    try:
        data_str = data.decode('utf-8')
        if data_str.startswith('[') and data_str.endswith(']'):
            data_str = data_str[1:-1] # remove the first and last character
            sock.sendto(bytes(data_str, "utf-8"), (UDP_ADDRESS, UDP_PORT))
            print(data_str)
        else: 
            print("Partial packet received")
        data_list = data_str.split(',')
    except UnicodeDecodeError:
        print("UnicodeDecodeError")
    
    
   


async def run():
    client = BleakClient(DEVICE_ADDRESS)
    try:
        await client.connect()
        while True:
            data = await client.read_gatt_char(CHARACTERISTIC_UUID) 
            await data_handler(data)
    except BleakError as e: 
        print(e)
    


    


# Run the coroutine in the event loop
loop = asyncio.get_event_loop()
loop.run_until_complete(run())


