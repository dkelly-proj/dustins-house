# Imports
import dash
from dash import html, dcc
from datetime import datetime
from sqlalchemy import create_engine
from config import pgs
import pandas as pd
import os
import plotly.graph_objects as go
import queries

# Get Data
#pgs = os.environ['pgs']
engine = create_engine(pgs)

## Current Temp
cur_temp = pd.read_sql(queries.current_temp, con = engine, parse_dates = 'date')['temp'][0]

## Earliest Data
min_time = pd.read_sql(queries.min_date, con = engine, parse_dates = 'date')['min'][0].strftime('%B %d, %Y')

## Daily Average
df_daily = pd.read_sql(queries.daily, con = engine, parse_dates = 'date').sort_values('date')

## Record Low
record_low = pd.read_sql(queries.low, con = engine)

## Record High
record_high = pd.read_sql(queries.high, con = engine)

## Graph
fig = go.Figure()
fig.add_trace(go.Scatter(x = df_daily['date'], y = df_daily['temp']))

app = dash.Dash(__name__)
#server = app.server

app.layout = html.Div([html.H6(children = "Current Temp is " + str(cur_temp) + "°F"),
                       html.H1(children="Collecting Data Since " + str(min_time), className="hello"),
                       html.H2(children="Average Daily Temperature"),
                       dcc.Graph(figure = fig),
                       html.H2(children = "Records"),
                       html.H6(children = "Low Record is " + str(record_low['temp'][0]) + " from " + str(record_low['date'][0]))])

if __name__ == '__main__':
   app.run_server(debug=True)
