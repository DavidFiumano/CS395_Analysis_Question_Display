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
from . import color_map

AOT_DATA = getData()

# AOT_DATA = filterBySensorPath(AOT_DATA, subsystem='lightsense') # metsense data ONLY

node_ids = AOT_DATA.node_id.unique()

# generate the dropdown list for the list of sensors
sensor_opts = list()

for node_id in node_ids:
    opt = dict()
    opt['label'] = node_id
    opt['value'] = node_id
    sensor_opts.append(opt)

day_opts = [
    {
        'label' : 'Monday',
        'value' : 24
    },
    {
        'label' : 'Tuesday',
        'value' : 25
    },
    {
        'label' : 'Wednesday',
        'value' : 26
    },
    {
        'label' : 'Thursday',
        'value' : 27
    },
    {
        'label' : 'Friday',
        'value' : 28
    },
    {
        'label' : 'Saturday',
        'value' : 29
    },
    {
        'label' : 'Sunday',
        'value' : 30
    },
]

processing_opts = [
    {
        'label' : 'Moving Average',
        'value' : 'moving_average'
    }
]

lats = list()
lons = list()
names = list()
subsystems_reporting = list()
sizes = list()
addresses = list()
colors = list()
for node in node_ids:

    node_data = filterByNodeId(AOT_DATA, node)
    node_datum = node_data.head(1)

    lat = 0
    lon = 0

    lat = node_datum['latitude'].tolist()[0]
    lon = node_datum['longitude'].tolist()[0]
    name = node_datum['node_id'].tolist()[0]
    address = node_datum['address'].tolist()[0]

    subsystems = node_data.subsystem.unique()
    subsystems_reporting.append(str(subsystems))
    sizes.append(len(subsystems)*10 + 10)

    lats.append(lat)
    lons.append(lon)
    names.append(name)
    addresses.append(address)

    if name in color_map:
        colors.append(color_map[name])
    else:
        colors.append('blue')

scattermapbox = go.Figure(
    go.Scattermapbox(
        name="All Node Map",
        mode="markers",
        lat=lats,
        lon=lons,
        text=names,
        customdata=np.stack([names, subsystems_reporting, addresses], axis=-1),
        hovertemplate="Node %{customdata[0]}<br>" +
                      "Location: (%{lat}, %{lon})<br>" +
                      "Subsystems Reporting: %{customdata[1]}<br>" +
                      "Address: %{customdata[2]}",
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
                    lat=41.692703,
                    lon=-87.62102 
                ),
                "zoom" : 18 # set this to something reasonable for you and your computer. 
                # As long as we can see all the nodes and don't need to move or zoom into the graph too much to find them all, I am happy with whatever you set the 'zoom' value to
            }
    )

layout = html.Div(
    [
        html.H1("Question 3"),
        html.H2("Plantower Sensor Map"),
        dcc.Graph(id="q3map", figure=scattermapbox),
        html.Div(
            [
                html.H2("Select Sensors to Graph"),
                dcc.Dropdown(id='q3days', multi=True, options=day_opts, value=[24, 30], searchable=True),
                dcc.Dropdown(id='q3node_dropdown', options=sensor_opts, value='001e061183f5'),
                dcc.Dropdown(id='q3subsystem', disabled=True),
                dcc.Dropdown(id='q3sensor', disabled=True),
                dcc.Dropdown(id='q3parameter', disabled=True),
                dcc.Dropdown(id='q3process_data', multi=True, options=processing_opts, value=[], searchable=True, placeholder="Preprocessing Options")
            ],
            style={'width' : '32%', 'display' : 'inline-block', 'vertical-align' : 'middle'}
        ),
        html.Div(
            [
                html.H2("Sensor Graph"),
                dcc.Graph(id='q3sensor_graph', figure=px.scatter())
            ],
            style={'width' : '67%', 'display' : 'inline-block', 'vertical-align' : 'top'}
        ),
        html.Div(
            [
                html.H2("Part A"),
                "Cars produce a lot of tiny particles of soot and other pollution when their engine is on. Generally, this matter collects in the air when cars drive by and slowly dissappates when the cars go away. We can observe this using AoT nodes with plantower sensors onboard.",
                "Note: All questions in Q3 concern the blue node (001e061183f5) specifically. It is located at the intersection of East 111th street and South Michigan Avenue.",
                html.Br(), html.Br(),
                "(5 pts) Which day has (generally) the lowest 1 um particle pollution? Why might this be? Back this data up with traffic data from Google Maps.",
                html.Br(), html.Br(),
                "(15 pts) On Sunday morning, there is a small spike in 1 um particle matter in the air from 12-1 pm. This is true almost every Sunday. Where might people be moving to/from to cause this pollution? Cite any addtional information you use.",
                html.Br(), "Hint: Look at this on Google Maps. What buildings would have the most people Sunday mornings? Where might those people go at around 12 pm?"
            ]
        )
    ]
)

current_subsystem = None
current_sensor = None

current_data = None

@app.callback(
    [
        Output('q3subsystem', 'options'),
        Output('q3subsystem', 'value'),
        Output('q3subsystem', 'disabled')
    ],
    [
        Input('q3node_dropdown', 'value')
    ]
)
def subsystem_selector_callback(current_node):
    opts = list()

    subsystem_data = filterByNodeId(AOT_DATA, current_node)
    subsystems = subsystem_data.subsystem.unique()
    if len(subsystems) == 0:
        raise dash.exceptions.PreventUpdate("Could not update subsystems, since there are not any.")

    for subsystem in subsystems:
        opts.append(
            {
                'label' : subsystem,
                'value' : subsystem
            }
        )

    return (opts, opts[-1]['value'], False)

@app.callback(
    [
        Output('q3sensor', 'options'),
        Output('q3sensor', 'value'),
        Output('q3sensor', 'disabled')
    ],
    [
        Input('q3subsystem', 'value')
    ],
    [
        State('q3node_dropdown', 'value'),
    ]
)
def sensor_selector_callback(current_subsystem, current_node):
    opts = list()

    node_data = filterByNodeId(AOT_DATA, current_node)
    sensor_data = filterBySensorPath(
                                        node_data, 
                                        subsystem = current_subsystem
                                    )
    
    sensors = sensor_data.sensor.unique()

    for sensor in sensors:
        opts.append(
            {
                'label' : sensor,
                'value' : sensor
            }
        )

    return (opts, opts[0]['value'], False)

@app.callback(
    [
        Output('q3parameter', 'options'),
        Output('q3parameter', 'value'),
        Output('q3parameter', 'disabled')
    ],
    [
        Input('q3sensor', 'value')
    ],
    [
        State('q3subsystem', 'value'),
        State('q3node_dropdown', 'value'),
    ]
)
def sensor_selector_callback(current_sensor, current_subsystem, current_node):
    opts = list()

    node_data = filterByNodeId(AOT_DATA, current_node)
    parameter_data = filterBySensorPath(
                                            node_data, 
                                            subsystem = current_subsystem,
                                            sensor = current_sensor
                                       )
    parameters = parameter_data.parameter.unique()

    for parameter in parameters:
        opts.append(
            {
                'label' : parameter,
                'value' : parameter
            }
        )

    return (opts, opts[0]['value'], False)

@app.callback(
    Output('q3sensor_graph', 'figure'),
    [
        Input('q3parameter', 'value'),
        Input('q3process_data', 'value'),
        Input('q3days', 'value')
    ],
    [
        State('q3sensor', 'value'),
        State('q3subsystem', 'value'),
        State('q3node_dropdown', 'value'),
        State('q3days', 'value')
    ]
)
def update_graph(current_parameter, processing_settings, day, current_sensor, current_subsystem, current_node, days):

    if current_parameter == None:
        raise dash.exceptions.PreventUpdate()

    data = filterByNodeId(AOT_DATA, current_node)
    graph_data = filterBySensorPath(data, 
                                    subsystem = current_subsystem,
                                    sensor = current_sensor,
                                    parameter = current_parameter)
    
    # generate x_axis
    x_axis = range(0, 1440) # minutes in a day

    # get data
    days = set(days) # prevent duplicate values from breaking stuff

    # colors
    colors = {
        24 : 'red',
        25 : 'green',
        26 : 'blue',
        27 : 'purple',
        28 : 'yellow',
        29 : 'orange',
        30 : 'black'
    }

    # day of the week
    dotw = {
        24 : 'Monday',
        25 : 'Tuesday',
        26 : 'Wednesday',
        27 : 'Thursday',
        28 : 'Friday',
        29 : 'Saturday',
        30 : 'Sunday'
    }

    n_cols = 2

    # create figure
    fig = make_subplots(1, n_cols)
    col = 0
    # traces
    # make a trace for each day
    for day in days:
        current_dotw = dotw[day]
        day_data = filterByDay(graph_data, datetime(month=8, day=day, year=2020).date())

        times = day_data['time'].tolist()

        col += 1

        if 'moving_average' in processing_settings:
            # get data into usable format
            day_data_rolling = day_data['value_hrf'].rolling(10).mean()
            trace = go.Scattergl(
                x = times,
                x0 = time(hour=0, minute=0, second=0),
                #dx = time(minute = 1),
                y = day_data_rolling,
                name = current_dotw,
                showlegend=True,
                mode="lines",
                marker={
                    "color" : colors[day]
                }
            )
            fig.add_trace(trace, row = 1, col = col)
        else:
            trace = go.Scattergl(
                x = times,
                x0 = time(hour=0, minute=0, second=0),
                #dx = time(minute = 1),
                y = day_data['value_hrf'].tolist(),
                name = current_dotw,
                showlegend=True,
                mode="markers",
                marker={
                    'color' : colors[day]
                }
            )
            fig.add_trace(trace, row = 1, col = col)

        if col == n_cols:
            break

    
    fig.update_layout(
        title_text=current_parameter + " Over Time",
        xaxis_title="Time (12:00 am to 11:59 pm)",
        yaxis_title=current_parameter
    )

    return fig
