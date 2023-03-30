from datetime import datetime
import matplotlib.pyplot as plt
import pandas as pd

receive_flag = False # False if listening to the port which python is sending to, True if listening to the port which the C# program is sending to

times = []

if receive_flag: 
    pass 
else:
    df = pd.read_csv('/Users/zsoltkardos/Library/CloudStorage/OneDrive-UniversityofLeeds/University/8th semester/MECH5080 Team Project/ClientSide/output.csv')
    df['timestamp'] = pd.to_datetime(df['timestamp'], format='%Y-%m-%d %H:%M:%S.%f')
    df.set_index('timestamp', inplace=True)
    freq_df = df.resample('1S').count()
    fig, ax = plt.subplots()
    ax.plot(freq_df.index, freq_df)
    ax.set_xlabel('Time')
    ax.set_ylabel('Frequency')
    ax.set_title('IMU Reading Frequency over Time')
    plt.show()