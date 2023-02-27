import asyncio
from bleak import BleakClient, BleakError 

# UUIDs for the service and characteristics that contain the data
DEVICE_ADDRESS = "F5A6EF50-BF44-B5DB-3BD0-0432180F23FF"
SERVICE_UUID = "bd0f56c6-a403-4d3a-86ba-6fed11ce8473"
CHARACTERISTIC_UUID = "1fe90638-437c-490c-ad92-bda3b9423bab"

async def run():
    try:
        async with BleakClient(DEVICE_ADDRESS) as client:
            while True:
                data = await client.read_gatt_char(CHARACTERISTIC_UUID)    
                print(data)    
    except BleakError as e:
        print(f"Error: {e}")

# Run the coroutine in the event loop
loop = asyncio.get_event_loop()
loop.run_until_complete(run())