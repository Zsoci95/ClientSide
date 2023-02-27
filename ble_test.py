#!/usr/bin/env python3

import sqlite3
import asyncio
from datetime import datetime
from bleak import BleakClient, BleakError

# Define database name and create connection
db_name = "imu_data.db"
conn = sqlite3.connect(db_name)
c = conn.cursor()

# Open existing table to store IMU data
c.execute('''CREATE TABLE IF NOT EXISTS imu_data (timestamp INTEGER, quaternion_w REAL, quaternion_x REAL, quaternion_y REAL, quaternion_z REAL, acc_x REAL, acc_y REAL, acc_z REAL)''')

# Define device address and UUIDs
device_address = "78:21:84:8A:14:F2"  # replace with actual device address
imu_service_uuid = "bd0f56c6-a403-4d3a-86ba-6fed11ce8473"  # replace with actual IMU service UUID
imu_data_uuid = "1fe90638-437c-490c-ad92-bda3b9423bab"  # replace with actual IMU data UUID

# Define callback function for receiving notifications
async def handle_notification(sender, data, queue):
    timestamp = int(datetime.now().timestamp())
    data_str = data.decode('utf-8')
    data_list = data_str.split(',')
    quaternion_w = float(data_list[0])
    quaternion_x = float(data_list[1])
    quaternion_y = float(data_list[2])
    quaternion_z = float(data_list[3])
    acc_x = float(data_list[4])
    acc_y = float(data_list[5])
    acc_z = float(data_list[6])
    if queue.full():
        queue.get_nowait()  # discard oldest data point
    queue.put((timestamp, quaternion_w, quaternion_x, quaternion_y, quaternion_z, acc_x, acc_y, acc_z))
    try:
        reader, writer = await asyncio.open_connection('127.0.0.1', 12345) # open TCP connection to local host, replace IP and port with your desired values
        message = f"{quaternion_w},{quaternion_x},{quaternion_y},{quaternion_z}\n"  # add new line at the end for message delimiter
        writer.write(message.encode())
        await writer.drain()
        writer.close()
        await writer.wait_closed()
    except:
        pass

async def process_data(queue):
    while True:
        data = await queue.get()
        timestamp, quaternion_w, quaternion_x, quaternion_y, quaternion_z, acc_x, acc_y, acc_z = data
        c.execute("INSERT INTO imu_data (timestamp, quaternion_w, quaternion_x, quaternion_y, quaternion_z, acc_x, acc_y, acc_z) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                  (timestamp, quaternion_w, quaternion_x, quaternion_y, quaternion_z, acc_x, acc_y, acc_z))
        conn.commit()

async def run():
    queue = asyncio.Queue(maxsize=10000)
    task = asyncio.create_task(process_data(queue))
    try:
        async with BleakClient("F5A6EF50-BF44-B5DB-3BD0-0432180F23FF") as client:
            while True:
                data = await client.read_gatt_char(imu_data_uuid)
                handle_notification(None, data, queue)
                
    except BleakError as e:
        print(f"Error: {e}")

# Run the coroutine in the event loop
loop = asyncio.get_event_loop()
loop.run_until_complete(run())
