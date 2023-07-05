import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from dateutil.parser import parse
import matplotlib.dates as mdates

# Define parameters
BAR_HEIGHT = 0.4
SUBSYSTEM_GAP = 0.6
LEFT_MARGIN = 0.25
RIGHT_MARGIN = 0.95

def plot_failure_data(df):
    
    # Filter rows where 'severity' is 'Failure' and create a copy of the resulting DataFrame
    df = df[df['severity'] == 'Failure'].copy()

    # Fill NA/NaN values in 'subSystem' column with 'DFE'
    df['subSystem'].fillna('DFE', inplace=True)

    # Convert 'time' column to datetime without a timezone
    df['time'] = df['time'].apply(lambda x: parse(x, ignoretz=True))

    # Replace underscores in 'subSystem' column
    df['subSystem'] = df['subSystem'].str.replace("_", " ")

    df['state'] = df['state'].replace('MECH_INIT', 'GET_STANDBY')

    #df['subSystem'] = df['subSystem'].apply(lambda x: ' '.join([word[0].upper() + word[1:] for word in x.split('_')]))

    # Create a new dataframe that counts the number of failures for each subsystem
    subSystem_counts = df['subSystem'].value_counts().reset_index().rename(columns={'index': 'subSystem', 'subSystem': 'counts'})

    # Sort the new dataframe by counts in descending order
    subSystem_counts.sort_values(by='counts', ascending=True, inplace=True)

    # Initialize bar position
    pos = 0

    # Define color dictionary
    color_dict = {'OFF': 'red', 'SERVICE': '#FFA500', 'STANDBY': '#EADA1B', 'GET_STANDBY': '#FFFF00', 
                  'GET_READY': 'lightgreen', 'DYNAMIC_READY': '#00FF00', 'READY': 'green', 'PRE_PRINT': '#2C82BA', 'PRINT': '#591AF5', 
                  'POST_PRINT': '#40B1DE'}

    # Create custom handles for the legend
    handles = [plt.Rectangle((0,0),1,1, color=color_dict[label]) for label in color_dict.keys()]
    
    max_error_count = 0  # Initialize maximum error count

    # Initialize lists to store x and y values for scatter plot and line plot
    scatter_x_all = []
    scatter_y_all = []

    # Loop through the sorted 'subSystem' values
    for system in subSystem_counts['subSystem']:
        # Filter the original DataFrame df by the current subsystem
        df_subsystem = df[df['subSystem'] == system]

        # Group by 'name' and 'state' and get the counts
        error_counts = df_subsystem.groupby('name')['state'].value_counts().unstack(fill_value=0)
        error_counts['total'] = error_counts.sum(axis=1)
        error_counts.sort_values(by='total', ascending=True, inplace=True)

        # Update maximum count
        max_count_system = error_counts['total'].max()  # Max count for the current system
        if max_count_system > max_error_count:
            max_error_count = max_count_system  # Update max_error_count if max_count_system is larger

        # Add subsystem as a bold title to the y-axis
        label_pos = pos + len(error_counts) * BAR_HEIGHT 
        ax.text(-0.1, label_pos, system, ha='right', va='center', color='black', weight='bold', fontsize=12)


        # Create a stacked bar for each error type in the subsystem
        for i, (error, row) in enumerate(error_counts.iterrows()):
            # Keep track of the end of the last bar
            last_bar_end = 0

            # Sort the states by their counts
            row_sorted = row.sort_values(ascending=False)           

            for state in row_sorted.index.drop('total'):  # Excluding 'total' column from plotting
                # Use the color from the color_dict if it exists, otherwise use 'red' as default
                color = color_dict.get(state, 'red')
                ax.barh(pos + i * BAR_HEIGHT, row_sorted[state], left=last_bar_end, height=BAR_HEIGHT, align='center', color=color, edgecolor='black')
                last_bar_end += row_sorted[state]

            # Add a dividing line between bars
            ax.hlines(y=pos + i * BAR_HEIGHT + BAR_HEIGHT/2, xmin=0, xmax=last_bar_end, colors='black', linewidth=0.5)

            # Add the name of the error to the left of the bar
            ax.text(-0.1, pos + i * BAR_HEIGHT, f'{error}', va='center', ha='right', color='black', fontsize=8)
            
            for _, failure in df_subsystem.iterrows():
                scatter_x = failure['time']
                scatter_y = pos + error_counts.index.get_loc(failure['name']) * BAR_HEIGHT
                scatter_x_all.append(scatter_x)
                scatter_y_all.append(scatter_y)

        # Add some extra space between subsystems
        pos += len(error_counts) * BAR_HEIGHT
        pos += SUBSYSTEM_GAP

    # Add 1 line extra after the max_count
    ax.set_xticks(range(max_error_count + 2), minor=True)  # +2 because range() excludes the stop value

    # Add grid lines on X-axis for all numbers
    ax.grid(which='minor', axis='x', color='gray', linestyle='--', linewidth=0.5, alpha=0.3)
    # Make every fifth line a little more bold
    ax.set_xticks(range(0, max_error_count + 2, 5))  # +2 because range() excludes the stop value
    ax.grid(which='major', axis='x', color='gray', linestyle='--', linewidth=1, alpha=0.5)

    # Increase the left and right margins of the plot to prevent bars from extending beyond the edges
    plt.subplots_adjust(left=LEFT_MARGIN, right=RIGHT_MARGIN)

    # Hide y-axis
    ax.get_yaxis().set_visible(False)

    # Create custom handles for the legend
    ax.legend(handles, color_dict.keys(), loc='lower right')

    # Create a secondary x-axis at the top of the graph for time
    ax2.plot(df['time'], np.zeros_like(df['time']), ' ', alpha=0.0)
    # Set the date format
    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m\n%H:%M'))

    # Set the limits of the y-axis to show all subsystems
    ax.set_ylim(-0.4, pos - SUBSYSTEM_GAP)

    # Set the limits of the x-axis according to the maximum count of errors.
    ax.set_xlim(0, max_error_count + 1)  # +1 for a little extra space
    ax2.set_xlim(df['time'].min() - pd.Timedelta(minutes=30), df['time'].max() + pd.Timedelta(minutes=30))

    # Sort the scatter plot and line plot data by time
    scatter_data = sorted(zip(scatter_x_all, scatter_y_all))

    scatter_x_sorted = [x for x, y in scatter_data]
    scatter_y_sorted = [y for x, y in scatter_data]

    # Perform scatter plot and line plot
    ax2.scatter(scatter_x_sorted, scatter_y_sorted, color='black', s=10)  # Adjust size (s) as needed
    ax2.plot(scatter_x_sorted, scatter_y_sorted, color='black', alpha=0.5)  # This line connects the scatter points in chronological order
    # Show the plot
    #plt.show()

# Load your data
df = pd.read_csv('DB/S6 - Failures 31-05-2023 17_02 - 1-06-2023 17_02.csv')

# Create a figure with size 12x8
fig, ax = plt.subplots(figsize=(12, 8))
ax2 = ax.twiny()

# Call the function with your DataFrame
plot_failure_data(df)

# Save the figure before showing it
fig.savefig("failure_graph.png")

# Now show the plot
#plt.show()




# Save the figure before showing it
#plt.savefig("failure_plot.png")

# Call the function with your DataFrame
#plot_failure_data(df)

# Now show the plot
#plt.show()  