How to intsall clientside
=========================
1. Install Python from https://www.python.org/downloads/
2. Install python packages: asyncio, bleak, pyodbc using pip from command line (pip install bleak). If pip not found, try pip3 instead of pip
3. Clone ClientSide repository
4. Run middleware.py 
5. If device not found error: change device_used to 1 or 2
6. If there's still an error: run ble_scan.py to find the correct device address (should be the long code to the left of device named M5-Stack-server)
7. To test if you're receiving data: put print(data_str) under sock.sendto(bytes(data_str, "utf-8"), (UDP_ADDRESS, UDP_PORT)) in the data_handler function
8. To check if SQL is working: set sql_used to true and change all the variable names to match the database