from config_manager import *
import datetime
import sqlite3
import pandas as pd
import os


def auto_sql_handling_system(sub_path):
    # Create the directory if it doesn't already exist
    paths = [fjp()['paths']['sqldbPath_csv'],
             fjp()['paths']['sqldbPath'],
             fjp()['paths']['databaseName'],
             fjp()["paths"]["PushExpDataPathRel"],
             fjp(jsname='log.json')["current_press"],
             fjp()["paths"]["PullExpDataPathRel"]
             ]

    output_dir = f"{paths[5]}/{paths[4]}/{sub_path}/{paths[1]}"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    source_dir = f"{paths[5]}/{paths[4]}/{sub_path}"
    if not os.path.exists(source_dir):
        os.makedirs(source_dir)

    # Assumption Only one file
    db_files = [file for file in os.listdir(source_dir) if file.endswith(".db")]

    # Connect to the SQLite database
    conn = sqlite3.connect(f"{source_dir}/{db_files[0]}")

    # Get a cursor object
    c = conn.cursor()

    # Get a list of all tables
    c.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = c.fetchall()

    # For each table, load data into a DataFrame and export to a CSV file
    for table_name in tables:
        table_name = table_name[0]
        df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
        df.to_csv(f'{output_dir}/{table_name}.csv', index=False)

    # Close the connection
    conn.close()
