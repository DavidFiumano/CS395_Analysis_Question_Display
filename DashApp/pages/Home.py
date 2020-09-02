# DASH
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

# PLOTLY
import plotly.graph_objects as go
import plotly.express as px
import plotly

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
    },
    {
        'label' : 'Remove Outliers',
        'value' : 'outliers'
    }
]

layout = html.Div(
    [
        html.Div(
            [
                html.H1("Select Sensors to Graph"),
                dcc.Dropdown(id='days', multi=True, options=day_opts, value=[24, 29], searchable=True),
                dcc.Dropdown(id='node_dropdown', options=sensor_opts, value=sensor_opts[0]['value']),
                dcc.Dropdown(id='subsystem', disabled=True),
                dcc.Dropdown(id='sensor', disabled=True),
                dcc.Dropdown(id='parameter', disabled=True),
                dcc.Dropdown(id='process_data', multi=True, options=processing_opts, value=[], searchable=True, placeholder="Preprocessing Options")
            ],
            style={'width' : '49%', 'display' : 'inline-block', 'vertical-align' : 'middle'}
        ),
        html.Div(
            [
                html.H1("Sensor Graph"),
                dcc.Graph(id='sensor_graph', figure=px.scatter())
            ],
            style={'width' : '49%', 'display' : 'inline-block', 'vertical-align' : 'top'}
        )
    ]
)

current_subsystem = None
current_sensor = None

current_data = None

@app.callback(
    [
        Output('subsystem', 'options'),
        Output('subsystem', 'value'),
        Output('subsystem', 'disabled')
    ],
    [
        Input('node_dropdown', 'value')
    ]
)
def subsystem_selector_callback(current_node):
    opts = list()

    subsystem_data = filterByNodeId(AOT_DATA, current_node)
    subsystems = subsystem_data.subsystem.unique()

    for subsystem in subsystems:
        opts.append(
            {
                'label' : subsystem,
                'value' : subsystem
            }
        )

    return (opts, opts[0]['value'], False)

@app.callback(
    [
        Output('sensor', 'options'),
        Output('sensor', 'value'),
        Output('sensor', 'disabled')
    ],
    [
        Input('subsystem', 'value')
    ],
    [
        State('node_dropdown', 'value'),
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
        Output('parameter', 'options'),
        Output('parameter', 'value'),
        Output('parameter', 'disabled')
    ],
    [
        Input('sensor', 'value')
    ],
    [
        State('subsystem', 'value'),
        State('node_dropdown', 'value'),
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
    Output('sensor_graph', 'figure'),
    [
        Input('parameter', 'value'),
        Input('process_data', 'value'),
        Input('days', 'value')
    ],
    [
        State('sensor', 'value'),
        State('subsystem', 'value'),
        State('node_dropdown', 'value'),
        State('days', 'value')
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
        30 : 'pink'
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

    # create figure
    fig = go.Figure()

    # traces
    # make a trace for each day
    for day in days:
        day_data = filterByDay(graph_data, datetime(month=8, day=day, year=2020).date())

        times = day_data['time'].tolist()
         
        if 'moving_average' in processing_settings:
            # get data into usable format
            day_data_rolling = day_data['value_hrf'].rolling(10).mean()
            trace = go.Scattergl(
                x = times,
                y = day_data_rolling,
                name = dotw[day],
                showlegend=True,
                mode="lines",
                marker={
                    "color" : colors[day]
                }
            )
            fig.add_trace(trace)
        else:
            trace = go.Scattergl(
                x = times,
                y = day_data['value_hrf'].tolist(),
                name = dotw[day],
                showlegend=True,
                mode="markers",
                marker={
                    'color' : colors[day]
                }
            )
            fig.add_trace(trace)

    
    fig.update_layout(
        title_text=current_parameter + " Over Time",
        xaxis_title="Time (12:00 am to 11:59 pm)",
        yaxis_title=current_parameter
    )

    return fig

