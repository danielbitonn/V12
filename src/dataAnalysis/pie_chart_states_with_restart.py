import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np

# Read the CSV files
df = pd.read_csv('DB/S6 - Press States 5-06-2023 05_00 - 6-06-2023 05_00.csv')
df2 = pd.read_csv('DB/S6 - Restarts 5-06-2023 05_00 - 6-06-2023 05_00.csv')

# Filter the rows in the second dataframe
df2 = df2[df2['type'].isin(['SwShutdown', 'SwStartupInitiated'])]

# Change the names of the filtered rows
df2['type'] = df2['type'].replace({'SwShutdown': 'Shutdown', 'SwStartupInitiated': 'Power-Up'})

# Merge the dataframes
df = pd.concat([df, df2.rename(columns={'type': 'pressState'})])

# Replace 'Init' with 'Off'
df['pressState'] = df['pressState'].replace({'Init': 'Off'})

# Sort the dataframe by time and reset the index
df = df.sort_values(by='time').reset_index(drop=True)

# Replace 'Print' with 'Pre / Post Print' if 'machineState' is 'PRE_PRINT' or 'POST_PRINT'
df.loc[(df['machineState'].isin(['PRE_PRINT'])) & (df['pressState'] == 'Print'), 'pressState'] = 'Pre Print'
df.loc[(df['machineState'].isin(['POST_PRINT'])) & (df['pressState'] == 'Print'), 'pressState'] = 'Post Print'

# Convert the 'time' column to datetime objects, convert to the desired timezone, and remove timezone information
df['time'] = pd.to_datetime(df['time']).dt.tz_localize(None)

# Identify rows where 'pressState' is 'Shutdown' or 'Power-Up'
shutdown_indices = df[df['pressState'] == 'Shutdown'].index
powerup_indices = df[df['pressState'] == 'Power-Up'].index

# Pair the indices of 'Shutdown' and 'Power-Up' events
indices_to_drop = []

for shutdown_index in shutdown_indices:
    # Find the next 'Power-Up' event after a 'Shutdown'
    powerup_index = powerup_indices[powerup_indices > shutdown_index].min()
    
    if np.isnan(powerup_index):
        continue

    # Append the indices of the logs between 'Shutdown' and 'Power-Up' to the list
    indices_to_drop.extend(range(shutdown_index + 1, int(powerup_index)))

# Drop the logs between 'Shutdown' and 'Power-Up'
df = df.drop(indices_to_drop)


# Reset the DataFrame index
df = df.reset_index(drop=True)

# Store the indices to drop
indices_to_drop = []

# Check if df has at least 2 rows
if len(df) > 1:
    # Use while loop instead of for loop
    i = 0
    while i < len(df) - 1:
        # Check if the current log is a 'Shutdown' and the next log is a 'Power-Up'
        if df.loc[i, 'pressState'] == 'Shutdown' and df.loc[i + 1, 'pressState'] == 'Power-Up':
            # Check if the 'Shutdown' log lasts less than 10 minutes
            if (df.loc[i + 1, 'time'] - df.loc[i, 'time']).total_seconds() < 10 * 60:
                # Change the state of the 'Shutdown' log to 'Restart'
                df.loc[i, 'pressState'] = 'Restart'
                # Add the 'Power-Up' log index to the list to be dropped
                indices_to_drop.append(i + 1)
                i += 2  # Skip the next row
                continue  # Continue to the next iteration
        i += 1  # Increment the index by 1

# Drop the rows with the collected indices
df = df.drop(indices_to_drop)

# Reset the index to account for the dropped rows
df = df.reset_index(drop=True)


# Define state colors
state_colors = {
    'Off': '#BC0E00',
    'Service': '#EBB517',
    'Standby': '#EADA1B',
    'GetReady': 'lightgreen',
    'Ready': 'green',
    'Print': '#591AF5',
    'Pre Print': '#40B1DE',
    'Post Print': '#40B1DE',    
    'Shutdown': 'gray',
    'Power-Up': '#5C2E91',
    'Restart' : '#AB30DE'
}

# First, create a list to store the duration of each press state
data = []

# Calculate the duration of each press state
prev_time = df['time'].iloc[0]
prev_state = df['pressState'].iloc[0]

for index, row in df.iterrows():
    if index == 0:
        continue

    duration = row['time'] - prev_time
    data.append({'pressState': prev_state, 'duration': duration.total_seconds()})

    prev_time = row['time']
    prev_state = row['pressState']

# Convert the list to a DataFrame
df_duration = pd.DataFrame(data)

# Group by 'pressState' and sum the durations
df_duration = df_duration.groupby('pressState').sum().reset_index()

# Convert the durations from seconds to hours for better readability
df_duration['duration'] = df_duration['duration'] / 3600

# Calculate the total duration
total_duration = df_duration['duration'].sum()

# Calculate the proportion of each press state
df_duration['proportion'] = df_duration['duration'] / total_duration

# If 'Power-Up' is less than 1%, include it in 'Restart'
if df_duration[df_duration['pressState'] == 'Power-Up']['proportion'].values[0] < 0.02:
    df_duration.loc[df_duration['pressState'] == 'Power-Up', 'pressState'] = 'Restart'

# Group by 'pressState' again and sum the durations
df_duration = df_duration.groupby('pressState').sum().reset_index()

# Filter out 'Shutdown' durations more than an hour
df_duration = df_duration[~((df_duration['pressState'] == 'Shutdown') & (df_duration['duration'] > 1))]

# Define the desired order
order = ['Shutdown', 'Power-Up', 'Off', 'Restart', 'Service', 'Standby', 'GetReady', 'Ready', 'Pre Print', 'Print', 'Post Print']

# Create a column 'order' to sort by
df_duration['order'] = df_duration['pressState'].apply(lambda x: order.index(x) if x in order else len(order))

# Sort by 'order', then drop the 'order' column
df_duration = df_duration.sort_values('order').drop('order', axis=1)

# Create the pie chart
fig, ax = plt.subplots(figsize=(10, 10))

# Use the color map you defined earlier
colors = df_duration['pressState'].map(state_colors)

# ax.pie(df_duration['duration'], labels=df_duration['pressState'], colors=colors, autopct='%1.1f%%', startangle=90, counterclock=False)

# `edgecolor` determines the color of the lines.
ax.pie(df_duration['duration'], labels=df_duration['pressState'], colors=colors, autopct='%1.1f%%', startangle=90, counterclock=False,
       wedgeprops={'linewidth': 1.0, 'edgecolor': 'white'})

# Ensure that pie is drawn as a circle.
ax.axis('equal')

# Display the plot
# plt.show()

fig.savefig("pie_chart_states_with_restart.png", bbox_inches='tight')

