import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from src.util.filesHandle import *


def visual_basic_graph(df):
    # Create subplots
    fig, axs = plt.subplots(2, figsize=(20, 6))

    # 'PressState'
    # Create a numeric representation of the states for the plotting
    press_state_mapping = {state: i for i, state in enumerate(df['PressState'].unique())}
    df['PressState_numeric'] = df['PressState'].map(press_state_mapping)
    axs[0].plot(df['time'], df['PressState_numeric'], drawstyle='steps-post', color='blue')
    axs[0].set_yticks(list(press_state_mapping.values()))
    axs[0].set_yticklabels(list(press_state_mapping.keys()))
    axs[0].set_title('Timeline of Press States')
    # Set the time resolution for the x-axis (PressState)
    axs[0].xaxis.set_major_locator(mdates.HourLocator())  # set the major ticks to be every Min
    axs[0].xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))  # set the format of the ticks to be 'Hour-Minute'
    axs[0].tick_params(axis='x', rotation=45)

    # 'MachineState'
    # Create a numeric representation of the states for the plotting
    machine_state_mapping = {state: i for i, state in enumerate(df['MachineState'].unique())}
    df['MachineState_numeric'] = df['MachineState'].map(machine_state_mapping)
    axs[1].plot(df['time'], df['MachineState_numeric'], drawstyle='steps-post', color='red')
    axs[1].set_yticks(list(machine_state_mapping.values()))
    axs[1].set_yticklabels(list(machine_state_mapping.keys()))
    axs[1].set_title('Timeline of Machine States')
    # Set the time resolution for the x-axis (MachineState)
    axs[1].xaxis.set_major_locator(mdates.HourLocator())  # set the major ticks to be every Min
    axs[1].xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))  # set the format of the ticks to be 'Hour-Minute'
    axs[1].tick_params(axis='x', rotation=45)

    # Adjust the space between the plots
    plt.tight_layout()
    plt.show()


def visual_interactive_graph(df):
    # TODO: create interactive graph
    # 'PressState'
    press_state_mapping = {state: i for i, state in enumerate(df['PressState'].unique())}
    df['PressState_numeric'] = df['PressState'].map(press_state_mapping)
    # 'MachineState'
    machine_state_mapping = {state: i for i, state in enumerate(df['MachineState'].unique())}
    df['MachineState_numeric'] = df['MachineState'].map(machine_state_mapping)

    # Create figure with secondary y-axis
    fig = make_subplots(rows=2, cols=1)

    fig.add_trace(
        go.Scatter(x=df['time'], y=df['PressState_numeric'], mode='lines', name='PressState'),
        row=1, col=1
    )

    fig.add_trace(
        go.Scatter(x=df['time'], y=df['MachineState_numeric'], mode='lines', name='MachineState'),
        row=2, col=1
    )

    # Update xaxis properties
    fig.update_xaxes(title_text="Time", row=1, col=1)
    fig.update_xaxes(title_text="Time", row=2, col=1)

    # Update yaxis properties
    fig.update_yaxes(title_text="PressState", row=1, col=1)
    fig.update_yaxes(title_text="MachineState", row=2, col=1)

    fig.update_layout(height=600, width=800, title_text="State over Time")

    fig.show()


def state_distribution_analysis():
    # Importing Data
    df = pd.read_csv(find_rel_path(file_name="../dataAnalysis/test_to_gcsteamcont.csv"))

    # Convert the 'time' column to datetime objects, convert to the desired timezone, and remove timezone information
    df['time'] = pd.to_datetime(df['PlcTime']).dt.tz_localize(None)
    df.sort_values('time').reset_index(drop=True)

    # Replace 'Print' with 'Pre / Post Print' if 'machineState' is 'PRE_PRINT' or 'POST_PRINT'
    df.loc[(df['MachineState'].isin(['PRE_PRINT', 'POST_PRINT'])) & (
            df['PressState'] == 'Print'), 'PressState'] = 'Pre / Post Print'

    visual_basic_graph(df)
