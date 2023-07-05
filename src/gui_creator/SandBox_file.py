import pycountry
import pygetwindow as gw
import pyperclip
import win32com.client as win32

import getpass
import json
import os
import subprocess
import threading
import time
import tkinter as tk
from datetime import datetime
from tkinter import *
from tkinter import ttk

from src.gui_creator.gui_utilities.event_handling_frame import EventHandlingFrame

username = getpass.getuser()

# Initialize a global row index
global_row_index = 0

# Directory of python scripts and images
# dir_path = "c:\\Users\\elazar\\OneDrive - HP Inc\\Documents\\Daily Report\\"
dir_path = "src\\dataAnalysis\\"

# List of python scripts
python_files = [
    os.path.join(dir_path, 'state_timeline_graph_with_restart.py'),
    os.path.join(dir_path, 'pie_chart_states_with_restart.py'),
    os.path.join(dir_path, 'failure_graph.py')
]


# Function to execute Python scripts
def execute_python_scripts():
    for file in python_files:
        subprocess.run(['python', file], check=True)


# List of images
image_files = [
    os.path.join(dir_path, 'state_timeline_graph_with_restart.png'),
    os.path.join(dir_path, 'failure_graph.png'),
    os.path.join(dir_path, 'pie_chart_states_with_restart.png')
]

# Thread for executing Python scripts
script_thread = threading.Thread(target=execute_python_scripts)
script_thread.start()

# Define the press status options and their associated colors
PRESS_STATUS_OPTIONS = [
    ('Up & Running', 'green'),
    ('Running with limitation', 'orange'),
    ('Proactive shutdown', '#999900'),
    ('Pending customer', 'purple'),
    ('MD - Troubleshooting', 'red'),
    ('MD - Waiting for parts', 'red'),
    ('MD - Escalation', 'red')
]
SHIFT_OPTIONS = ['Morning', 'Noon', 'Night']


def fse_data_gui():
    def delete_row(container, row, status_vars, row_counters):
        for widget in container.grid_slaves(row=row):
            widget.destroy()
        del status_vars[id(container), row]
        row_counters[container] -= 1

    def create_row(container, name, status, row, status_vars, row_counters):
        name_entry = tk.Entry(container)
        status_var = tk.IntVar(value=1 if status == "Active" else 0)
        check = tk.Checkbutton(container, variable=status_var)
        if status == "Active":
            check.select()
        del_button = tk.Button(container, text="Delete",
                               command=lambda row=row: delete_row(container, row, status_vars, row_counters))

        check.grid(row=row, column=0)
        name_entry.grid(row=row, column=1)
        name_entry.insert(0, name)
        del_button.grid(row=row, column=2)

        status_vars[id(container), row] = status_var, name_entry

    def add_person(container, status_vars, row_counters):
        row = row_counters[container]
        create_row(container, "", "Active", row, status_vars, row_counters)
        row_counters[container] += 1

    def save_data(window, row_counters, status_vars, original_keys):
        data = {}
        for container in row_counters:
            key = original_keys[id(container)]
            rows = sorted(i for i in status_vars if i[0] == id(container))  # get all valid rows in this container
            data[key] = [
                {"name": status_vars[row][1].get(), "status": "Active" if status_vars[row][0].get() else "Inactive"} for
                row in rows]

        with open('data/fse_data.json', 'w') as file:
            json.dump(data, file, indent=2)

        window.destroy()

    def load_and_create_window():
        with open('data/fse_data.json', 'r') as file:
            data = json.load(file)

        window = tk.Toplevel()
        window.title("FSE Data")

        row_counters = {}
        status_vars = {}
        original_keys = {}

        for i, (key, values) in enumerate(data.items()):
            frame = tk.LabelFrame(window, text=key)
            frame.grid(row=0, column=i, padx=10, pady=10, sticky='ns')

            row_counters[frame] = 0
            original_keys[id(frame)] = key

            if isinstance(values, list):
                for value in values:
                    row = row_counters[frame]
                    create_row(frame, value.get('name', ''), value.get('status', ''), row, status_vars, row_counters)
                    row_counters[frame] += 1
            else:
                row = row_counters[frame]
                create_row(frame, values.get('name', ''), values.get('status', ''), row, status_vars, row_counters)
                row_counters[frame] += 1

            add_button = tk.Button(frame, text="Add Person",
                                   command=lambda frame=frame: add_person(frame, status_vars, row_counters))
            add_button.grid(row=1000, columnspan=3)

        save_button = tk.Button(window, text="Save",
                                command=lambda: save_data(window, row_counters, status_vars, original_keys))
        save_button.grid(row=1, column=0, columnspan=3, sticky='we')

        window.mainloop()

    load_and_create_window()


def minimize_teams():
    teams_window = gw.getWindowsWithTitle("Microsoft Teams")[0]
    if teams_window is not None:
        teams_window.minimize()


def open_teams_and_copy():
    # Open Teams application.
    subprocess.Popen([rf"C:\Users\{username}\AppData\Local\Microsoft\Teams\Update.exe", "--processStart", "Teams.exe"])

    # Clear the clipboard
    pyperclip.copy("")

    # Now check clipboard in a loop until we have Teams link
    copied_data = ""
    start_time_teams = time.time()
    while not copied_data.startswith("https://teams.microsoft.com/"):
        copied_data = pyperclip.paste()
        time.sleep(0.1)
        if time.time() - start_time_teams > 60:  # If clipboard checking takes longer than 60 seconds
            return None

    # Minimize the Teams window
    minimize_teams()

    return copied_data


def display_country_flag():
    # Load data from the text file
    with open('data/general_info_data.txt', 'r') as file:
        data = json.load(file)

    # Find the country code for the given location (in English)
    country_name = data['Location'].split(", ")[-1]
    country_info = pycountry.countries.get(name=country_name)
    country_code = country_info.alpha_2.lower() if country_info else None

    if country_code:
        # Get the country flag from the 'flagpedia.net' API
        flag_url = f"https://flagpedia.net/data/flags/emoji/twitter/256x256/{country_code}.png"
        return flag_url


def load_general_info_data():
    with open('data/general_info_data.txt') as f:
        data = json.load(f)

    today = datetime.today()

    for key in ["SW Version", "PLC Version", "DFE Version"]:
        change_date_key = f"{key} Change Date"
        if change_date_key in data:
            change_date = datetime.strptime(data[change_date_key], '%Y-%m-%d')
            days_diff = (today - change_date).days

            if days_diff == 0:
                data[key] += "<br><span style='font-size: 12px; color: green;'>(updated today)</span>"
            elif days_diff <= 14:
                data[key] += "<br><span style='font-size: 12px; color: orange;'>(recently updated)</span>"

    return data


def get_day_counters(press_status):
    filename = 'data/general_info_history.json'
    with open(filename, 'r') as f:
        data = json.load(f)

    # Get today's date in 'YYYY-MM-DD' format
    today_date = datetime.now().date().isoformat()

    # If last record is from today's date, remove it
    if data and data[-1]['date'] == today_date:
        data.pop()

    # Append today's press_status
    data.append({
        "date": today_date,
        "machine_state": press_status
    })

    # Overwrite the JSON file with updated data
    with open(filename, 'w') as f:
        json.dump(data, f)

    # Compute the counters
    same_state_days = 0
    md_state_days = 0

    # Loop over the data in reverse order
    for record in reversed(data):
        current_state = record["machine_state"]

        # If state is the same as press_status, increment same_state_days
        if current_state == press_status:
            same_state_days += 1
        else:
            # Stop counting if state is not the same
            break

    # Loop over the data in reverse order for md_state_days
    if press_status.startswith("MD"):
        for record in reversed(data):
            current_state = record["machine_state"]

            # If state starts with "MD", increment md_state_days
            if current_state.startswith("MD"):
                md_state_days += 1
            else:
                # Stop counting if state doesn't start with "MD"
                break

    return same_state_days, md_state_days


# def get_day_counters(press_status):
#     filename = 'data/general_info_history.json'
#     with open(filename, 'r') as f:
#         data = json.load(f)

#     # Initialize counters and previous state
#     same_state_days = 0
#     md_state_days = 0
#     previous_state = None

#     # Loop over the data
#     for record in data:
#         current_state = record["machine_state"]
#         previous_state = current_state  # Update previous state for the next iteration

#     # If the latest state is the same as the user selected status, increment same_state_days
#     if press_status == previous_state:
#         same_state_days = len([rec for rec in data if rec["machine_state"] == press_status]) +1
#     else:
#         same_state_days = 1

#     # If the latest state starts with "MD", increment or reset md_state_days
#     if press_status.startswith("MD"):
#         md_state_days = len([rec for rec in data if rec["machine_state"].startswith("MD")])+1
#     else:
#         md_state_days = 0

#     return same_state_days, md_state_days


def add_highlight_entry():
    frame = tk.Frame(window)
    entry = tk.Entry(frame, width=70)

    # Load Teams logo, resize it, and create a button
    logo = PhotoImage(file="teams_logo.png")
    logo = logo.subsample(int(logo.width() / 19), int(logo.height() / 19))  # resize

    # Modify the command of the Teams button to save the returned value
    teams_button = tk.Button(frame, image=logo, command=lambda: copied_links.append(open_teams_and_copy()))
    teams_button.image = logo  # Keep a reference to prevent garbage collection

    delete_button = tk.Button(frame, text="Delete", command=lambda: delete_entry(frame, entry, highlight_entries))

    entry.grid(row=0, column=0, sticky='we', padx=(0, 5))
    teams_button.grid(row=0, column=1, padx=(0, 10))  # Added padding (right) to create gap
    delete_button.grid(row=0, column=2)

    frame.grid_columnconfigure(0, weight=1)
    frame.grid(row=len(highlight_entries) + 4, column=0, sticky="we")

    highlight_entries.append((frame, entry))

    # Rearrange elements
    rearrange_highlight_entries(highlight_entries, window)


def display_issues():
    global global_row_index
    # Load data from the JSON file
    with open('data/main_open_issues.json', 'r') as file:
        data = json.load(file)

    for issue in data["case"]:
        # Create new frame and entries
        frame = tk.Frame(window)
        case_entry = tk.Entry(frame, width=20)
        description_entry = tk.Entry(frame, width=30)
        update_entry = tk.Entry(frame, width=20)

        # Calculate day counter based on creation date
        creation_date = datetime.strptime(issue["creation date"], "%d-%m-%Y")
        day_counter = (datetime.now() - creation_date).days

        # Create the day_counter label
        day_counter_label = tk.Label(frame, text=str(day_counter), width=5)
        day_counter_label.grid(row=1, column=3, sticky='we')

        teams_link = issue["teams conversation"]

        # Load Teams logo, resize it, and create a button
        if teams_link:
            logo = PhotoImage(file="teams_logo_bw.png")
        else:
            logo = PhotoImage(file="teams_logo.png")
        logo = logo.subsample(int(logo.width() / 19), int(logo.height() / 19))  # resize

        issue_entry = {"frame": frame, "entries": (case_entry, description_entry, update_entry),
                       "day_counter": day_counter, "teams_link": teams_link}

        # Teams button that updates the issue's teams link
        teams_button = tk.Button(frame, image=logo, command=lambda issue_entry=issue_entry: issue_entry.update(
            {"teams_link": open_teams_and_copy()}))
        teams_button.image = logo  # Keep a reference to prevent garbage collection
        # teams_button.grid(row=1, column=5)

        # Now, after issue_entry is defined, create the delete button
        delete_button = tk.Button(frame, text="Delete",
                                  command=lambda frame=frame, issue_entry=issue_entry: delete_entry(frame, issue_entry,
                                                                                                    issue_entries))

        # Set entry values
        case_entry.insert(0, issue["Case Number"])
        description_entry.insert(0, issue["description"])

        # Create labels
        case_label = tk.Label(frame, text="Case Number:")
        description_label = tk.Label(frame, text="Description:")
        update_label = tk.Label(frame, text="Update:")

        # Grid layout
        case_label.grid(row=0, column=0)
        case_entry.grid(row=1, column=0, sticky='we')
        description_label.grid(row=0, column=1)
        description_entry.grid(row=1, column=1, sticky='we')
        update_label.grid(row=0, column=2)
        update_entry.grid(row=1, column=2, sticky='we')
        day_counter_label.grid(row=1, column=3)
        teams_button.grid(row=1, column=4, padx=(0, 10))
        delete_button.grid(row=1, column=5, rowspan=2)

        frame.grid_columnconfigure(0, weight=0)
        frame.grid_columnconfigure(1, weight=1)
        frame.grid_columnconfigure(2, weight=1)
        frame.grid(row=global_row_index, column=0, sticky="we")
        global_row_index += 1

        issue_entries.append(issue_entry)

        # Rearrange elements
        rearrange_issue_entries(highlight_entries, issue_entries, window)


def add_issue_entry():
    global global_row_index
    frame = tk.Frame(window)
    case_entry = tk.Entry(frame, width=20)
    description_entry = tk.Entry(frame, width=30)
    update_entry = tk.Entry(frame, width=20)

    # Create the day_counter label for new issues
    day_counter_label = tk.Label(frame, text="new")
    day_counter_label.grid(row=1, column=3, sticky='we')

    # Load Teams logo, resize it, and create a button
    logo = PhotoImage(file="teams_logo.png")
    logo = logo.subsample(int(logo.width() / 19), int(logo.height() / 19))  # resize
    teams_link = ""

    issue_entry = {"frame": frame, "entries": (case_entry, description_entry, update_entry), "day_counter": "new",
                   "teams_link": teams_link}

    # Teams button that updates the issue's teams link
    teams_button = tk.Button(frame, image=logo,
                             command=lambda: issue_entry.update({"teams_link": open_teams_and_copy()}))
    teams_button.image = logo  # Keep a reference to prevent garbage collection
    # teams_button.grid(row=1, column=5)

    # Now, after issue_entry is defined, create the delete button
    delete_button = tk.Button(frame, text="Delete",
                              command=lambda frame=frame, issue_entry=issue_entry: delete_entry(frame, issue_entry,
                                                                                                issue_entries))

    case_label = tk.Label(frame, text="Case Number:")
    description_label = tk.Label(frame, text="Description:")
    update_label = tk.Label(frame, text="Update:")
    day_counter_label = tk.Label(frame, text="new", width=5)

    case_label.grid(row=0, column=0)
    case_entry.grid(row=1, column=0, sticky='we')
    description_label.grid(row=0, column=1)
    description_entry.grid(row=1, column=1, sticky='we')
    update_label.grid(row=0, column=2)
    update_entry.grid(row=1, column=2, sticky='we')
    day_counter_label.grid(row=1, column=3)
    teams_button.grid(row=1, column=4, padx=(0, 10))
    delete_button.grid(row=1, column=5, rowspan=2)

    frame.grid_columnconfigure(0, weight=0)
    frame.grid_columnconfigure(1, weight=1)
    frame.grid_columnconfigure(2, weight=1)
    frame.grid(row=global_row_index, column=0, sticky="we")
    global_row_index += 1

    issue_entries.append(issue_entry)

    # Rearrange elements
    rearrange_issue_entries(highlight_entries, issue_entries, window)


def delete_entry(frame, issue_entry, issue_entries):
    # Remove the entry from the entries list before destroying the frame
    for entry in issue_entries:
        if isinstance(entry, dict):
            if entry["frame"] == frame and entry["entries"] == issue_entry["entries"]:
                issue_entries.remove(entry)
                frame.destroy()  # Here, destroy the frame.
                # Rearrange elements
                rearrange_highlight_entries(highlight_entries, window)
                rearrange_issue_entries(highlight_entries, issue_entries, window)
                break
        elif isinstance(entry, tuple):
            if entry[0] == frame and entry[1] == issue_entry:
                issue_entries.remove(entry)
                frame.destroy()  # Here, destroy the


def rearrange_highlight_entries(highlight_entries, window):
    global global_row_index  # declare global_row_index as global
    for i, entry in enumerate(highlight_entries):
        entry[0].grid(row=i + 6, column=0, sticky="we")  # +6 to account for widgets above

    add_highlight_button.grid(row=len(highlight_entries) + 6, column=0)  # move the 'Add Highlight' button
    separator.grid(row=len(highlight_entries) + 7, column=0, sticky="we", padx=5, pady=5)  # move the separator

    global_row_index = len(highlight_entries) + 8  # Set global_row_index based on highlight entries


def rearrange_issue_entries(highlight_entries, issue_entries, window):
    global global_row_index  # declare global_row_index as global
    issue_label.grid(row=global_row_index, column=0, sticky="w")  # move the 'Main Open Issues' label

    for i, issue_entry in enumerate(issue_entries):
        frame = issue_entry["frame"]
        if frame.winfo_exists():  # check if frame exists before adjusting grid position
            frame.grid(row=global_row_index + i + 1, column=0)  # +1 to leave space for the label

    add_issue_button.grid(row=global_row_index + len(issue_entries) + 1, column=0)  # move the 'Add Issue' button

    global_row_index += len(issue_entries) + 2  # Update global_row_index for the next time


def launch_checkbox_interface(window):
    # Function to save the current state of the checkboxes and comboboxes
    def save_data():
        # Get the current state of the checkboxes
        for i, title in enumerate(titles[:6]):
            data[today][title] = [var.get() for var in checkbox_vars[i * 6:(i + 1) * 6]]
        # Get the current state of the comboboxes
        for i, combo in enumerate(comboboxes):
            data[today][titles[i + 6]] = combo.get()
        # Save the data back to the file
        with open('data/consumables_counter.json', 'w') as f:
            json.dump(data, f, indent=4)

    # Create the main checkbox_frame
    checkbox_frame = tk.Frame(window)

    # Define titles
    titles = ['Asid', 'CS wipers', 'CS sponge', 'CR roller', 'BID Developer', 'BID base', 'Blanket', 'UTK parts',
              'Raw material']

    # Load data from the json file
    try:
        with open('data/consumables_counter.json', 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        data = {}

    # Get today's date
    today = str(datetime.today().date())

    # If today's data does not exist in the file, initialize it
    if today not in data:
        data[today] = {title: [False, False, False, False, False, False] if title in titles[:6] else "0" for title in
                       titles}

    checkbox_vars = []
    comboboxes = []

    for header_num in range(6):
        # Create a label for the header
        header = tk.Label(checkbox_frame, text=titles[header_num], font=("Arial", 10))
        header.grid(row=0, column=header_num * 2)  # Place the header at the top of the column

        # Create a frame for the checkboxes
        frame = tk.Frame(checkbox_frame)
        frame.grid(row=1, column=header_num * 2)  # Place the frame below the header

        # Create checkboxes
        for i in range(6):
            var = tk.IntVar(value=data[today][titles[header_num]][i])
            checkbox_vars.append(var)
            var.trace('w', lambda *args: save_data())  # Bind the save_data function to the variable
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

    # Create a ttk.Separator for the dividing line
    separator_solid = ttk.Separator(checkbox_frame, orient='vertical')
    separator_solid.grid(row=0, column=12, rowspan=3, sticky='ns')

    # Create the "Blanket" section with a combobox
    header = tk.Label(checkbox_frame, text="Blanket", font=("Arial", 10))
    header.grid(row=0, column=14)

    # Create a frame for the combobox
    frame = tk.Frame(checkbox_frame)
    frame.grid(row=1, column=14)

    # Create combobox with width of 2 characters
    values = [str(i) for i in range(7)]  # Values are strings from "0" to "6"
    combo = ttk.Combobox(frame, values=values, width=2)
    combo.set(data[today]["Blanket"])  # Set the initial value to today's data
    combo.bind('<<ComboboxSelected>>', lambda e: save_data())  # Bind the save_data function to the combobox
    comboboxes.append(combo)
    combo.pack()

    # Create another ttk.Separator for the dividing line
    separator_solid = ttk.Separator(checkbox_frame, orient='vertical')
    separator_solid.grid(row=0, column=16, rowspan=3, sticky='ns')

    # Add 2 more headers and 2 comboboxes
    more_headers = ['UTK parts', 'Raw material']
    for i, header_name in enumerate(more_headers):
        header = tk.Label(checkbox_frame, text=header_name, font=("Arial", 10))
        header.grid(row=0, column=18 + i * 2)

        frame = tk.Frame(checkbox_frame)
        frame.grid(row=1, column=18 + i * 2)

        combo = ttk.Combobox(frame, values=values, width=2)
        combo.set(data[today][header_name])  # Set the initial value to today's data
        combo.bind('<<ComboboxSelected>>', lambda e: save_data())  # Bind the save_data function to the combobox
        comboboxes.append(combo)
        combo.pack()

    # Run the application
    return checkbox_frame


# Function to create an HTML table from the given data
def create_html_table(general_info_data):
    # Load the JSON data from the "fse_data.json" file
    with open("data/fse_data.json", "r") as file:
        fse_data = json.load(file)

    # Create lists to hold the names of present people from each category
    present_wwts_fse = []
    present_local_fse = []
    present_local_T3_other = []

    # Iterate through each category and add the names of present people to the respective list
    for person_info in fse_data['WWTS FSE']:
        if person_info['status'] == "Active" and person_info['name'].strip():
            present_wwts_fse.append(person_info['name'])

    for person_info in fse_data['Local FSE']:
        if person_info['status'] == "Active" and person_info['name'].strip():
            present_local_fse.append(person_info['name'])

    for person_info in fse_data['Local T3 / other']:
        if person_info['status'] == "Active" and person_info['name'].strip():
            present_local_T3_other.append(person_info['name'])

    # Prepare the strings to be included in the table
    wwts_fse_string = '<br>'.join(present_wwts_fse)
    local_fse_string = '<br>'.join(present_local_fse)
    local_T3_other_string = '<br>'.join(present_local_T3_other)

    # Get the current date
    current_date = datetime.now()
    # Format the date
    formatted_date = current_date.strftime("%d %B %Y")

    # Define table data with loaded general info
    flag_url = display_country_flag()

    # Define table data with loaded general info and fse data
    table_data = [
        [("End User", general_info_data.get("End User", "")),
         ("Serial Number", general_info_data.get("Serial Number", "")),
         ("Location", general_info_data.get("Location", "") + f' <img src="{flag_url}" width="20"/>')],

        [("SW Version", general_info_data.get("SW Version", "")),
         ("PLC Version", general_info_data.get("PLC Version", "")),
         ("DFE Version", general_info_data.get("DFE Version", ""))],

        [("WWTS FSE", wwts_fse_string),
         ("Local FSE", local_fse_string),
         ("Local T3/Other", local_T3_other_string)],

        [("Date", formatted_date),
         ("Press Status", general_info_data.get("Press Status", "")),
         ("Shift", " + ".join(var.get() for var in shift_vars if var.get()))]
    ]

    # Generate HTML table
    html_table = "<table style='border-collapse: collapse; width: 100%;'>"
    for row in table_data:
        html_table += "<tr>"
        for cell in row:
            title, content = cell
            html_table += f"<td style='border: 1px solid #000; padding: 5px; padding-top: 10px; vertical-align: middle; text-align:center;'>\
                            <div style='position: relative;'>\
                                <div style='position: absolute; top: 0; font-weight: normal;'>{title}</div>\
                                <div style='font-weight: bold;'>{content}</div>\
                            </div>\
                        </td>"
        html_table += "</tr>"
    html_table += "</table>"

    return html_table


# Function to create square html
def create_square_html():
    with open('data/snow_data.json') as f:
        data = json.load(f)

    square_html = """
    <style>
    .square {
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        background-color: transparent;
        color: black;
        text-decoration: none;
        width: 100%;
        font-size: 2em;
        padding: 0;
        margin: 0;
    }
    .square-table td {
        display: flex;
        align-items: center;
        justify-content: center;
        text-align: center;
        border: 1px solid gray;
        width: """ + str(100 / len(data)) + """%;
    }
    .first-half {
        background-color: #ddf7fe;
    }
    .second-half {
        background-color: #f0eafa;
    }
    .title, .number {
        margin: 0;
        padding: 0;
        line-height: 1em;
    }
    .title {
        font-size: 0.5em;
    }
    a {
        color: black;
        text-decoration: none;
    }
    </style>
    <table class="square-table" style="width: 100%;">
    <tr>
    """
    for index, (title, item) in enumerate(data.items()):
        cell_class = 'first-half' if index < 3 else 'second-half'
        if index == 3:  # check if it's the 4th cell
            square_html += f"""
            <td class="{cell_class}">
                <div class="square">
                    <div class="title">{title.replace('_', ' ').title()}</div>
                    <div class="number">{item['number']}</div>
                </div>
            </td>
            """
        else:
            square_html += f"""
            <td class="{cell_class}">
                <div class="square">
                    <div class="title">{title.replace('_', ' ').title()}</div>
                    <div class="number"><a href="{item['link']}">{item['number']}</a></div>
                </div>
            </td>
            """
    square_html += "</tr></table>"
    return square_html


# Function to open Outlook with the entered details
def open_outlook():
    outlook = win32.Dispatch('outlook.application')
    mail = outlook.CreateItem(0)
    mail.To = "tal.elazar@hp.com"

    image_ids = []
    for image_path in image_files:
        # Ensure images exist
        if os.path.isfile(image_path):
            image_id = 'image_id' + os.path.basename(image_path)
            image_ids.append(image_id)
            attachment = mail.Attachments.Add(Source=image_path)
            attachment.PropertyAccessor.SetProperty("http://schemas.microsoft.com/mapi/proptag/0x3712001F", image_id)

    # Load the general info data
    general_info_data = load_general_info_data()

    # Get the press status and color
    press_status = press_status_var.get()
    color = 'black'
    for status, status_color in PRESS_STATUS_OPTIONS:
        if status == press_status:
            color = status_color
            break

    # Get the day counters without updating the text file
    same_state_days, md_state_days = get_day_counters(press_status)

    # Format the 'Press Status' cell
    # press_status_str = f'<span style="color:{color};">{press_status}</span>'
    # if press_status.startswith("MD"):
    #     press_status_str += f'<br><span style="font-size: 12px;">({same_state_days} days, total {md_state_days} MD)</span>'
    # else:
    #     press_status_str += f'<br><span style="font-size: 12px;">({same_state_days} days)</span>'
    # general_info_data["Press Status"] = press_status_str

    # Format the 'Press Status' cell
    press_status_str = f'<span style="color:{color};">{press_status}</span>'
    if press_status.startswith("MD"):
        if same_state_days == 1 and md_state_days == 1:
            press_status_str += f'<br><span style="font-size: 12px;">(First day)</span>'
        elif same_state_days == 1 and md_state_days > 1:
            press_status_str += f'<br><span style="font-size: 12px;">(First day, total {md_state_days} MD)</span>'
        elif same_state_days > 99:
            press_status_str += f'<br><span style="font-size: 12px;">(99+ days, total {md_state_days} MD)</span>'
        else:
            press_status_str += f'<br><span style="font-size: 12px;">({same_state_days} days, total {md_state_days} MD days)</span>'
    else:
        if same_state_days == 1:
            press_status_str += f'<br><span style="font-size: 12px;">(First day)</span>'
        elif same_state_days > 99:
            press_status_str += f'<br><span style="font-size: 12px;">(99+ days)</span>'
        else:
            press_status_str += f'<br><span style="font-size: 12px;">({same_state_days} days)</span>'
    general_info_data["Press Status"] = press_status_str

    from itertools import zip_longest
    highlights_html = ''
    for ((_, entry), teams_link) in zip_longest(highlight_entries, copied_links):
        point = entry.get()
        if point:  # Avoid adding empty bullet points
            if teams_link:  # Check if link exists for the highlight
                highlights_html += f'<li>{point} (<a href="{teams_link}" onclick="openTeams()"><img src="C:\\Users\\elazar\\OneDrive - HP Inc\\Documents\\Daily Report\\teams_logo.png" alt="Teams Logo"></a> Teams conversation)</li>'
            else:  # If no link exists, add highlight without link
                highlights_html += f'<li>{point}</li>'
    highlights_html = f'<h2 style="color:green;">Highlights</h2><ul>{highlights_html}</ul>' if highlights_html else ''

    # Reverse the order of issue_entries
    issue_entries.reverse()

    # Create HTML bullet list for issues
    issues_html = ''
    for issue_entry in issue_entries:
        frame, (case_entry, description_entry, update_entry) = issue_entry["frame"], issue_entry["entries"]
        day_counter, teams_link = issue_entry["day_counter"], issue_entry["teams_link"]

        if case_entry.winfo_exists() and description_entry.winfo_exists() and update_entry.winfo_exists():
            case = case_entry.get()
            description = description_entry.get()
            update = update_entry.get()
            if description or (case and update):  # Add issue if a description and/or a case number + update is entered
                case_part = f'<a href="http://example.com/{case or ""}" style="color:black;">{case}</a> - ' if case else ""
                description_part = f'{description}' + (' - ' if description and update else '') if description else ""
                update_part = f'<b>{update}</b>' if update else ""
                day_counter_part = f' - (opened yesterday)' if day_counter == 1 else f' - (open for <b>{day_counter}</b> days)' if day_counter != "new" else f' - (<b>{day_counter}</b>)'
                teams_link_part = f' (<a href="{teams_link}" onclick="openTeams()"><img src="C:\\Users\\elazar\\OneDrive - HP Inc\\Documents\\Daily Report\\teams_logo.png" alt="Teams Logo"></a> Teams conversation)' if teams_link else ""

                issues_html += f'<li>{case_part}{description_part}{update_part}{day_counter_part}{teams_link_part}</li>'
    issues_html = f'<h2 style="color:red;">Main Open Issues</h2><ul>{issues_html}</ul>' if issues_html else ''
    # Reverse the order of issue_entries
    issue_entries.reverse()

    # HTML body
    html = f"""
    <html>
    <body>
    <img src="src\\_ref_\\media\\V12.jpg" alt="Top image"><br>
    <h1 style="text-align:center; margin-bottom:0;">General Information</h1>
    {create_html_table(general_info_data)}<br>
    <h1 style="text-align:center;">Executive Summary</h1>
    {create_square_html()}<br>
    {highlights_html}<br>
    {issues_html}<br>
    <h1 style="text-align:center;">Production Data</h1><br>
    <table width="100%" border="0" cellspacing="0" cellpadding="0">
        <tr>
            <td colspan="2">
                <img src="cid:{image_ids[0]}"  width="100%">
            </td>
        </tr>
        <tr>
            <td width="60%">
                <img src="cid:{image_ids[1]}"  width="100%">
            </td>
            <td width="40%">
                <img src="cid:{image_ids[2]}"  width="100%">
            </td>
        </tr>
    </table>
    <h1 style="text-align:center;">Supportive pictures</h1><br>
    </body>
    </html>
    """
    mail.HTMLBody = html
    mail.Display(True)


# Create the main window
window = tk.Tk()

# Create the StringVar after the Tk instance
press_status_var = tk.StringVar()
shift_vars = [tk.StringVar() for _ in SHIFT_OPTIONS]

# Lists to hold all the highlight entries and issue entries
highlight_entries = []
issue_entries = []
copied_links = []

# Load the general info data
general_info_data = load_general_info_data()

# Get the stored shifts, if any
stored_shifts = general_info_data.get("Shift", [])

# Update shift_vars according to the stored shifts
for i, var in enumerate(shift_vars):
    if SHIFT_OPTIONS[i] in stored_shifts:
        var.set(SHIFT_OPTIONS[i])

# Create frames for each section
press_status_frame = tk.Frame(window)
shift_frame = tk.Frame(window)
checkbox_frame = tk.Frame(window)  # New frame for checkbox interface

# Create a common frame for these three elements
common_frame = tk.Frame(window)

# Create the "Press Status" part
press_status_label = tk.Label(common_frame, text="Press Status:")
press_status_label.grid(row=0, column=0, sticky="w")

press_status_combo = ttk.Combobox(common_frame, textvariable=press_status_var)
press_status_combo['values'] = [status[0] for status in PRESS_STATUS_OPTIONS]
press_status_combo.grid(row=0, column=1, sticky="we")

# Add a gap and vertical separator
tk.Label(common_frame, text="   ").grid(row=0, column=2)  # Empty label for gap
ttk.Separator(common_frame, orient='vertical').grid(row=0, column=3, sticky='ns', padx=5)  # Vertical separator

# Create the "Shift" part
shift_label = tk.Label(common_frame, text="Shift:")
shift_label.grid(row=0, column=4, sticky="w")  # Changed the column to 4

for i, shift in enumerate(SHIFT_OPTIONS):
    shift_checkbutton = tk.Checkbutton(common_frame, text=shift, variable=shift_vars[i], onvalue=shift, offvalue="")
    shift_checkbutton.grid(row=0, column=i + 5)  # Change the column to i+5

# Add a gap and vertical separator
tk.Label(common_frame, text="    ").grid(row=0, column=len(SHIFT_OPTIONS) + 5)  # Empty label for gap
ttk.Separator(common_frame, orient='vertical').grid(row=0, column=len(SHIFT_OPTIONS) + 6, sticky='ns',
                                                    padx=5)  # Vertical separator

# Add the "Edit FSE and Local Staff" part
edit_button = tk.Button(common_frame, text="Edit FSE and Local Staff", command=fse_data_gui)
edit_button.grid(row=0, column=len(SHIFT_OPTIONS) + 7, sticky="we",
                 padx=(20, 0))  # Change the column to len(SHIFT_OPTIONS)+7

# Create a horizontal separator
separator = ttk.Separator(common_frame, orient='horizontal')
separator.grid(row=1, column=0, columnspan=len(SHIFT_OPTIONS) + 8, sticky='ew', padx=5, pady=5)

# Now, place the common_frame in your window
common_frame.grid(row=0, column=0, sticky="we", padx=5, pady=5)

# Checkbox interface
checkbox_interface = launch_checkbox_interface(checkbox_frame)
checkbox_interface.pack()

# Place the frames and a separator on the window
press_status_frame.grid(row=0, column=0, sticky="we", padx=5, pady=5)
shift_frame.grid(row=1, column=0, sticky="we", padx=5, pady=5)  # Shift frame below the Press Status frame
checkbox_frame.grid(row=2, column=0, padx=5, pady=5)  # Checkbox frame below the Shift frame
tk.Frame(window, height=2, bd=1, relief=tk.SUNKEN).grid(row=3, column=0, sticky="we", padx=5, pady=5)  # separator

# Move "Highlights" elements to the highlights frame
highlight_label = tk.Label(window, text="Highlights:")
highlight_label.grid(row=5, column=0, sticky="w")

add_highlight_button = tk.Button(window, text="Add Highlight", command=add_highlight_entry)
add_highlight_button.grid(row=6, column=0, sticky="we")  # now set to row 4, just below the "Highlights" label

# Highlights frame grid placement
highlights_frame = tk.Frame(window)
highlights_frame.grid(row=7, column=0, sticky="we", padx=5, pady=5)  # Highlights frame below the separator

# Separator is defined here
separator = tk.Frame(window, height=2, bd=1, relief=tk.SUNKEN)
separator.grid(row=8, column=0, sticky="we", padx=5, pady=5)  # initial placement of separator

# Other elements
issue_label = tk.Label(window, text="Main Open Issues:")
issue_label.grid(row=9, column=0, sticky="w")

# Issues frame grid placement
issues_frame = tk.Frame(window)
issues_frame.grid(row=10, column=0, sticky="we", padx=5, pady=5)

add_issue_button = tk.Button(window, text="Add Issue", command=add_issue_entry)
add_issue_button.grid(row=11, column=0, sticky="we")  # now set to row 11, just below the issues_frame

event_handling_frame = EventHandlingFrame(window)
event_handling_frame.grid(row=12, column=0, sticky="we", padx=5, pady=5)

submit_button = tk.Button(window, text="Open in Outlook", command=open_outlook)
submit_button.grid(row=1001, column=0, sticky="we")  # large row index to always keep it at the bottom

# Add initial highlight and issue entry rows
add_highlight_entry()
display_issues()
add_issue_entry()

# Create the main Tkinter window
window.grid_columnconfigure(0, weight=1)

# Start the Tkinter event loop
window.mainloop()
