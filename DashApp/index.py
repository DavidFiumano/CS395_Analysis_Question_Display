# the purpose of this file is to serve as the "home page" for the app.
# There is a drop-down menu which allows users to select the graph 
# Each graph's callback functions are defined in the student files

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

import plotly.graph_objects as go

from .app import app

from .pages import Home, Q1, Q2, Q3, Q4, Q5, Q6, Q7 # import other page layouts

dropdown_opts = [
    {
        'label' : 'Home',
        'value' : 'Home'
    },
    {
        'label' : 'Question 1',
        'value' : 'Q1'
    },
    {
        'label' : 'Question 2',
        'value' : 'Q2'
    },
    {
        'label' : 'Question 3',
        'value' : 'Q3'
    },
    {
        'label' : 'Question 4',
        'value' : 'Q4'
    },
    {
        'label' : 'Question 5',
        'value' : 'Q5'
    },
    {
        'label' : 'Question 6',
        'value' : 'Q6'
    },
    {
        'label' : 'Question 7',
        'value' : 'Q7'
    }
]

app.layout = html.Div(
    children=[
                html.H1("CS 395 Project 1 Analysis Questions"),
                html.H3("Change Question and Question Data here: "),
                dcc.Dropdown(id="main_dropdown", options=dropdown_opts, value="Home"),
                html.Div(id="content-div")
            ]
)

@app.callback(
    Output('content-div', 'children'),
    [
        Input('main_dropdown', 'value')
    ]
)
def main_dropdown_callback(value):
    if value == 'Home':
        return Home.layout
    elif value == 'Q1':
        return Q1.layout
    elif value == 'Q2':
        return Q2.layout
    elif value == 'Q3':
        return Q3.layout
    elif value == 'Q4':
        return Q4.layout
    elif value == 'Q5':
        return Q5.layout
    elif value == 'Q6':
        return Q6.layout
    elif value == 'Q7':
        return Q7.layout
    else:
        return html.H1("Invalid option selected")