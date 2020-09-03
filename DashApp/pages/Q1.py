# PANDAS AND NUMPY
import pandas as pd
import numpy as np

# DASH
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

# PLOTLY
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

# DATETIME
from datetime import datetime, date, time

# CUSTOM CODE
import os.path as path 
import sys

PROJECT_ROOT = path.dirname(path.dirname(path.dirname(path.abspath(__file__))))

if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from data_parser import getData
from data_filters import *
from DashApp.app import app

AOT_DATA = getData()

node_ids = AOT_DATA.node_id.unique()

color_map = {
    '001e061184a3' : 'red',
    '001e0610ee36' : 'green',
    '001e0610fb4c' : 'purple',
    '001e0611462f' : 'yellow',
    '001e061183bf' : 'orange',
    '001e06113acb' : 'black',
    '001e0610f703' : 'pink',
    '001e0610f05c' : 'gray',
    '001e06113107' : 'darkred',
    '001e061183f5' : 'blue'
}

lats = list()
lons = list()
names = list()
subsystems_reporting = list()
sizes = list()
colors = list()
addresses = list()
descriptions = list()
for node in node_ids:

    node_data = filterByNodeId(AOT_DATA, node)
    node_datum = node_data.head(1)

    lat = 0
    lon = 0

    lat = node_datum['latitude'].tolist()[0]
    lon = node_datum['longitude'].tolist()[0]
    name = node_datum['node_id'].tolist()[0]
    address = node_datum['address'].tolist()[0]
    description = node_datum['description'].tolist()[0]

    subsystems = node_data.subsystem.unique()
    subsystems_reporting.append(str(subsystems))
    sizes.append(len(subsystems)*5 + 10)

    lats.append(lat)
    lons.append(lon)
    names.append(name)
    addresses.append(address)
    descriptions.append(description)

    if name in color_map.keys():
        colors.append(color_map[name])
    else:
        colors.append('blue')

scattermapbox = go.Figure(
    go.Scattermapbox(
        name="Node Date Map",
        mode="markers",
        lat=lats,
        lon=lons,
        text=names,
        customdata=np.stack([names, subsystems_reporting, addresses, descriptions], axis=-1),
        hovertemplate="Node %{customdata[0]}<br>" +
                      "Location: (%{lat}, %{lon})<br>" +
                      "Subsystems: %{customdata[1]}<br>" +
                      "Address: %{customdata[2]}<br>" +
                      "Description: %{customdata[3]}",
        marker = {
            'size' : sizes,
            'color' : colors
        },
    )
)

scattermapbox.update_layout(
        mapbox_style="open-street-map", # this is absolutely required - open-street-map is easy to use, the other styles require an api key and have annoying limitations 
        margin={"r":0,"t":0,"l":0,"b":0}, # This is optional, but specifies the margins of the map in the page
        mapbox= # If you do not include this (centering and zooming on your map), you will lose points. Please include it so we don't have to zoom in a ton to grade your stuff
            {
                "center" : go.layout.mapbox.Center(
                    lat=41.8781, # this is chicago's GPS coordinates according to google maps
                    lon=-87.6298
                ),
                "zoom" : 9 # set this to something reasonable for you and your computer. 
                # As long as we can see all the nodes and don't need to move or zoom into the graph too much to find them all, I am happy with whatever you set the 'zoom' value to
            }
    )

# layout
layout = html.Div(
    [
        html.H1("Question 1"),
        html.H2("Part A:"),
        "Not all of these nodes were on for all of the week. Some were only turned on at the end. See the following map:", html.Br(), html.Br(),
        "Use the date range picker below the map to see what nodes reported between what date ranges.",
        dcc.Graph(id='graph1', figure=scattermapbox),
        dcc.DatePickerRange(id='date_picker', 
                            min_date_allowed=datetime(2020, 8, 24), 
                            max_date_allowed=datetime(2020, 8, 31), 
                            initial_visible_month=datetime(2020, 8, 24),
                            first_day_of_week=1
                           ),
        html.H3("Answer the following questions on blackboard for Q1 Part A:"),
        "(1 pt) What day was node 001e061184a3 (the lighter red one) activated during the week?", html.Br(), html.Br(),
        "(1 pt) What about node 001e0610ee36 (the green one)?", html.Br(), html.Br(),
        "(1 pt) What day was node 001e0610fb4c (the purple one) turned on?", html.Br(), html.Br(),
        html.H2("Part B:"),
        "Knowing when these nodes turned on/off can let you figure out what information nodes can help you find. On blackboard answer the following: ", html.Br(), html.Br(),
        "(2 pts) Node 001e610fb4c (the purple one) had a Honeywell HIH-4030 % Humidity sensor onboard. If, for some reason, we had reason to believe that the humidity in that area was going to be higher that at other nodes on Thursday (8/27) that week, could we observe this in the data available?",
        html.Br(), html.Br(),
        "Some sensor subsystems are more useful for answering some questions about the environment than others. For example, the chemsense subsystem can be used to learn information about the chemicals in the air around the sensors.",
        html.Br(), html.Br(),
        "Knowing this, we can combine the information on this page with the visualizations on the home page to answer the following questions:", html.Br(), html.Br(),
        "(3 pts) Say that there was an accident at the Stockyards Industrial Corridor (zoom in near the yellow node to see this location) on the morning of the 29th and the wind was blowing south to north that day. We might want to track the spread of smoke from accident to assess the impact of the accident on public health.",
        "Which nodes might be able to help us assess the effect of the disaster on air quality (just say the colors of the nodes, no need to worry about the node name)?",
        html.Br(),
        "Hint: However over the nodes to see which nodes have what sensors. The sensor subsystems that might help with this are: chemsense (detect chemicals in the smoke), plantower (detect the smoke particles) and lightsense (detect the how much the smoke obscures sunlight).",
        html.Br(), html.Br()
    ]
)

@app.callback(
    Output('graph1', 'figure'),
    [
        Input('date_picker', 'start_date'),
        Input('date_picker', 'end_date')
    ]
)
def date_filterer(start_date, end_date):
    if start_date == None or end_date == None:
        raise dash.exceptions.PreventUpdate()
    
    start_datetime = datetime.strptime(start_date, "%Y-%m-%d")
    end_datetime = datetime.strptime(end_date, "%Y-%m-%d")
    data = filterByDateRange(AOT_DATA, start_datetime, end_datetime)

    global node_ids

    lats = list()
    lons = list()
    names = list()
    subsystems_reporting = list()
    sizes = list()
    colors = list()
    for node in node_ids:

        node_data = filterByNodeId(data, node)
        node_datum = node_data.head(1)

        lat = 0
        lon = 0
        try:
            lat = node_datum['latitude'].tolist()[0]
            lon = node_datum['longitude'].tolist()[0]
            name = node_datum['node_id'].tolist()[0]
        except:
            continue

        subsystems = node_data.subsystem.unique()
        subsystems_reporting.append(str(subsystems))
        sizes.append(len(subsystems)*5 + 10)

        lats.append(lat)
        lons.append(lon)
        names.append(name)

        global color_map

        if name in color_map.keys():
            colors.append(color_map[name])
        else:
            colors.append('blue')

    scattermapbox = go.Figure(
        go.Scattermapbox(
            name="Node Date Map",
            mode="markers",
            lat=lats,
            lon=lons,
            text=names,
            customdata=np.stack([names, subsystems_reporting], axis=-1),
            hovertemplate="Node %{customdata[0]}<br>" +
                          "Location: (%{lat}, %{lon})<br>" +
                          "Subsystems: %{customdata[1]}",
            marker = {
                'size' : sizes,
                'color' : colors
            },
        )
    )

    scattermapbox.update_layout(
            mapbox_style="open-street-map", # this is absolutely required - open-street-map is easy to use, the other styles require an api key and have annoying limitations 
            margin={"r":0,"t":0,"l":0,"b":0}, # This is optional, but specifies the margins of the map in the page
            mapbox= # If you do not include this (centering and zooming on your map), you will lose points. Please include it so we don't have to zoom in a ton to grade your stuff
                {
                    "center" : go.layout.mapbox.Center(
                        lat=41.8781, # this is chicago's GPS coordinates according to google maps
                        lon=-87.6298
                    ),
                    "zoom" : 9 # set this to something reasonable for you and your computer. 
                    # As long as we can see all the nodes and don't need to move or zoom into the graph too much to find them all, I am happy with whatever you set the 'zoom' value to
                }
    )

    return scattermapbox