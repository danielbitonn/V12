import tkinter as tk
from tkinter import ttk
from datetime import datetime, timedelta
import pandas as pd
import json
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from tkinter import messagebox
import time

# Read the CSV files
df = pd.read_csv('data/pull_data/S6 - Press States 22-05-2023 05_00 - 22-05-2023 23_59.csv')
df2 = pd.read_csv('data/pull_data/S6 - Restarts 22-05-2023 05_00 - 22-05-2023 23_59.csv')
df_failures = pd.read_csv('data/pull_data/S6 - Failures 22-05-2023 05_00 - 22-05-2023 23_59.csv')

df_failures['time'] = pd.to_datetime(df_failures['time']).dt.tz_localize(None)
df_failures = df_failures[df_failures['severity'] == 'Failure']

# Filter the rows in the second dataframe
df2 = df2[df2['type'].isin(['SwShutdown', 'SwStartupInitiated'])]

# Change the names of the filtered rows
df2['type'] = df2['type'].replace({'SwShutdown': 'Shutdown', 'SwStartupInitiated': 'Power-Up'})

# Merge the dataframes
df = pd.concat([df, df2.rename(columns={'type': 'pressState'})])

# Sort the dataframe by time and reset the index
df = df.sort_values(by='time').reset_index(drop=True)

# Replace 'Print' with 'Pre / Post Print' if 'machineState' is 'PRE_PRINT' or 'POST_PRINT'
df.loc[(df['machineState'].isin(['PRE_PRINT', 'POST_PRINT'])) & (
        df['pressState'] == 'Print'), 'pressState'] = 'Pre / Post Print'

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

##########################################################################################################
##########################################################################################################
##########################################################################################################
##########################################################################################################
##########################################################################################################


# Initialize variables to store the start time and total duration of the combined states
combined_start_time = None
combined_duration = timedelta()
combined_states = []

# Topics and times
# topics = ["Operator duties", "Troubleshooting", "Mechanical issue", "Software issue"]
topics = ["--Because of press--", "Part replacement", "Scheduled Maintenance", "Unscheduled Maintenance", "SW issue",
          "HW issue",
          "--Because of site--", "Operator duties", "Unavailable job", "Unavailable substrate", "Site maintenance"]

times = [f'{str(i).zfill(2)}:{str(j).zfill(2)}' for i in range(24) for j in range(0, 60, 15)]

# Load data
try:
    with open("data/main_events_archive.json", "r") as file:
        data = json.load(file)
except FileNotFoundError:
    data = {"Main events": []}

# Get today's date
today = datetime.now().strftime("%Y-%m-%d")

# Look for today's events in the data
events_today = []
for day_events in data["Main events"]:
    if day_events["date"] == today:
        events_today = day_events["events"]
        break

# Iterate through the DataFrame rows
for i in range(len(df) - 1):  # iterate till second last row
    # Calculate the time difference between this row and the next row
    time_diff = df['time'].iloc[i + 1] - df['time'].iloc[i]

    # Check if the 'pressState' was 'Ready' or 'Service' for more than 15 minutes
    if df['pressState'].iloc[i] in ['Ready'] and time_diff > timedelta(minutes=15):
        events_today.append({
            'topic': df['pressState'].iloc[i],
            'start_time': df['time'].iloc[i].strftime('%H:%M'),
            'end_time': df['time'].iloc[i + 1].strftime('%H:%M'),
            'description': f'The machine was in {df["pressState"].iloc[i]} state for more than 15 minutes.'
        })


    # Check if the 'pressState' is 'Off'/'Service'/'Standby'/'Shutdown'/'Restart'
    elif df['pressState'].iloc[i] in ['Off', 'Service', 'Standby', 'Shutdown', 'Restart']:
        # Start accumulating the duration if it's not already started
        if combined_start_time is None:
            combined_start_time = df['time'].iloc[i]

        combined_duration += time_diff
        combined_states.append(df['pressState'].iloc[i])

    # Special case for 'GetReady'
    elif df['pressState'].iloc[i] == 'GetReady':
        # Only include 'GetReady' in the combination if it's not followed by 'Ready'
        if df['pressState'].iloc[i + 1] != 'Ready':
            if combined_start_time is None:
                combined_start_time = df['time'].iloc[i]

            combined_duration += time_diff
            combined_states.append(df['pressState'].iloc[i])
        else:
            if combined_duration > timedelta(minutes=15):
                events_today.append({
                    'topic': 'Combined',
                    'start_time': combined_start_time.strftime('%H:%M'),
                    'end_time': df['time'].iloc[i].strftime('%H:%M'),
                    'description': f'The machine was in a combination of {", ".join(set(combined_states))} states for more than 15 minutes.'
                })

            combined_start_time = None
            combined_duration = timedelta()
            combined_states = []

    else:
        # Reset the start time, total duration, and combined states when the machine leaves the combined states
        if combined_duration > timedelta(minutes=15):
            events_today.append({
                'topic': 'Combined',
                'start_time': combined_start_time.strftime('%H:%M'),
                'end_time': df['time'].iloc[i].strftime('%H:%M'),
                'description': f'The machine was in a combination of {", ".join(set(combined_states))} states for more than 15 minutes.'
            })

        combined_start_time = None
        combined_duration = timedelta()
        combined_states = []

# Check the accumulated states one last time after the loop
if combined_duration > timedelta(minutes=15):
    events_today.append({
        'topic': 'Combined',
        'start_time': combined_start_time.strftime('%H:%M'),
        'end_time': df['time'].iloc[-1].strftime('%H:%M'),
        'description': f'The machine was in a combination of {", ".join(set(combined_states))} states for more than 15 minutes.'
    })

##########################################################################################################
##########################################################################################################
##########################################################################################################
##########################################################################################################
##########################################################################################################

# Define row_counter
row_counter = len(events_today)

# If no events for today were found, create a new entry
if not events_today:
    data["Main events"].append({"date": today, "events": events_today})

event_rows = []


class EventRow:
    def __init__(self, master, row, event=None):
        if event is None:
            event = {'topic': '', 'start_time': '08:00', 'end_time': '08:00', 'description': ''}

        topic_combo = ttk.Combobox(master, values=topics, state='readonly')
        topic_combo.set(event['topic'])  # Set the value from the event data
        topic_combo.grid(row=row, column=0, padx=5)

        start_time_combo = ttk.Combobox(master, values=times, state='readonly', width=5)
        start_time_combo.set(event['start_time'])  # Set the value from the event data
        start_time_combo.grid(row=row, column=1)

        end_time_combo = ttk.Combobox(master, values=times, state='readonly', width=5)
        end_time_combo.set(event['end_time'])  # Set the value from the event data
        end_time_combo.grid(row=row, column=2)

        description_entry = tk.Entry(master)
        description_entry.insert(0, event['description'])  # Set the value from the event data
        description_entry.grid(row=row, column=3, sticky='we', padx=5)

        delete_button = tk.Button(master, text="Delete", command=self.delete)
        delete_button.grid(row=row, column=4, padx=5)

        def update_event(*args):
            # Store previous values
            previous_start_time = event['start_time']
            previous_end_time = event['end_time']

            event['topic'] = topic_combo.get()

            # Verify that the time entered is within the DataFrame's timestamps
            start_time_str = start_time_combo.get()
            end_time_str = end_time_combo.get()

            start_time = datetime.strptime(start_time_str, '%H:%M').time()  # Extract the time part
            end_time = datetime.strptime(end_time_str, '%H:%M').time()  # Extract the time part

            df_min_time = df['time'].min().time()
            df_max_time = df['time'].max().time()

            if not (df_min_time <= start_time <= df_max_time and df_min_time <= end_time <= df_max_time):
                messagebox.showerror("Invalid Time", "Error: Time entered is beyond the DataFrame time range.")

                # Restore previous values
                start_time_combo.set(previous_start_time)
                end_time_combo.set(previous_end_time)
                return

            event['start_time'] = start_time_str
            event['end_time'] = end_time_str
            event['description'] = description_entry.get()

            # Update the event and save it to JSON
            save_data()

        # Call update_event when the values change
        topic_combo.bind('<<ComboboxSelected>>', update_event)
        start_time_combo.bind('<<ComboboxSelected>>', update_event)
        end_time_combo.bind('<<ComboboxSelected>>', update_event)
        description_entry.bind('<KeyRelease>', update_event)

        self.row = row
        self.widgets = [topic_combo, start_time_combo, end_time_combo, description_entry, delete_button]
        self.event = event

    def delete(self):
        # Remove widgets
        for widget in self.widgets:
            widget.grid_remove()

        # Remove this event from the list
        event_rows.remove(self)
        events_today.remove(self.event)


def event_exists(event):
    """Check if an event with the same 'start_time' and 'end_time' already exists in events_today"""
    for existing_event in events_today:
        # Ignore events with the same start and end times
        if (existing_event['start_time'] == existing_event['end_time']):
            continue

        if (existing_event['start_time'] == event['start_time'] and
                existing_event['end_time'] == event['end_time']):
            return True

    return False


def save_data():
    # Rebuild the events_today list from the event_row objects
    events_today_rebuilt = []

    for event_row in event_rows:
        event = event_row.event
        # Only add the event if a topic is selected and it does not already exist
        if event['topic'] != '' and not event_exists(event):
            events_today_rebuilt.append(event)

    # Check if an entry for today already exists in data
    existing_entry = [day_events for day_events in data["Main events"] if day_events["date"] == today]

    # Add the new entry for today to data only if there are any events and no existing entry
    if events_today_rebuilt and not existing_entry:
        data["Main events"].append({"date": today, "events": events_today_rebuilt})

    # Write data to file
    with open("data/main_events_archive.json", "w") as file:
        json.dump(data, file, indent=4)


def add_event():
    # Create a new event
    event = {'topic': '', 'start_time': '08:00', 'end_time': '08:00', 'description': ''}

    # Prevent adding if the event already exists
    if event_exists(event):
        print('Event with same start and end time already exists')
        return

    # Add to events_today
    events_today.append(event)

    # Update the row_counter
    global row_counter
    row_counter += 1

    # Create a new row for the event
    event_row = EventRow(root, row_counter, event)
    event_rows.append(event_row)

    # Update the "Add Event" button position
    add_button_frame.grid(row=row_counter + 1, columnspan=5)


def close_window():
    save_data()
    time.sleep(1)  # Delay for 1 second
    root.destroy()


# Create the Tkinter application
root = tk.Tk()
root.title("Daily Report")
root.iconbitmap('src/_ref_/media/sandbox_timeline_report.ico')
root.geometry("1000x600")

# Save data when the application is about to close
root.protocol("WM_DELETE_WINDOW", close_window)

# Configure the column containing the description_entry widgets to be stretchable
root.grid_columnconfigure(3, weight=1)

# Create labels
labels = ["Topic", "Start time", "End time", "Description", "Delete"]
for i, label in enumerate(labels):
    tk.Label(root, text=label).grid(row=0, column=i, padx=5)

# Create the frame for the "Add Event" button
add_button_frame = tk.Frame(root)

# Create a button to add new events
add_button = tk.Button(add_button_frame, text="Add Event", command=add_event)
add_button.pack()

# Create a row for each event
for i, event in enumerate(events_today):
    event_row = EventRow(root, i + 1, event)
    event_rows.append(event_row)

# If there were no events loaded from file, add an empty event
if len(event_rows) == 0:
    add_event()
else:
    add_button_frame.grid(row=row_counter + 1, column=0, columnspan=5)

root.mainloop()

##########################################################################################################################################
############### Graphs
##########################################################################################################################################

# List to hold text objects
texts = []

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
    'Restart': '#AB30DE'
}

# Create the horizontal bar plot
fig, (ax2, ax1) = plt.subplots(2, sharex=True, gridspec_kw={'height_ratios': [1, 1], 'hspace': 0})

# For ax1, create a neutral color plot
prev_time = df['time'].iloc[0]
for index, row in df.iterrows():
    if index == 0:
        continue
    ax1.barh(0, row['time'] - prev_time, left=prev_time, height=0.5, color='lightgrey')
    prev_time = row['time']

# For ax2, create a colored plot by state
prev_time = df['time'].iloc[0]
prev_state = df['pressState'].iloc[0]
for index, row in df.iterrows():
    if index == 0:
        continue
    ax2.barh(0, row['time'] - prev_time, left=prev_time, height=1, color=state_colors[prev_state])
    prev_time = row['time']
    prev_state = row['pressState']

# Generate a list of hourly ticks between the first and last log
first_log = df['time'].min()
last_log = df['time'].max()
hourly_ticks = pd.date_range(first_log.floor('H'), last_log.ceil('H'), freq='H')

# Filter out the hours before the first log and after the last log
hourly_ticks = hourly_ticks[(hourly_ticks > first_log) & (hourly_ticks < last_log)]

# Add first and last log to the list of ticks
ticks = hourly_ticks.insert(0, first_log).append(pd.Index([last_log]))

axes = [ax1, ax2]
for ax in axes:
    # Set x-axis ticks, format, and limits
    ax.set_xticks(ticks)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    ax.set_xlim(first_log, last_log)
    plt.xticks(rotation=45)

    # Add a grid to the plot
    ax.xaxis.grid(True, linestyle='--', alpha=0.5)

    # Remove y-axis
    ax.yaxis.set_visible(False)

# Add arrows to the ax1
y_positions = [0.007, 0.001]  # Two different y-positions for the text

# List all unique topics
unique_topics = list(set(event['topic'] for event in events_today))

# Prepare a color palette for topics
topic_colors = dict(zip(unique_topics, plt.cm.get_cmap('tab10', len(unique_topics)).colors))

for i, event in enumerate(events_today):
    # Parse the start and end times back into datetime objects
    start_time = datetime.strptime(event['start_time'], '%H:%M').replace(year=first_log.year, month=first_log.month,
                                                                         day=first_log.day)
    end_time = datetime.strptime(event['end_time'], '%H:%M').replace(year=first_log.year, month=first_log.month,
                                                                     day=first_log.day)

    # Choose the y-position based on whether the index is even or odd
    y_position = y_positions[i % 2]

    # Add a color bar from the start time to the end time
    ax1.barh(y_position, end_time - start_time, left=start_time, color=topic_colors[event['topic']])

    # Add a label above the color bar
    # text = ax1.text(start_time + (end_time - start_time)/2, y_position + 0.007, event['topic'], ha='center')
    # texts.append(text)

# Set the y-axis limits for ax1
ax1.set_ylim(0, max(y_positions) + 0.01)  # Adjust this to fit your texts

# # Set labels and legend only for ax2
# ax1.set_title('Press States Timeline')
# legend_handles = [plt.Rectangle((0, 0), 1, 1, color=state_colors[state]) for state in state_colors]
# legend = ax2.legend(legend_handles, state_colors.keys(), title='Press States', loc='center left', bbox_to_anchor=(1, 0.5))
# legend.set_zorder(0)  # Set the zorder to move the legend to the background

from matplotlib.lines import Line2D

# Your previous legend creation code
legend_handles = [plt.Rectangle((0, 0), 1, 1, color=state_colors[state]) for state in state_colors]

# Create a custom legend handle for the failure symbol
failure_handle = Line2D([0], [0], marker='X', color='None', markerfacecolor='red', markeredgecolor='red', markersize=8)

# Add the failure handle to the legend handles
legend_handles.append(failure_handle)

# Add the corresponding label to the legend labels
legend_labels = list(state_colors.keys()) + ['Failure']

# Create the legend with the custom handles and labels
legend = ax2.legend(legend_handles, legend_labels, title='Press States and Events', loc='center left',
                    bbox_to_anchor=(1, 0.5))
legend.set_zorder(0)  # Set the zorder to move the legend to the background

# Add legend for ax1
topic_handles = [plt.Rectangle((0, 0), 1, 1, color=topic_colors[topic]) for topic in topic_colors]
legend1 = ax1.legend(topic_handles, topic_colors.keys(), title='Topics', loc='center left', bbox_to_anchor=(1, 0.5))
legend1.set_zorder(0)  # Set the zorder to move the legend to the background

# Remove the bottom spine of ax1
ax2.spines['bottom'].set_visible(False)

# Remove the bottom spine of ax1
ax1.spines['top'].set_visible(False)

for index, row in df_failures.iterrows():
    ax1.plot(row['time'], 0.007, marker='X', color='red', markersize=8)

# Adjust the plot layout
plt.tight_layout()

# Display the plot
plt.show()

####################################################################################################################
