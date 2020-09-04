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
                    lat=41.839066, # this is chicago's GPS coordinates according to google maps
                    lon=-87.665685 
                ),
                "zoom" : 17 # set this to something reasonable for you and your computer. 
                # As long as we can see all the nodes and don't need to move or zoom into the graph too much to find them all, I am happy with whatever you set the 'zoom' value to
            },
        clickmode="event+select"
    )

layout = html.Div(
    [
        html.H2("Ashland Metro Station Map"),
        dcc.Graph(id="q2map", figure=scattermapbox),
        html.Div(
            [
                html.H2("Select Sensors to Graph"),
                dcc.Dropdown(id='q2days', multi=True, options=day_opts, value=[24, 30], searchable=True),
                dcc.Dropdown(id='q2node_dropdown', options=sensor_opts, value='001e06113acb'),
                dcc.Dropdown(id='q2subsystem', disabled=True),
                dcc.Dropdown(id='q2sensor', disabled=True),
                dcc.Dropdown(id='q2parameter', disabled=True),
                dcc.Dropdown(id='q2process_data', multi=True, options=processing_opts, value=[], searchable=True, placeholder="Preprocessing Options")
            ],
            style={'width' : '32%', 'display' : 'inline-block', 'vertical-align' : 'middle'}
        ),
        html.Div(
            [
                html.H2("Sensor Graph"),
                dcc.Graph(id='q2sensor_graph', figure=px.scatter())
            ],
            style={'width' : '67%', 'display' : 'inline-block', 'vertical-align' : 'top'}
        ),
        html.Div(
            [
                html.H1("Question 2"),
                "There is a Array of Things node placed at the Ashland Metro station. This is a station in the middle of the orange line.",
                " Question 2 concerns this node specifically. (see the map below)",
                html.Br(),
                "This metro schedule may be useful for answering some of the questions: https://www.transitchicago.com/assets/1/6/rail-tt_orange.pdf",
                "You will also need to find this location on google maps and use some of google's analytics to answer some of the questions.",
                html.Br(), html.Br(),
                html.H2("Part A"),
                "(1 pt) This node has two sensor subsystems on it, metsense and lightsense. Do both appear to be working properly? How do you know?",
                html.Br(), html.Br(),
                "The sound intensity sensor on the metsense subsystem is called spv1840lr5h_b (it's the only one that starts with spv, so it should be easy enough to find). However, the data it produces is not very clear.",
                " In order to resolve this, and make this data useful, data scientists will often use what is called a \"Moving Average\" to view general trends within the data.",
                " Moving averages are a very simple way to show general trends in the data where they may not otherwise be clear. In this case, the sensor doesn't have great resolution, so it produces these horizontal lines of data instead of something more useful.",
                " To fix this, we will take a look at the moving average of the data. This will allow us to see more clearly how noisy the area around the sensor is over the course of a day.",
                " To apply a moving average to your data, select the \"Moving Average\" from the bottom most dropdown menu.",
                html.Br(), html.Br(),
                "(1 pts) Enable the sound intensity sensor and select a moving average. Based on this information, when is this metro station the loudest?",
                html.Br(), html.Br(),
                "(1 pts) Compare Monday and Sunday for that week. Which day is louder and why might that be?",
                html.Br(), html.Br(),
                "(1 pts) Compare Monday and Saturday for that week. When is Saturday louder than Monday?", 
                html.Br(), html.Br(),
                "(6 pts) Using Google Maps traffic/popular times data and the metro schedule, briefly explain what trends most account for the noise on the subways system.",
                html.Br(), html.Br(),
                "(5 pts) How well correlated is the data from the sound sensor with the business/train activity of the area around it? Is the sensor data better correlated with train activity or the amount of people on the platform? Or is it not especially well correlated with either?",
                html.H2("Part C"),
                "The meteorlogical subsystem also has a 3-axis Accelerometer built-in (the sensor is called mma8452_q). It measures its acceleration in the x, y, and z directions. We can use this to measure vibration by seeing how much acceleration the sensor experiences in each direction over time.",
                
            ]
        )
    ]
)

current_subsystem = None
current_sensor = None

current_data = None

@app.callback(
    [
        Output('q2subsystem', 'options'),
        Output('q2subsystem', 'value'),
        Output('q2subsystem', 'disabled')
    ],
    [
        Input('q2node_dropdown', 'value')
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
        Output('q2sensor', 'options'),
        Output('q2sensor', 'value'),
        Output('q2sensor', 'disabled')
    ],
    [
        Input('q2subsystem', 'value')
    ],
    [
        State('q2node_dropdown', 'value'),
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
        Output('q2parameter', 'options'),
        Output('q2parameter', 'value'),
        Output('q2parameter', 'disabled')
    ],
    [
        Input('q2sensor', 'value')
    ],
    [
        State('q2subsystem', 'value'),
        State('q2node_dropdown', 'value'),
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
    Output('q2sensor_graph', 'figure'),
    [
        Input('q2parameter', 'value'),
        Input('q2process_data', 'value'),
        Input('q2days', 'value')
    ],
    [
        State('q2sensor', 'value'),
        State('q2subsystem', 'value'),
        State('q2node_dropdown', 'value'),
        State('q2days', 'value')
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

@app.callback(
    Output('q2node_dropdown', 'value'),
    [
        Input('q2map', 'clickData')
    ]
)
def click_selector(clickData):
    return clickData['points'][0]['customdata'][0]