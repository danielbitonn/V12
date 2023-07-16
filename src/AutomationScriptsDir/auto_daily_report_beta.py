import tkinter as tk
from tkinter import ttk
from tkinter import Menu, Menubutton, StringVar, N, E, W
import tkinter.font as font
from datetime import datetime, timedelta
import pandas as pd
import json
import numpy as np
from tkinter import messagebox
import time
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.lines import Line2D
import os
import glob


# Function to check if an event with the same start_time and end_time exists in events_today
def event_exists(new_event, events):
    for event in events:
        if event['start_time'] == new_event['start_time'] and event['end_time'] == new_event['end_time']:
            return True
    return False


# Define a function to extract the timestamp from the filename
def extract_timestamp(filename):
    # Extract the timestamp string from the filename
    timestamp_str = filename.split('To_')[1].split('.csv')[0]
    # Convert the timestamp string to a datetime object
    timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d_%H-%M-%S')
    return timestamp


def initial_daily_beta():
    event_rows = []
    # Set the path and press serial number
    today_path = datetime.now().strftime('%Y-%m-%d')
    press_sn = 'b70001002'

    # Define the directory path
    dir_path = f'DB/data/pull_data/{press_sn}/{today_path}'

    # List all CSV files
    all_csv_files = glob.glob(os.path.join(dir_path, '*.csv'))

    # Sort the list of files based on the timestamp in the filename
    all_csv_files.sort(key=extract_timestamp, reverse=True)

    # Now the newest file is the first in the list
    newest_file = all_csv_files[0]

    # Check the name of the newest file to decide which dataframe to load the data into
    if 'press-state-history' in newest_file:
        df = pd.read_csv(newest_file)
        df.columns = df.columns.str.lower()


    elif 'restart-history' in newest_file:
        df2 = pd.read_csv(newest_file)
        df2.columns = df2.columns.str.lower()

    elif 'event-history' in newest_file:
        df_failures = pd.read_csv(newest_file)
        df_failures.columns = df_failures.columns.str.lower()

    ####################################################################################################################
    ####################################################################################################################
    ####################################################################################################################
    press_state = 'pressstate'
    sub_system = 'subsystem'
    machine_state = 'machinestate'
    ####################################################################################################################
    ####################################################################################################################
    ####################################################################################################################

    df = pd.read_csv('DB/S6 - Press States 3-07-2023 06_00 - 3-07-2023 23_00.csv')
    df.columns = df.columns.str.lower()
    df2 = pd.read_csv('DB/S6 - Restarts 3-07-2023 06_00 - 3-07-2023 23_00.csv')
    df2.columns = df2.columns.str.lower()
    df_failures = pd.read_csv('DB/S6 - Failures 3-07-2023 06_00 - 3-07-2023 23_00.csv')
    df_failures.columns = df_failures.columns.str.lower()

    df_failures['time'] = pd.to_datetime(df_failures['time']).dt.tz_localize(None)
    df_failures = df_failures[df_failures['severity'] == 'Failure']

    df[press_state] = df[press_state].replace({'Init': 'Off'})

    df_failures_UW = df_failures[df_failures['name'] == 'UW_ROLL_EMPTY']
    df_failures_RW = df_failures[df_failures['name'] == 'RW_ROLL_FULL']
    df_failures = df_failures[~df_failures['name'].isin(['UW_ROLL_EMPTY', 'RW_ROLL_FULL'])]

    # Filter the rows in the second dataframe
    df2 = df2[df2['type'].isin(['SwShutdown', 'SwStartupInitiated'])]

    # Change the names of the filtered rows
    df2['type'] = df2['type'].replace({'SwShutdown': 'Shutdown', 'SwStartupInitiated': 'Power-Up'})

    # Merge the dataframes
    df = pd.concat([df, df2.rename(columns={'type': press_state})])

    # Sort the dataframe by time and reset the index
    df = df.sort_values(by='time').reset_index(drop=True)

    # Replace 'Print' with 'Pre / Post Print' if 'machineState' is 'PRE_PRINT' or 'POST_PRINT'
    df.loc[(df[machine_state].isin(['PRE_PRINT', 'POST_PRINT'])) & (
            df[press_state] == 'Print'), press_state] = 'Pre / Post Print'

    # Convert the 'time' column to datetime objects, convert to the desired timezone, and remove timezone information
    df['time'] = pd.to_datetime(df['time']).dt.tz_localize(None)

    # Identify rows where 'pressState' is 'Shutdown' or 'Power-Up'
    shutdown_indices = df[df[press_state] == 'Shutdown'].index
    powerup_indices = df[df[press_state] == 'Power-Up'].index

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
            if df.loc[i, press_state] == 'Shutdown' and df.loc[i + 1, press_state] == 'Power-Up':
                # Check if the 'Shutdown' log lasts less than 10 minutes
                if (df.loc[i + 1, 'time'] - df.loc[i, 'time']).total_seconds() < 10 * 60:
                    # Change the state of the 'Shutdown' log to 'Restart'
                    df.loc[i, press_state] = 'Restart'
                    # Add the 'Power-Up' log index to the list to be dropped
                    indices_to_drop.append(i + 1)
                    i += 2  # Skip the next row
                    continue  # Continue to the next iteration
            i += 1  # Increment the index by 1

    # Drop the rows with the collected indices
    df = df.drop(indices_to_drop)

    # Reset the index to account for the dropped rows
    df = df.reset_index(drop=True)

    ####################################################################################################################
    ####################################################################################################################
    ####################################################################################################################

    # Initialize variables to store the start time and total duration of the combined states
    combined_start_time = None
    combined_duration = timedelta()
    combined_states = []

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

    new_events = []

    # Iterate through the DataFrame rows
    for i in range(len(df) - 1):  # iterate till second last row
        # Calculate the time difference between this row and the next row
        time_diff = df['time'].iloc[i + 1] - df['time'].iloc[i]

        # Check if the 'pressState' was 'Ready' or 'Service' for more than 15 minutes
        if df[press_state].iloc[i] in ['Ready'] and time_diff > timedelta(minutes=15):
            new_events.append({
                'topic': df[press_state].iloc[i],
                'start_time': df['time'].iloc[i].strftime('%H:%M'),
                'end_time': df['time'].iloc[i + 1].strftime('%H:%M'),
                'description': f'The machine was in {df[press_state].iloc[i]} state for more than 15 minutes.'
            })

        # Check if the 'pressState' is 'Off'/'Service'/'Standby'/'Shutdown'/'Restart'
        elif df[press_state].iloc[i] in ['Off', 'Service', 'Standby', 'Shutdown', 'Restart']:
            # Start accumulating the duration if it's not already started
            if combined_start_time is None:
                combined_start_time = df['time'].iloc[i]

            combined_duration += time_diff
            combined_states.append(df[press_state].iloc[i])

        # Special case for 'GetReady'
        elif df[press_state].iloc[i] == 'GetReady':
            # Only include 'GetReady' in the combination if it's not followed by 'Ready'
            if df[press_state].iloc[i + 1] != 'Ready':
                if combined_start_time is None:
                    combined_start_time = df['time'].iloc[i]

                combined_duration += time_diff
                combined_states.append(df[press_state].iloc[i])
            else:
                if combined_duration > timedelta(minutes=15):
                    new_events.append({
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
                new_events.append({
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
        new_events.append({
            'topic': 'Combined',
            'start_time': combined_start_time.strftime('%H:%M'),
            'end_time': df['time'].iloc[-1].strftime('%H:%M'),
            'description': f'The machine was in a combination of {", ".join(set(combined_states))} states for more than 15 minutes.'
        })

    # Now we iterate through the new_events list and only add those events to events_today that do not already exist there
    for event in new_events:
        if not event_exists(event, events_today):
            events_today.append(event)
    # Sort the events_today by start_time
    events_today = sorted(events_today, key=lambda x: datetime.strptime(x['start_time'], '%H:%M'))

    # Define row_counter
    row_counter = len(events_today)

    # If no events for today were found, create a new entry
    if not events_today:
        data["Main events"].append({"date": today, "events": events_today})

    return events_today


class EventRow:
    def __init__(self, master, row, events, event_index, event_rows, event=None):
        if event is None:
            event = {'topic_var': '', 'part': '', 'start_time': '08:00', 'mid_time': '', 'end_time': '08:00',
                     'description': ''}

        # Save a reference to events_today and the index of the event in it
        self.events = events
        self.event_index = event_index

        # Create StringVar to hold the selected topic
        self.topic_var = StringVar()
        self.topic_var.set(event['topic'])

        # create a menubutton
        topic_button = Menubutton(master, text=self.topic_var.get(), relief="raised", bd=2, width=20, anchor=W)
        topic_button.grid(row=row, column=0, padx=5)

        # create a menu
        topics_menu = Menu(topic_button, tearoff=0)

        # add your menu items
        self.add_menu_items(topics_menu, ["--Troubleshooting--", "SW issue", "PQ issue", "PQ issue + fix / clean",
                                          "PQ issue + Part replace", "PQ issue + Consumable replace", "HW issue",
                                          "HW issue + fix / clean", "HW issue + Part replace",
                                          "HW issue + Consumable replace", "other",
                                          "--Active actions--", "Part replacement", "Scheduled Maintenance",
                                          "Unscheduled Maintenance", "Web break", "other",
                                          "--Site's reasons--", "Operator duties", "Pending job",
                                          "Pending substrate",
                                          "Site maintenance", "other"])

        topic_button["menu"] = topics_menu

        # Whenever topic_var is updated, the button's text is updated
        self.topic_var.trace('w', lambda *args: topic_button.config(text=self.topic_var.get()))

        # Create the part/consumable button and initially disable it
        self.part_consumable_button = Menubutton(master, text="Select", state='disabled', relief="raised", bd=2,
                                                 width=20, anchor=W)
        self.part_consumable_button.grid(row=row, column=1, padx=5)  # Adjust the column to fit in your layout

        # Create a menu for the button
        self.part_consumable_menu = Menu(self.part_consumable_button, tearoff=0)
        self.part_consumable_button["menu"] = self.part_consumable_menu

        # Instance variable
        self.start_time_combo = ttk.Combobox(master, values=times, state='readonly', width=5)
        self.start_time_combo.set(event['start_time'])  # Set the value from the event data
        self.start_time_combo.grid(row=row, column=2)

        # Instance variable
        self.mid_time_combo = ttk.Combobox(master, values=[], state='disabled', width=5)
        # Check if 'mid_time' key exists and its value is not None
        if 'mid_time' in event and event['mid_time'] is not None:
            self.mid_time_combo.configure(state='readonly')  # Enable the combobox
            self.mid_time_combo.set(event['mid_time'])  # Set the value from the event data
        self.mid_time_combo.grid(row=row, column=3)

        # Instance variable
        self.end_time_combo = ttk.Combobox(master, values=times, state='readonly', width=5)
        self.end_time_combo.set(event['end_time'])  # Set the value from the event data
        self.end_time_combo.grid(row=row, column=4)

        # Instance variable
        self.description_entry = tk.Entry(master)
        self.description_entry.insert(0, event['description'])  # Set the value from the event data
        self.description_entry.grid(row=row, column=5, sticky='we', padx=5)
        # Boolean attribute that checks whether the field has been focused before
        self._description_focused = False
        # Add a focus event to the description entry field
        self.description_entry.bind("<FocusIn>", self.on_description_focus)
        # Create dictionary to map topics to their corresponding descriptions
        self.topic_descriptions = {
            "SW issue": "Description for SW issue",
            "PQ issue": "Description for PQ issue",
            "PQ issue + fix / clean": "Description for PQ issue requiring fix or cleaning",
            "PQ issue + Part replace": "Description for PQ issue requiring part replacement",
            "PQ issue + Consumable replace": "PQ issue requiring consumable replacement",
            "HW issue": "Description for HW issue",
            "HW issue + fix / clean": "Description for HW issue requiring fix or cleaning",
            "HW issue + Part replace": "Description for HW issue requiring part replacement",
            "HW issue + Consumable replace": "HW issue requiring consumable replacement",
            "other": "Description for other issues",
            "Part replacement": "Description for Part replacement",
            "Scheduled Maintenance": "Description for Scheduled Maintenance",
            "Unscheduled Maintenance": "Description for Unscheduled Maintenance",
            "Web break": "Description for Unscheduled Maintenance",
            "other": "Description for other active actions",
            "Operator duties": "Description for Operator duties",
            "Pending job": "Description for Pending job",
            "Pending substrate": "Description for Pending substrate",
            "Site maintenance": "Description for Site maintenance",
            "other": "Description for other site reasons"
        }

        delete_button = tk.Button(master, text="Delete", command=self.delete)
        delete_button.grid(row=row, column=6, padx=5)

        # Define self.event here before calling update_event
        self.event = event

        # First, define the callback function:
        def update_mid_time_state(*args):
            if '+' in self.topic_var.get():
                self.mid_time_combo.config(state='readonly')
            else:
                self.mid_time_combo.config(state='disabled')
                self.mid_time_combo.set('')  # Reset the value

        # Then, call this function whenever the topic_var changes:
        self.topic_var.trace_add('write', update_mid_time_state)

        def update_event(*args):
            # Store previous values
            previous_start_time = self.event['start_time']
            previous_end_time = self.event['end_time']

            # Verify that the time entered is within the DataFrame's timestamps
            start_time_str = self.start_time_combo.get()
            end_time_str = self.end_time_combo.get()

            start_time = datetime.strptime(start_time_str, '%H:%M').time()  # Extract the time part
            end_time = datetime.strptime(end_time_str, '%H:%M').time()  # Extract the time part

            # Combine the time with today's date to allow subtraction
            start_datetime = datetime.combine(datetime.today(), start_time)
            end_datetime = datetime.combine(datetime.today(), end_time)

            # Initialize the list of mid times
            mid_times = []

            # Generate mid times at 5-minute intervals
            current_time = start_datetime + timedelta(minutes=5)  # Start 5 minutes after the start time
            while current_time < end_datetime:  # Don't include the end time
                mid_times.append(current_time)
                current_time += timedelta(minutes=5)  # Increase by 5 minutes each time

            # If the number of mid times is less than 10, generate more mid times at smaller intervals
            if len(mid_times) < 10:
                mid_times = []
                interval_minutes = (
                                           end_datetime - start_datetime).seconds // 60 // 10  # Ensure at least 1 min intervals
                current_time = start_datetime + timedelta(
                    minutes=interval_minutes)  # Start from the calculated interval after the start time
                while current_time < end_datetime:  # Don't include the end time
                    mid_times.append(current_time)
                    current_time += timedelta(
                        minutes=interval_minutes)  # Increase by the calculated interval minutes each time

            # Convert the datetime objects back to strings
            mid_times = [time.strftime('%H:%M') for time in mid_times]

            # Add an empty option to the start of the list
            mid_times.insert(0, '')

            # Set these values to the mid_time_combo
            self.mid_time_combo['values'] = mid_times

            df_min_time = df['time'].min().time()
            df_max_time = df['time'].max().time()

            if not (df_min_time <= start_time <= df_max_time and df_min_time <= end_time <= df_max_time):
                messagebox.showerror("Invalid Time", "Error: Time entered is beyond the DataFrame time range.")

                # Restore previous values
                self.start_time_combo.set(previous_start_time)
                self.end_time_combo.set(previous_end_time)
                return

            mid_time = self.mid_time_combo.get() if self.mid_time_combo['state'] == 'readonly' else None

            self.event = {
                'topic': self.get_topic(),
                'start_time': start_time_str,
                'mid_time': mid_time,
                'end_time': end_time_str,
                'description': self.description_entry.get()
            }

            # Update the event in events_today
            self.events[self.event_index] = self.event

            # # Update the event and save it to JSON
            # save_data()

        # Now update the mid_time_combo for the first time
        update_event()

        # Call update_event when the values change
        self.topic_var.trace("w", update_event)
        self.start_time_combo.bind('<<ComboboxSelected>>', update_event)
        self.mid_time_combo.bind('<<ComboboxSelected>>', update_event)
        self.end_time_combo.bind('<<ComboboxSelected>>', update_event)
        self.description_entry.bind('<KeyRelease>', update_event)

        self.row = row
        self.widgets = [topic_button, self.part_consumable_button, self.start_time_combo, self.mid_time_combo,
                        self.end_time_combo, self.description_entry, delete_button]
        self.event = event

    def reposition_widgets(self):
        for i, widget in enumerate(self.widgets):
            widget.grid(row=self.row_num, column=i)

    def add_menu_items(self, menu, items):
        for item in items:
            if item.startswith('--') and item.endswith('--'):
                menu.add_command(label=item, font=font.Font(weight='bold'), state='disabled')
            else:
                menu.add_command(label=item, command=lambda i=item: self.update_topic_and_description(i))

    def get_topic(self):
        return self.topic_var.get()

    def delete(self):
        # Remove widgets
        for widget in self.widgets:
            widget.grid_remove()

        # Remove this event from the list
        event_rows.remove(self)
        try:
            events_today.remove(self.event)
        except ValueError:
            print("Warning: Tried to remove an event that doesn't exist in the events_today list.")

        # Update the row numbers of the remaining EventRows and reposition their widgets
        for i, event_row in enumerate(event_rows):
            event_row.row_num = i + 3
            event_row.reposition_widgets()

        # Update the "Add Event" button position
        add_button_frame.grid(row=len(event_rows) + 3, column=0, columnspan=7)

    def add_part_consumable_menu_items(self, menu, items):
        # Clear the menu
        menu.delete(0, 'end')

        # Add items with command to update button text
        for item in items:
            menu.add_command(label=item, command=lambda item=item: self.part_consumable_button.config(text=item))

    def load_csv_order_parts(self):
        # Load the csv file into a pandas DataFrame
        df = pd.read_csv("SNOW/parts.csv")

        # Filter the DataFrame based on 'Part Serial Number' and 'Replaced' conditions
        df_filtered = df[(df['Part Serial Number'].astype(str) == '70001005') & (df['Replaced'] != 1)]

        # Combine the 'Product' and 'Description' columns
        items = df_filtered['Product'] + " - " + df_filtered['Description']

        # Convert the result to a list
        return items

    def load_json_consumables(self):
        # Get today's date in the correct format
        # today = datetime.now().strftime("%Y-%m-%d")

        # Open and read the JSON file
        with open("data/consumables_counter.json", 'r') as f:
            data = json.load(f)

        # Check if today's date is in the JSON file
        if today not in data:
            return []

        # Get the items for today's date
        todays_items = data[today]

        # Initialize an empty list to hold the items
        items = []

        # Iterate over the items for today's date
        for item, values in todays_items.items():
            # Ignore "UTK parts" and "Raw material"
            if item in ["UTK parts", "Raw material"]:
                continue

            # Check if the item is a blanket (string values)
            if isinstance(values, str):
                if int(values) >= 1:
                    items.append(item)
                continue

            # Check if the value 1 appears at least once in the item's values
            if 1 in values:
                items.append(item)

        # Return the items
        return items

    def on_description_focus(self, event):
        if not self._description_focused:
            self.description_entry.delete(0, 'end')
            self._description_focused = True

    def update_topic_and_description(self, topic):
        # Update the topic
        self.topic_var.set(topic)

        # Update the description
        default_description = self.topic_descriptions.get(topic, "")
        self.description_entry.delete(0, 'end')
        self.description_entry.insert(0, default_description)

        # Check if the selected topic involves part replacement or consumable replacement
        if "Part replace" in topic or "Part replacement" in topic:
            self.part_consumable_button.config(state='normal')  # Enable the button
            items = self.load_csv_order_parts()  # Load items from parts CSV
            self.add_part_consumable_menu_items(self.part_consumable_menu,
                                                items)  # Add items to the part/consumable menu
        elif "Consumable replace" in topic:
            self.part_consumable_button.config(state='normal')  # Enable the button
            items = self.load_json_consumables()  # Load items from consumables CSV
            self.add_part_consumable_menu_items(self.part_consumable_menu,
                                                items)  # Add items to the part/consumable menu
        else:
            self.part_consumable_button.config(state='disabled')  # Disable the button


class CheckBoxInterface:
    def __init__(self, window):
        self.window = window  # This line is added
        self.checkbox_frame = tk.Frame(self.window)
        self.titles = ['Asid', 'CS wipers', 'CS sponge', 'CR roller', 'BID Developer', 'BID base', 'Blanket',
                       'UTK parts', 'Raw material']
        self.checkbox_vars = []
        self.comboboxes = []
        self.today = str(datetime.today().date())
        self.data = self.load_data()
        self.create_interface()

    def load_data(self):
        try:
            with open('data/consumables_counter.json', 'r') as f:
                data = json.load(f)
        except FileNotFoundError:
            data = {}
        if self.today not in data:
            data[self.today] = {
                title: [False, False, False, False, False, False] if title in self.titles[:6] else "0"
                for title in self.titles}
        return data

    def save_data(self, *args):
        for i, title in enumerate(self.titles[:6]):
            self.data[self.today][title] = [var.get() for var in self.checkbox_vars[i * 6:(i + 1) * 6]]
        for i, combo in enumerate(self.comboboxes):
            self.data[self.today][self.titles[i + 6]] = combo.get()
        with open('data/consumables_counter.json', 'w') as f:
            json.dump(self.data, f, indent=4)

    def create_interface(self):
        for header_num in range(6):
            header = tk.Label(self.checkbox_frame, text=self.titles[header_num], font=("Arial", 10))
            header.grid(row=0, column=header_num * 2)

            frame = tk.Frame(self.checkbox_frame)
            frame.grid(row=1, column=header_num * 2)

            for i in range(6):
                var = tk.IntVar(value=self.data[self.today][self.titles[header_num]][i])
                self.checkbox_vars.append(var)
                var.trace('w', self.save_data)
                row, col = divmod(i, 2)
                if col == 0:
                    lbl = tk.Label(frame, text=f"{i + 1}")
                    lbl.grid(row=row, column=col * 2)
                    chk = tk.Checkbutton(frame, variable=var)
                    chk.grid(row=row, column=col * 2 + 1)
                else:
                    chk = tk.Checkbutton(frame, variable=var)
                    chk.grid(row=row, column=col * 2)
                    lbl = tk.Label(frame, text=f"{i + 1}")
                    lbl.grid(row=row, column=col * 2 + 1)

        separator_solid = ttk.Separator(self.checkbox_frame, orient='vertical')
        separator_solid.grid(row=0, column=12, rowspan=3, sticky='ns')

        header = tk.Label(self.checkbox_frame, text="Blanket", font=("Arial", 10))
        header.grid(row=0, column=14)

        frame = tk.Frame(self.checkbox_frame)
        frame.grid(row=1, column=14)

        values = [str(i) for i in range(7)]
        combo = ttk.Combobox(frame, values=values, width=2)
        combo.set(self.data[self.today]["Blanket"])
        combo.bind('<<ComboboxSelected>>', self.save_data)
        self.comboboxes.append(combo)
        combo.pack()

        separator_solid = ttk.Separator(self.checkbox_frame, orient='vertical')
        separator_solid.grid(row=0, column=16, rowspan=3, sticky='ns')

        more_headers = ['UTK parts', 'Raw material']
        for i, header_name in enumerate(more_headers):
            header = tk.Label(self.checkbox_frame, text=header_name, font=("Arial", 10))
            header.grid(row=0, column=18 + i * 2)

            frame = tk.Frame(self.checkbox_frame)
            frame.grid(row=1, column=18 + i * 2)

            combo = ttk.Combobox(frame, values=values, width=2)
            combo.set(self.data[self.today][header_name])
            combo.bind('<<ComboboxSelected>>', self.save_data)
            self.comboboxes.append(combo)
            combo.pack()

        # Apply column configuration after creating the widgets
        self.checkbox_frame.grid_columnconfigure(1, minsize=25)
        self.checkbox_frame.grid_columnconfigure(3, minsize=25)
        self.checkbox_frame.grid_columnconfigure(5, minsize=25)
        self.checkbox_frame.grid_columnconfigure(7, minsize=25)
        self.checkbox_frame.grid_columnconfigure(9, minsize=25)
        self.checkbox_frame.grid_columnconfigure(11, minsize=10)

    ####################################################################################################################
    ####################################################################################################################
    ####################################################################################################################


def save_data():
    # Rebuild the events_today list from the event_row objects
    events_today_rebuilt = []

    for event_row in event_rows:
        event = event_row.event
        mid_time = event_row.mid_time_combo.get() if event_row.mid_time_combo.get() != '' else None

        event_copy = {
            'topic': event['topic'],
            'start_time': event['start_time'],
            'mid_time': mid_time,
            'end_time': event['end_time'],
            'description': event['description']
        }
        events_today_rebuilt.append(event_copy)

    # Remove duplicates from events_today_rebuilt
    events_today_rebuilt = [dict(t) for t in set(tuple(event.items()) for event in events_today_rebuilt)]

    # Find the entry for today in data
    for day_events in data["Main events"]:
        if day_events["date"] == today:
            # Update the entry with the rebuilt events list
            day_events["events"] = events_today_rebuilt
            break
    else:  # This else clause belongs to the for loop, not the if statement
        # If no entry for today was found, create a new one
        data["Main events"].append({"date": today, "events": events_today_rebuilt})

    # Write data to file
    with open("data/main_events_archive.json", "w") as file:
        json.dump(data, file, indent=4)


def add_event(root, events_today, event_rows, add_button_frame):
    # Create a new event
    event = {'topic': '', 'start_time': '08:00', 'mid_time': '', 'end_time': '08:00', 'description': ''}

    # Add to events_today
    events_today.append(event)

    # Create a new row for the event
    event_row = EventRow(root, len(event_rows) + 3, events_today, len(event_rows), event_rows, event)
    event_rows.append(event_row)

    # Update the "Add Event" button position
    add_button_frame.grid(row=len(event_rows) + 3, column=0, columnspan=7)


def close_window(root):
    save_data()
    time.sleep(1)  # Delay for 1 second
    root.destroy()


def run_daily_gui(events_today):
    root = tk.Tk()
    root.title("Daily Report")
    # root.iconbitmap('logo.ico')
    root.geometry("1000x600")

    # Save data when the application is about to close
    root.protocol("WM_DELETE_WINDOW", close_window(root))

    # Configure the column containing the description_entry widgets to be stretchable
    root.grid_columnconfigure(5, weight=1)

    # Add CheckBoxInterface to the application
    checkbox_interface = CheckBoxInterface(root)
    checkbox_interface.checkbox_frame.grid(row=0, column=0, columnspan=8)  # Place it on top

    # Add a horizontal line separator
    separator = ttk.Separator(root, orient="horizontal")
    separator.grid(row=1, column=0, columnspan=8, sticky="ew")

    # Create labels
    labels = ["Topic", "Parts", "Start time", "Mid time", "End time", "Description", "Delete"]
    for i, label in enumerate(labels):
        tk.Label(root, text=label).grid(row=2, column=i, padx=5)

    # Create the frame for the "Add Event" button
    add_button_frame = tk.Frame(root)

    # Create a button to add new events
    add_button = tk.Button(add_button_frame, text="Add Event", command=add_event(root, events_today, event_rows, add_button_frame))
    add_button.pack()

    event_rows = []  # List to hold all EventRow objects
    for index, event in enumerate(events_today):
        event_row = EventRow(root, index + 3, events_today, index, event)
        event_rows.append(event_row)

    # If there were no events loaded from file, add an empty event
    if len(event_rows) == 0:
        add_event(root, events_today, event_rows, add_button_frame)
    else:
        add_button_frame.grid(row=len(event_rows) + 3, column=0,
                              columnspan=7)  # Consider the total number of EventRow items and offset by 3

    root.mainloop()

    ########################################################################################################################
    ########################################################################################################################
    ########################################################################################################################

    # List to hold text objects
    texts = []

    # Define state colors
    state_colors = {
        'Off': '#BC0E00',
        # 'Init': '#BC0E00',
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

    # List of all topics
    topics_menu = [
        "--Troubleshooting--", "SW issue", "PQ issue", "PQ issue + fix / clean", "PQ issue + Part replace",
        "PQ issue + Consumable replace", "HW issue", "HW issue + fix / clean", "HW issue + Part replace",
        "HW issue + Consumable replace", "other",
        "--Active actions--", "Part replacement", "Scheduled Maintenance", "Unscheduled Maintenance", "Web break",
        "other",
        "--Site's reasons--", "Operator duties", "Pending job", "Pending substrate", "Site maintenance", "other",
        'Combined', 'Ready'
    ]

    # Prepare a color palette for topics
    topics = [topic for topic in topics_menu if not topic.startswith('--')]  # Filter out the titles

    # Three families of topics with different shades of colors
    families = {
        'PQ issue': ['PQ issue', 'PQ issue + fix / clean', 'PQ issue + Part replace', 'PQ issue + Consumable replace'],
        'HW issue': ['HW issue', 'HW issue + fix / clean', 'HW issue + Part replace', 'HW issue + Consumable replace',
                     'Part replacement', 'Web break'],
        'Maintenance': ['Scheduled Maintenance', 'Unscheduled Maintenance', 'Site maintenance'],
        'Other': ['Operator duties', 'Pending job', 'Pending substrate', 'Site maintenance', 'other', 'Combined',
                  'Ready',
                  'SW issue']
    }

    colormaps = {
        'PQ issue': 'Purples',
        'HW issue': 'Reds',
        'Maintenance': 'Greens',
        'Other': 'Greys'
    }

    topic_colors = {}
    for family, colormap in colormaps.items():
        cmap = plt.get_cmap(colormap)
        colors = cmap(np.linspace(0.3, 1, len(families[family])))  # Generate colors from the colormap
        topic_colors.update(zip(families[family], colors))  # Assign colors to topics

    # Create the horizontal bar plot
    fig, (ax2, ax1) = plt.subplots(2, figsize=(20, 3), sharex=True, gridspec_kw={'height_ratios': [1, 1], 'hspace': 0})

    # For ax1, create a neutral color plot
    prev_time = df['time'].iloc[0]
    for index, row in df.iterrows():
        if index == 0:
            continue
        ax1.barh(0, row['time'] - prev_time, left=prev_time, height=0.5, color='whitesmoke')
        prev_time = row['time']

    # For ax2, create a colored plot by state
    prev_time = df['time'].iloc[0]
    prev_state = df[press_state].iloc[0]
    for index, row in df.iterrows():
        if index == 0:
            continue
        ax2.barh(0, row['time'] - prev_time, left=prev_time, height=1, color=state_colors[prev_state])
        prev_time = row['time']
        prev_state = row[press_state]

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

    # Set the y-axis limits for ax1
    ax1.set_ylim(0, max(y_positions) + 0.01)  # Adjust this to fit your texts

    # Create a custom legend handle for the failure symbol
    failure_handle = Line2D([0], [0], marker='X', color='None', markerfacecolor='red', markeredgecolor='red',
                            markersize=8)
    UW_failure_handle = Line2D([0], [0], marker='^', color='None', markerfacecolor='blue', markeredgecolor='blue',
                               markersize=8)
    RW_failure_handle = Line2D([0], [0], marker='v', color='None', markerfacecolor='green', markeredgecolor='green',
                               markersize=8)

    # Get unique topics from events_today
    used_topics = set(event['topic'] for event in events_today)

    # Create a list for storing sorted topics
    sorted_topics = []

    # Iterate over each family and append the used topics in this family to sorted_topics
    for family in families:
        for topic in families[family]:
            if topic in used_topics:
                sorted_topics.append(topic)

    # Now sorted_topics contains the topics sorted according to the order in families

    # Create legend handles only for the sorted topics
    topic_handles = [plt.Rectangle((0, 0), 1, 1, color=topic_colors[topic]) for topic in sorted_topics]
    topic_handles.append(failure_handle)
    topic_handles.append(UW_failure_handle)
    topic_handles.append(RW_failure_handle)

    # Create the first legend for topics
    topic_labels = sorted_topics + ['Failure', 'UW empty', 'RW full']

    # Compute the number of columns based on the number of used topics
    ncol = len(sorted_topics) // 5 if len(sorted_topics) % 5 == 0 else len(sorted_topics) // 5 + 1

    state_legend_handles = [plt.Rectangle((0, 0), 1, 1, color=state_colors[state]) for state in state_colors]

    # Remove the bottom spine of ax2
    ax2.spines['bottom'].set_visible(False)

    # Remove the top spine of ax1
    ax1.spines['top'].set_visible(False)

    for index, row in df_failures.iterrows():
        ax1.plot(row['time'], 0.007, marker='X', color='red', markersize=8)
    # Plot for df_failures_UW
    for index, row in df_failures_UW.iterrows():
        ax1.plot(row['time'], 0.007, marker='^', color='blue', markersize=8)

    # Plot for df_failures_RW
    for index, row in df_failures_RW.iterrows():
        ax1.plot(row['time'], 0.007, marker='v', color='green', markersize=8)

    #########################################################

    fig_leg1, ax_leg1 = plt.subplots()
    ax_leg1.axis('off')
    legend1 = plt.legend(topic_handles, topic_labels, loc='center', ncol=int(np.ceil(len(topic_handles) / 5)),
                         edgecolor='black', fancybox=True)
    legend1.set_title('Topics')
    ax_leg1.add_artist(legend1)

    # Update the figure size to fit the legend
    fig_leg1.canvas.draw()
    bbox = legend1.get_window_extent().transformed(fig_leg1.dpi_scale_trans.inverted())
    fig_leg1.savefig('Images/legend1.png', dpi=300, bbox_inches=bbox)

    fig_leg2, ax_leg2 = plt.subplots()
    ax_leg2.axis('off')
    legend2 = plt.legend(state_legend_handles, state_colors.keys(), loc='center',
                         ncol=int(np.ceil(len(state_legend_handles) / 5)), edgecolor='black', fancybox=True)
    legend2.set_title('Press States')
    ax_leg2.add_artist(legend2)

    # Update the figure size to fit the legend
    fig_leg2.canvas.draw()
    bbox = legend2.get_window_extent().transformed(fig_leg2.dpi_scale_trans.inverted())
    fig_leg2.savefig('Images/legend2.png', dpi=300, bbox_inches=bbox)

    fig.savefig('Images/main_plot.png', dpi=300, bbox_inches='tight')
