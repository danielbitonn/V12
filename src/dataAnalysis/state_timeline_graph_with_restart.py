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

# Sort the dataframe by time and reset the index
df = df.sort_values(by='time').reset_index(drop=True)

# Replace 'Print' with 'Pre / Post Print' if 'machineState' is 'PRE_PRINT' or 'POST_PRINT'
df.loc[(df['machineState'].isin(['PRE_PRINT', 'POST_PRINT'])) & (df['pressState'] == 'Print'), 'pressState'] = 'Pre / Post Print'

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
    'Pre / Post Print': '#40B1DE',
    'Shutdown': 'gray',
    'Power-Up': '#5C2E91',
    'Restart' : '#AB30DE'
}

# Create the horizontal bar plot
fig, ax = plt.subplots(figsize=(15, 2))
prev_time = df['time'].iloc[0]
prev_state = df['pressState'].iloc[0]

for index, row in df.iterrows():
    if index == 0:
        continue

    ax.barh(0, row['time'] - prev_time, left=prev_time, height=1, color=state_colors[prev_state])

    prev_time = row['time']
    prev_state = row['pressState']

# Generate a list of hourly ticks between the first and last log
first_log = df['time'].min()
last_log = df['time'].max()
hourly_ticks = pd.date_range(first_log.floor('H'), last_log.ceil('H'), freq='H')

# Filter out the hours before the first log and after the last log
#hourly_ticks = hourly_ticks[(hourly_ticks >= first_log) & (hourly_ticks <= last_log)]
hourly_ticks = hourly_ticks[(hourly_ticks > first_log) & (hourly_ticks < last_log)]
#hourly_ticks = hourly_ticks[(hourly_ticks > first_log.ceil('H')) & (hourly_ticks < last_log.floor('H'))]


# Add first and last log to the list of ticks
ticks = hourly_ticks.insert(0, first_log).append(pd.Index([last_log]))

# Set x-axis ticks, format, and limits
ax.set_xticks(ticks)
ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
ax.set_xlim(first_log, last_log)
plt.xticks(rotation=45)

# Add a grid to the plot
ax.xaxis.grid(True, linestyle='--', alpha=0.5)



# Add a grid to the plot
ax.xaxis.grid(True, linestyle='--', alpha=0.5)

# Remove y-axis
ax.yaxis.set_visible(False)

# Set labels and legend
#plt.xlabel('Time')
plt.title('Press States Timeline')
legend_handles = [plt.Rectangle((0, 0), 1, 1, color=state_colors[state]) for state in state_colors]
legend = plt.legend(legend_handles, state_colors.keys(), title='Press States', loc='center left', bbox_to_anchor=(1, 0.5))
legend.set_zorder(0)  # Set the zorder to move the legend to the background

# Adjust the top margin
plt.subplots_adjust(top=0.9)  # adjust value as needed

# Display the plot
plt.tight_layout()
# plt.show()

fig.savefig("state_timeline_graph_with_restart.png", bbox_inches='tight')

