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
from datetime import time

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

# layout
layout = html.Div(
    [
        html.H1("Question 4")
    ]
)