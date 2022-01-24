# Imports
## Dash and Plotly
import dash
from dash import html, dcc
from dash.dependencies import Input, Output
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

## Record Low
record_low = pd.read_sql(queries.low, con = engine)

## Record High
record_high = pd.read_sql(queries.high, con = engine)

## Last Week
df_wk = pd.read_sql(queries.weekly, con = engine)

## Last Seven Days
wk_fig = go.Figure()
wk_fig.add_trace(go.Scatter(x = df_wk['date'], y = df_wk['temp'],
                               line=dict(color='rgba(56,250,251,1)', width=2),
                               text = [item.strftime('%b %d, %Y %H:%M%p') for item in df_wk['date']],
                               hovertemplate = '''Date and Time: %{text}<br>Temp: %{y:.2f}°F<extra></extra>'''))

wk_fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='white',
                        showlegend = False, title_text = 'Last Seven Days',
                        xaxis=dict(rangeslider=dict(visible = True), type = "date", showgrid = False),
                        yaxis=dict(gridcolor = '#444444'),
                        yaxis_title = "Temperature in °F")


app = dash.Dash(external_stylesheets = [dbc.themes.DARKLY])
app.title = "Dustin's Temperature Dashboard"
#server = app.server

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
                            html.P("Welcome to Dustin's Temperature Dashboard! Click the tabs below to view customized, interactive visualizations of the temperature outside " +
                                   "of Dustin's house in Columbus, Ohio. This dashboard was created with Python, SQL, Git, and a few other languages. Links to the source code " +
                                   "and data are available in the upper right-hand corner. The dashboard will refresh every 20 minutes to fetch the latest data.")]),
                                   style = {"margin-bottom": "2rem"}),
                    dbc.Row(
                        dbc.Col(
                            dbc.Tabs([
                                dbc.Tab(dcc.Graph(id = 'daily-figure'), label = 'Average Daily Temp'),
                                dbc.Tab(dcc.Graph(id = 'high-low-figure'), label = "Daily Highs and Lows"),
                                dbc.Tab(dcc.Graph(figure = wk_fig, id = 'weekly-figure'), label = "Last Seven Days")]))),
                    dbc.Row(
                        dbc.Col([
                            html.H3(children = "Records")], width = "auto"), justify = "center", style = {"margin-top": "2rem"}),
                    dbc.Row(
                        dbc.Col([
                            html.H6(children="Collecting Data Since September 29, 2021", className="hello")], width = "auto"), justify = "center", style = {"margin-bottom": "2rem"}),
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
                                dbc.AccordionItem("Every 20 minutes Heroku refreshes this dashboard to display the latest data for all measurements and visualizations",
                                                  title = "3 - Heroku queries and displays data")]), width = 8), justify = "center", style = {"margin-bottom": "20rem"})]),
                dcc.Interval(id = 'interval-component', interval = 1200 * 1000, n_intervals = 0)])

# Daily Average Figure
@app.callback(Output('daily-figure', 'figure'),
              Input('interval-component', 'n_intervals'))
def update_daily_averages(n):
    # Collect data
    df_daily = pd.read_sql(queries.daily, con = engine, parse_dates = 'date').sort_values('date')

    # Build figure
    daily_fig = go.Figure()
    daily_fig.add_trace(go.Scatter(x = df_daily['date'], y = df_daily['temp'],
                                   line=dict(color='rgba(56,250,251,1)', width=2),
                                   text = [item.strftime('%b %d, %Y') for item in df_daily['date']],
                                   hovertemplate = '''Date: %{text}<br>Avg: %{y:.2f}°F<extra></extra>'''))

    daily_fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='white',
                            showlegend = False, title_text = 'Average Daily Temperature',
                            xaxis=dict(rangeslider=dict(visible = True), type = "date", showgrid = False),
                            yaxis=dict(gridcolor = '#444444'),
                            yaxis_title = "Temperature in °F")

    return daily_fig

# Daily High Low Figure
@app.callback(Output('high-low-figure', 'figure'),
              Input('interval-component', 'n_intervals'))
def update_daily_high_low(n):
    # Collect Data
    df_hl = pd.read_sql(queries.daily_hl, con = engine)

    # Build figure
    hl_fig = go.Figure()
    hl_fig.add_trace(go.Scatter(x = df_hl['min'], y = df_hl['max'], mode = "markers",
                                marker=dict(color='rgba(56,250,251,1)'),
                                text = [item.strftime('%b %d, %Y') for item in df_hl['date']],
                                hovertemplate = '''Date: %{text}<br>Max: %{y:.2f}°F<br>Min: %{x:.2f}°F<extra></extra>'''))

    hl_fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='white',
                            showlegend = False, title_text = 'Daily Highs and Lows',
                            yaxis_title = "Maximum Temperature in °F",
                            xaxis_title = "Minimum Temperature in °F",
                            yaxis = dict(gridcolor = '#444444'),
                            xaxis = dict(gridcolor = '#444444'))

    return hl_fig








if __name__ == '__main__':
   app.run_server(debug=True)
