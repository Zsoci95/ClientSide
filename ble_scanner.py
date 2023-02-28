#!/usr/bin/env python3
import asyncio
from bleak import BleakClient, BleakError 
import socket

# UUIDs for the service and characteristics that contain the data
DEVICE_ADDRESS = "78:21:84:8A:14:F2"
SERVICE_UUID = "bd0f56c6-a403-4d3a-86ba-6fed11ce8473"
CHARACTERISTIC_UUID = "1fe90638-437c-490c-ad92-bda3b9423bab"
UDP_PORT = 12345
UDP_ADDRESS = '127.0.0.1'
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#sock.bind((UDP_ADDRESS, UDP_PORT))

async def data_handler(data): 
    try:
        data_str = data.decode('utf-8')
        sock.sendto(bytes(data_str, "utf-8"), (UDP_ADDRESS, UDP_PORT))
        data_list = data_str.split(',')
        print(data_str)
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

