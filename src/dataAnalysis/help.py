
# import pandas as pd
#
#
# dataFile = "download_file.csv"
# df = pd.read_csv(dataFile)
#
# print(df.columns)
#
# columns = ['Site Name', 'Serial Number', 'State Datetime', 'Press State',
#        'Site Name.1', 'Site Region', 'delta time [Min.]', 'State delta time']
# color_list = [
#     "blue",
#     "green",
#     "red",
#     "cyan",
#     "magenta",
#     "yellow",
#     "black",
#     "purple",
#     "lime",
#     "navy",
#     "teal",
#     "maroon",
#     "aqua",
#     "fuchsia",
#     "olive",
#     "gray",
#     "silver",
#     "darkred",
#     "orange",
#     "pink"
# ]


# Color Mapping
# state_mapping = {
#     'POWER_DISABLE': 'gray',
#     'OFF': 'black',
#     'GO_TO_SERVICE': 'orange',
#     'SERVICE': 'yellow',
#     'MECH_INIT': 'green',
#     'GO_TO_OFF': 'blue',
#     'STANDBY': 'purple',
#     'GET_READY': 'cyan',
#     'DYNAMIC_READY': 'magenta',
#     'PRE_PRINT': 'red',
#     'POST_PRINT': 'brown',
#     'READY': 'pink',
#     'PRINT': 'lightblue',
#     'GO_TO_STANDBY': 'darkgreen',
#     'Off': 'black',
#     'Service': 'yellow',
#     'Standby': 'purple',
#     'GetReady': 'cyan',
#     'Ready': 'pink',
#     'Print': 'lightblue'
# }


# unique_name='fdfs'
# extension = '454132'
# res = unique_name+extension
#
# print(res)

import os
import fnmatch
import pandas as pd
# from src.util.filesHandle import *
# path = find_rel_path(file_name="test_to_gcsteamcont.csv")


def verify_convert_datetime(data_frame, column):
    formats = ['%Y-%m-%d %H:%M:%S', '%m/%d/%Y %H:%M']
    for fmt in formats:
        try:
            data_frame[column] = pd.to_datetime(data_frame[column], format=fmt)
            print(f"'{column}' successfully converted to datetime format.")
            return data_frame
        except ValueError:
            continue
    print(f"Could not convert '{column}' to datetime format. Please check the timestamp format.")
    return data_frame


df = pd.read_csv('test_to_gcsteamcont.csv')

print(type(df['PlcTime'][1]))
df['PlcTime'] = pd.to_datetime(df['PlcTime'])
print(type(df['PlcTime'][1]))
df = verify_convert_datetime(df, 'PlcTime')
df['time'] = pd.to_datetime(df['PlcTime'])
df.sort_values('time').reset_index(drop=True)

# Convert the 'time' column to datetime objects, convert to the desired timezone, and remove timezone information
df['time'] = pd.to_datetime(df['time']).dt.tz_localize(None)

print(type(df['time'][1]))
