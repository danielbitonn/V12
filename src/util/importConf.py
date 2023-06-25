import json


def load_config():
    # Open the JSON file and load the data
    with open('src/util/conf.json') as file:
        data = json.load(file)

    # Access the azure variables
    azure_config = data['azure']
    # Access the indexes variables
    indexes_config = data['indexes']

    # Return the variables as a dictionary
    return {
        'azure_config': azure_config,
        'indexes_config': indexes_config,
    }
