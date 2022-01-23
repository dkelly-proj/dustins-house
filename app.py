# Imports
## Dash and Plotly
import dash
from dash import html, dcc
import plotly.graph_objects as go
import dash_bootstrap_components as dbc

## Helpers
import queries
#from config import pgs

## Standard
from datetime import datetime
from sqlalchemy import create_engine
import pandas as pd
import os

# Get Data
pgs = os.environ['pgs']
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

## Daily Highs and Lows
df_hl = pd.read_sql(queries.daily_hl, con = engine)

## Last Week
df_wk = pd.read_sql(queries.weekly, con = engine)

## Daily Average Graph
daily_fig = go.Figure()
daily_fig.add_trace(go.Scatter(x = df_daily['date'], y = df_daily['temp'],
                               line=dict(color='rgba(56,250,251,1)', width=2)))

daily_fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='white',
                        showlegend = False, title_text = 'Average Daily Temperature',
                        xaxis=dict(rangeslider=dict(visible = True), type = "date", showgrid = False),
                        yaxis=dict(gridcolor = '#444444'),
                        yaxis_title = "Temperature in °F")

## Daily Highs and Lows
hl_fig = go.Figure()
hl_fig.add_trace(go.Scatter(x = df_hl['min'], y = df_hl['max'], mode = "markers",
                            marker=dict(color='rgba(56,250,251,1)')))

hl_fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='white',
                        showlegend = False, title_text = 'Daily Highs and Lows',
                        yaxis_title = "Maximum Temperature in °F",
                        xaxis_title = "Minimum Temperature in °F",
                        yaxis = dict(gridcolor = '#444444'),
                        xaxis = dict(gridcolor = '#444444'))

## Last Seven Days
wk_fig = go.Figure()
wk_fig.add_trace(go.Scatter(x = df_wk['date'], y = df_wk['temp'],
                               line=dict(color='rgba(56,250,251,1)', width=2)))

wk_fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='white',
                        showlegend = False, title_text = 'Last Seven Days',
                        xaxis=dict(rangeslider=dict(visible = True), type = "date", showgrid = False),
                        yaxis=dict(gridcolor = '#444444'),
                        yaxis_title = "Temperature in °F")


app = dash.Dash(external_stylesheets = [dbc.themes.DARKLY])
server = app.server

# Navbar
navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("Dashboard GitHub", href="https://github.com/dkelly-proj/dustins-house")),
        dbc.DropdownMenu(
            children=[
                dbc.DropdownMenuItem("More Links", header=True),
                dbc.DropdownMenuItem("Dashboard Database", href="https://bit.io/dkelly-proj/cbus_temps"),
                dbc.DropdownMenuItem("Temperature GitHub", href="https://github.com/dkelly-proj/temp-log"),
            ],
            nav=True,
            in_navbar=True,
            label="More Links",
        ),
    ],
    brand="Visit Dustin's LinkedIn",
    brand_href="https://www.linkedin.com/in/dustin-l-kelly/",
    color="primary",
    dark=True,
)


app.layout = html.Div([
                navbar,
                dbc.Container([
                    dbc.Row(
                        dbc.Col(
                            html.H3(children = "Dustin's Temperature Dashboard"),
                            width = "auto"),
                            align = "end", justify = "center", style = {"margin-top": "4rem", "margin-bottom": "2rem"}),
                    dbc.Row(
                        dbc.Col([
                            html.H5(children="The Current Temperature at Dustin's House is " + str(cur_temp) + "°F"),
                            html.P('Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Malesuada proin libero nunc consequat interdum varius. Felis eget velit aliquet sagittis id consectetur. Elementum nibh tellus molestie nunc non blandit. Fringilla ut morbi tincidunt augue interdum. Ut tortor pretium viverra suspendisse potenti nullam ac tortor vitae. Nec dui nunc mattis enim ut tellus elementum sagittis vitae. Diam donec adipiscing tristique risus. Ac turpis egestas integer eget aliquet nibh. Sit amet est placerat in egestas.')]), style = {"margin-bottom": "2rem"}),
                    dbc.Row(
                        dbc.Col(
                            dbc.Tabs([
                                dbc.Tab(dcc.Graph(figure = daily_fig), label = 'Average Daily Temp'),
                                dbc.Tab(dcc.Graph(figure = hl_fig), label = "Daily Highs and Lows"),
                                dbc.Tab(dcc.Graph(figure = wk_fig), label = "Last Seven Days")]))),
                    dbc.Row(
                        dbc.Col([
                            html.H3(children = "Records")], width = "auto"), justify = "center", style = {"margin-top": "5rem"}),
                    dbc.Row(
                        dbc.Col([
                            html.H6(children="Collecting Data Since " + str(min_time), className="hello")], width = "auto"), justify = "center", style = {"margin-bottom": "2rem"}),
                    dbc.Row([
                        dbc.Col([
                            dbc.Card([
                                dbc.CardHeader("Lowest Temperature"),
                                dbc.CardBody(
                                    html.H2(str(record_low['temp'][0]) + "°F", className = "text-center")),
                                dbc.CardFooter(str(record_low['date'][0].strftime('%B %d, %Y')))], color = "info")], width = 3),
                        dbc.Col([
                            dbc.Card([
                                dbc.CardHeader("Highest Temperature"),
                                dbc.CardBody(
                                    html.H2(str(record_high['temp'][0]) + "°F", className = "text-center")),
                                dbc.CardFooter(str(record_high['date'][0].strftime('%B %d, %Y')))], color = "danger")], width = 3)], justify = "center"),
                    dbc.Row(
                        dbc.Col(
                            html.H3(children = "How it Works"), width = "auto"), justify = "center", style = {"margin-top": "5rem"}),
                    dbc.Row(
                        dbc.Col(
                            dbc.Accordion([
                                dbc.AccordionItem("Every 15 minutes a Linux server in Dustin's basement requests the current temperature for his zip code from a weather service API",
                                                  title = "1 - Linux server requests temperature"),
                                dbc.AccordionItem("The current temperature, once retrieved, is timestamped and written to a POSTGRESQL database on Bit.io",
                                                  title = "2 - Linux server stores temperature on Bit.io"),
                                dbc.AccordionItem("Every 30 minutes Heroku refreshes this dashboard to display the latest data for all measurements and visualizations",
                                                  title = "3 - Heroku queries and displays data")]), width = 8), justify = "center", style = {"margin-bottom": "20rem"})])])


if __name__ == '__main__':
   app.run_server(debug=True)
