import pandas as pd
from datetime import datetime

# filters the data frame so that it only includes data on a specific day
def filterByDay(df : pd.DataFrame, day : datetime.date):
    day_filter = df['date'] == day
    days_data = df[day_filter]
    return days_data

# filters the data frame so that it only includes data in the range of start_time to end_time (inclusive)
def filterByTime(df : pd.DataFrame, start_time : datetime.time, end_time : datetime.time):
    filter_start_time = df['time'] >= start_time
    filter_end_time = df['time'] <= end_time
    filter_time = filter_start_time & filter_end_time
    time_df = df[filter_time]
    return time_df

# filters the data frame so that it only includes data in a specific range of dates (incl.)
def filterByDateRange(df : pd.DataFrame, start : datetime, end : datetime):
    start_day = start.date()
    end_day = end.date()
    
    filter_start_date = df['date'] >= start_day
    filter_end_date = df['date'] <= end_day

    filter_date = filter_start_date & filter_end_date

    return df[filter_date]

# filter the data by node id
def filterByNodeId(df : pd.DataFrame, node_id : str):
    filter_node_id = df['node_id'] == node_id
    node_df = df[filter_node_id]
    return node_df

# filter the data by sensor path
def filterBySensorPath(df : pd.DataFrame, subsystem : str = None, sensor : str = None, parameter : str = None):
    if subsystem == sensor == parameter == None:
        return df

    filters = list()
    if subsystem != None:
        filters.append(df['subsystem'] == subsystem)
    
    if sensor != None:
        filters.append(df['sensor'] == sensor)
    
    if parameter != None:
        filters.append(df['parameter'] == parameter)

    combined_filter = None
    filter_set = False
    for f in filters:
        if not filter_set:
            combined_filter = f
            filter_set = True
        else:
            combined_filter = combined_filter & f

    return df[combined_filter]