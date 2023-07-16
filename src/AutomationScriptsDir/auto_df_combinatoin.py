import os
import time

import pandas as pd
import re

from config_manager import *


def func_compare_csv_files(file1, file2, field):
    # Load the data from the csv files
    df1 = pd.read_csv(file1)
    df2 = pd.read_csv(file2)

    # Create a new column in df1 that is marked with a "1" if the row (based on the field) is not present in df2
    df1['diff'] = df1[field].isin(df2[field]).map({True: 0, False: 1})

    # Save the modified df1 to a new csv file named 'diff.csv'
    df1.to_csv('diff.csv', index=False)

    return df1


def func_collect_and_combine_csv_files(directory):
    # List all .csv files in the directory
    all_files = [f for f in os.listdir(directory) if f.endswith('.csv') and fjp()['azure']['combineSeperator'] not in f]

    # Prepare a regular expression pattern to extract the index name, time period, and number extension
    pattern = re.compile(
        r"(?P<prefix>.*?)___SN___(?P<index_name>.*?)__From_(?P<from_time>.*?)_To_(?P<to_time>.*?)(?P<number_ext>\.\d*)?\.csv")

    # Initialize an empty dictionary to hold the dataframes
    dfs = {}

    # Iterate over each file
    for filename in all_files:
        match = pattern.match(filename)
        # If the filename matches the pattern
        if match:
            df = pd.read_csv(os.path.join(directory, filename))

            # Add columns for the index name, time period, and number extension
            index_name = match.group('index_name')
            from_time = match.group('from_time')
            to_time = match.group('to_time')
            number_ext = int(match.group('number_ext').replace('.', '')) if match.group('number_ext') else 0

            df['index_name'] = index_name
            df['from_time'] = from_time
            df['to_time'] = to_time
            df['number_ext'] = number_ext

            # Add the dataframe to the dictionary
            if index_name not in dfs:
                dfs[index_name] = {
                    'df_list': [],
                    'prefix': match.group('prefix'),
                    'from_time': from_time,
                    'to_time': to_time,
                }
            dfs[index_name]['df_list'].append(df)

    # Iterate over each index
    for index_name, data in dfs.items():
        df_list = data['df_list']
        prefix = data['prefix']
        from_time = data['from_time']
        to_time = data['to_time']

        # Combine all the DataFrames for this index into one
        combined_df = pd.concat(df_list, ignore_index=True)

        # Sort by time
        combined_df.sort_values('Time', inplace=True)

        # Drop duplicates, ignoring the 'number_ext' column
        columns_to_consider = [col for col in combined_df.columns if col != 'number_ext']
        combined_df.drop_duplicates(subset=columns_to_consider, inplace=True)

        # low-case columns name
        combined_df.columns = combined_df.columns.str.lower()

        # Construct output filename from index name and dates
        output_filename = f"{prefix}{fjp()['azure']['prssSNSeparator']}{index_name}_{from_time}_To_{to_time}{fjp()['azure']['combineSeperator']}.csv"
        output_filename = output_filename.replace(":", "-").replace(" ", "_")  # Clean up filename

        # Save combined DataFrame to .csv file
        combined_df.to_csv(os.path.join(directory, output_filename), index=False)

    # Remove original files
    for filename in all_files:
        os.remove(os.path.join(directory, filename))
    time.sleep(2)

    all_comb_files = [f for f in os.listdir(directory) if
                      f.endswith('.csv') and fjp()['azure']['combineSeperator'] in f]

    # Rename_files
    for f in all_comb_files:
        new_filename = f.replace(f"{fjp()['azure']['combineSeperator']}", "")  # Clean up filename
        # Rename the file
        old_filepath = os.path.join(directory, f)
        new_filepath = os.path.join(directory, new_filename)
        os.rename(old_filepath, new_filepath)
