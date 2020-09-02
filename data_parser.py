import pandas as pd
import os.path as path
from datetime import datetime, timedelta
from typing import List
from aot_api.AOTNode import Measurement

AOT_DATA = None # cache the data in memory so readEverything() is only slow once
AOT_DATA_CACHED = False # bool (whether or not data is cached or not)

# read in the data
def readData(filepath : str) -> pd.DataFrame:
    print("Reading in measurements...")
    df = pd.read_csv(filepath, parse_dates=["timestamp"])
    print("Read in all measurements!")
    return df

# read in the list of nodes
def readNodes(filepath : str) -> pd.DataFrame:
    print("Reading in node metadata...")
    df = pd.read_csv(filepath, parse_dates=["start_timestamp", "end_timestamp"], index_col='node_id')
    return df

# reads in the data, reads in the nodes, returns a combined dataframe associates each measurement with a latitude, longitude, street address and description
def getData(processed_data_path : str = 'data/preprocessed_data.hdf5', data_path : str = 'data/data.csv', node_path : str = 'data/nodes.csv'):

    global AOT_DATA, AOT_DATA_CACHED
    if AOT_DATA_CACHED:
        return AOT_DATA.copy()
    elif path.exists(processed_data_path):
        print("Reading cached preprocessed data...")
        df = pd.read_hdf(processed_data_path, key='df')
        AOT_DATA = df
        AOT_DATA_CACHED = True
        return AOT_DATA
    else:
        data = readData(data_path)
        nodes = readNodes(node_path)

        # make empty dataframe
        df = dict()

        df['date'] = []
        df['time'] = []
        df['description'] = []
        df['node_id'] = []
        df['latitude'] = []
        df['longitude'] = []
        df['address'] = []
        df['subsystem'] = []
        df['sensor'] = []
        df['parameter'] = []
        df['value_hrf'] = []

        print("Converting measurements to a dictionary...")
        measurements = data.to_dict('index')

        print("Converting node data to a dictionary...")
        nodes_dict = nodes.to_dict('index')

        print("Collecting new dataframe...")
        for m in measurements:
            measurement = measurements[m]
            node_id = measurement['node_id']
            # store the node id
            df['node_id'].append(node_id)

            # store the timestamp
            dt = measurement['timestamp']
            time = dt.time()
            date = dt.date()
            df['date'].append(date)
            df['time'].append(time)
            
            # attach node metadata
            df['description'].append(nodes_dict[node_id]['description'])
            df['address'].append(nodes_dict[node_id]['address'])
            df['latitude'].append(nodes_dict[node_id]['lat'])
            df['longitude'].append(nodes_dict[node_id]['lon'])

            # attach measurement data
            df['subsystem'].append(measurement['subsystem'])
            df['sensor'].append(measurement['sensor'])
            df['parameter'].append(measurement['parameter'])
            df['value_hrf'].append(measurement['value_hrf'])
        
        print("Generating new dataframe...")
        df = pd.DataFrame.from_dict(df)
        print("Writing new dataframe to cache location...")
        df.to_hdf(processed_data_path, key='df')
        AOT_DATA = df
        AOT_DATA_CACHED = True
        return AOT_DATA