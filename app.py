# Imports
## Dash and Plotly
import dash
from dash import html, dcc
import plotly.graph_objects as go
import dash_bootstrap_components as dbc

## Helpers
import queries
from config import pgs

## Standard
from datetime import datetime
from sqlalchemy import create_engine
import pandas as pd
import os

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

app = dash.Dash(external_stylesheets = [dbc.themes.DARKLY])
#server = app.server

# Navbar
navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("App GitHub", href="https://github.com/dkelly-proj/dustins-house")),
        dbc.DropdownMenu(
            children=[
                dbc.DropdownMenuItem("More Links", header=True),
                dbc.DropdownMenuItem("App Database", href="https://bit.io/dkelly-proj/cbus_temps"),
                dbc.DropdownMenuItem("Temperature GitHub", href="https://github.com/dkelly-proj/temp-log"),
            ],
            nav=True,
            in_navbar=True,
            label="More",
        ),
    ],
    brand="Dustin's LinkedIn",
    brand_href="https://www.linkedin.com/in/dustin-l-kelly/",
    color="primary",
    dark=True,
)


app.layout = html.Div([
                navbar,
                dbc.Container([
                    dbc.Row(
                        dbc.Col(
                            html.H3(children = "The Current Temperature at Dustin's House is " + str(cur_temp) + "°F"),
                            width = "auto"),
                            align = "end", justify = "center", style = {"margin-top": "2rem", "margin-bottom": "2rem"}),
                    dbc.Row(
                        dbc.Col([
                            html.H4(children="Average Daily Temperature at Dustin's House"),
                            dcc.Graph(figure = fig),
                            html.H3(children = "Records"),
                            html.H4(children="Collecting Data Since " + str(min_time), className="hello"),
                            html.H4(children = "Low Record is " + str(record_low['temp'][0]) + " from " + str(record_low['date'][0]))]))])])

if __name__ == '__main__':
   app.run_server(debug=True)
