# the purpose of this file is to serve as the "home page" for the app.
# There is a drop-down menu which allows users to select the graph 
# Each graph's callback functions are defined in the student files

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

import plotly.graph_objects as go

from .app import app

import os, sys

STUDENT_CODE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

if STUDENT_CODE_PATH not in sys.path:
    sys.path.append(STUDENT_CODE_PATH)

from student import createParticulateGraph, createGasGraph, createWeatherGraph, allNodesGraph

dropdown_opts = [
    {
        'label' : 'Gas Sensors',
        'value' : 'Gas_Graph'
    },
    {
        'label' : 'Particle Sensors',
        'value' : 'Particle_Graph'
    },
    {
        'label' : 'Weather Sensors',
        'value' : 'Weather_Graph'
    },
    {
        'label' : 'All Nodes',
        'value' : 'All_Nodes_Graph'
    }
]

app.layout = html.Div(
    children=[
                html.H1("CS 395 Project 0"),
                dcc.Dropdown(id='graph_selector', options=dropdown_opts, value='All_Nodes_Graph'),
                html.Button('Take an Interactive Snapshot', id='graph_snapshot_button', n_clicks=0),
                html.H3(id='snapshot_text'),
                dcc.Graph(id='student_graph')
            ]
)

@app.callback(
    Output('student_graph', 'figure'),
    [
        Input('graph_selector', 'value')
    ]
)
def create_app_callback(value):
    if value == None:
        return createWeatherGraph()
    elif value == 'Weather_Graph':
        return createWeatherGraph()
    elif value == 'Gas_Graph':
        return createGasGraph()
    elif value == 'Particle_Graph':
        return createParticulateGraph()
    elif value == "All_Nodes_Graph":
        return allNodesGraph()
    else:
        print('For some reason, the graph selector was set to an unknown value: ' + str(value) + '\nDefaulting to Weather graph.')
        return createWeatherGraph()

@app.callback(
    Output('snapshot_text', 'children'),
    [
        Input('graph_snapshot_button', 'n_clicks')
    ],
    [
        State('student_graph', 'figure')
    ]
)
def take_graph_snapshot(n_clicks, figure):
    if n_clicks == None or n_clicks == 0:
        return 'No Snapshots Taken Yet...'
    else:
        fig = go.Figure(figure)
        snapshot_file = 'student_snapshot_' + str(n_clicks) + '.html'
        fig.write_html(snapshot_file, include_plotlyjs='cdn')
        return 'Most Recent Snapshot Saved in ' + snapshot_file