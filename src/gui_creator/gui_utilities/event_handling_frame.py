import tkinter as tk
from tkinter import ttk
from datetime import datetime
import json


class EventHandlingFrame(ttk.Frame):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.topics = ["Operator duties", "Troubleshooting", "Mechanical issue", "Software issue"]
        self.times = [f'{str(i).zfill(2)}:{str(j).zfill(2)}' for i in range(24) for j in range(0, 60, 15)]
        self.data = self.load_data()
        self.today = datetime.now().strftime("%Y-%m-%d")
        self.events_today = self.get_today_events()
        self.row_counter = len(self.events_today)
        self.event_rows = []
        self.init_widgets()
        self.grid_columnconfigure(3, weight=1)

    def load_data(self):
        try:
            with open("data/main_events_archive.json", "r") as file:
                data = json.load(file)
        except FileNotFoundError:
            data = {"Main events": []}
        return data

    def get_today_events(self):
        for day_events in self.data["Main events"]:
            if day_events["date"] == self.today:
                return day_events["events"]
        # If no events for today were found, create a new entry
        self.data["Main events"].append({"date": self.today, "events": []})
        return []

    def save_data(self):
        events_today_rebuilt = [event_row.event for event_row in self.event_rows]
        existing_entry = [day_events for day_events in self.data["Main events"] if day_events["date"] == self.today]
        if existing_entry:
            self.data["Main events"].remove(existing_entry[0])
        if events_today_rebuilt:
            self.data["Main events"].append({"date": self.today, "events": events_today_rebuilt})
        with open("data/main_events_archive.json", "w") as file:
            json.dump(self.data, file, indent=4)

    class EventRow:
        def __init__(self, master, row, event=None, topics=None, times=None):
            if event is None:
                event = {'topic': '', 'start_time': '08:00', 'end_time': '08:00', 'description': ''}
            self.master = master
            self.row = row
            self.event = event
            self.widgets = []
            self.create_widgets(topics, times)

        def create_widgets(self, topics, times):
            topic_combo = ttk.Combobox(self.master, values=topics, state='readonly')
            topic_combo.set(self.event['topic'])
            topic_combo.grid(row=self.row, column=0, padx=5)
            self.widgets.append(topic_combo)

            start_time_combo = ttk.Combobox(self.master, values=times, state='readonly', width=5)
            start_time_combo.set(self.event['start_time'])
            start_time_combo.grid(row=self.row, column=1)
            self.widgets.append(start_time_combo)

            end_time_combo = ttk.Combobox(self.master, values=times, state='readonly', width=5)
            end_time_combo.set(self.event['end_time'])
            end_time_combo.grid(row=self.row, column=2)
            self.widgets.append(end_time_combo)

            description_entry = tk.Entry(self.master)
            description_entry.insert(0, self.event['description'])
            description_entry.grid(row=self.row, column=3, sticky='we', padx=5)
            self.widgets.append(description_entry)

            delete_button = tk.Button(self.master, text="Delete", command=self.delete)
            delete_button.grid(row=self.row, column=4, padx=5)
            self.widgets.append(delete_button)

            # Call update_event when the values change
            topic_combo.bind('<<ComboboxSelected>>', self.update_event)
            start_time_combo.bind('<<ComboboxSelected>>', self.update_event)
            end_time_combo.bind('<<ComboboxSelected>>', self.update_event)
            description_entry.bind('<KeyRelease>', self.update_event)

        def update_event(self, *args):
            self.event['topic'] = self.widgets[0].get()
            self.event['start_time'] = self.widgets[1].get()
            self.event['end_time'] = self.widgets[2].get()
            self.event['description'] = self.widgets[3].get()
            self.master.save_data()

        def delete(self):
            for widget in self.widgets:
                widget.grid_remove()
            self.master.event_rows.remove(self)
            self.master.events_today.remove(self.event)
            self.master.save_data()

    def add_event(self):
        event = {'topic': '', 'start_time': '08:00', 'end_time': '08:00', 'description': ''}
        self.events_today.append(event)
        self.row_counter += 1
        event_row = self.EventRow(self, self.row_counter, event, self.topics, self.times)
        self.event_rows.append(event_row)
        self.add_button_frame.grid(row=self.row_counter + 1, columnspan=5)

    def init_widgets(self):
        labels = ["Topic", "Start time", "End time", "Description", "Delete"]
        for i, label in enumerate(labels):
            tk.Label(self, text=label).grid(row=0, column=i, padx=5)
        self.add_button_frame = tk.Frame(self)
        add_button = tk.Button(self.add_button_frame, text="Add Event", command=self.add_event)
        add_button.pack()
        for i, event in enumerate(self.events_today):
            event_row = self.EventRow(self, i + 1, event, self.topics, self.times)
            self.event_rows.append(event_row)
        if len(self.event_rows) == 0:
            self.add_event()
        else:
            self.add_button_frame.grid(row=self.row_counter + 1, column=0, columnspan=5)
