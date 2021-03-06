# Imports
## Dash and Plotly
import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import dash_bootstrap_components as dbc

## Clustering
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

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

# Application
app = dash.Dash(external_stylesheets = [dbc.themes.DARKLY])
app.title = "Dustin's Temperature Dashboard"
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
                            html.H5(id = 'current-temp'),
                            html.P("Welcome to Dustin's Temperature Dashboard! Click the tabs below to view customized, interactive visualizations of the temperature outside " +
                                   "of Dustin's house in Columbus, Ohio. This dashboard was created with Python, SQL, Git, and a few other languages. Links to the source code " +
                                   "and data are available in the upper right-hand corner. The dashboard will refresh every 5 minutes to fetch the latest data.")]),
                                   style = {"margin-bottom": "2rem"}),
                    dbc.Row(
                        dbc.Col(
                            dbc.Tabs([
                                dbc.Tab(dcc.Graph(id = 'daily-figure'), label = 'Average Daily Temp'),
                                dbc.Tab(dcc.Graph(id = 'high-low-figure'), label = "Daily Highs and Lows"),
                                dbc.Tab(dcc.Graph(id = 'weekly-figure'), label = "Last Seven Days")]))),
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
                                    html.H2(id = 'low-temp', className = "text-center")),
                                dbc.CardFooter(id = 'low-temp-date')], color = "info")], width = 3),
                        dbc.Col([
                            dbc.Card([
                                dbc.CardHeader("Highest Temperature"),
                                dbc.CardBody(
                                    html.H2(id = 'high-temp', className = "text-center")),
                                dbc.CardFooter(id = 'high-temp-date')], color = "danger")], width = 3)], justify = "center"),
                    dbc.Row(
                        dbc.Col(
                            html.H3(children = "Humidity Data"), width = "auto"), justify = "center", style = {"margin-top": "5rem"}),
                    dbc.Row(
                        dbc.Col(
                            html.P("While building this dashboard, with admittedly zero meteorological knowledge, Dustin noticed that the temperature seemed to " +
                                   "fluctuate less on days with precipitation. Dustin has a hypothesis that humidity could be a proxy for precipitation, and that " +
                                   "days with higher average humidity should also have a lower standard deviation of temperatures."), width = "auto"), justify = "center",
                                   style = {'margin-bottom': "1rem"}),
                    dbc.Row(
                        dbc.Col(
                            html.P(id = "writeup"), width = "auto"), justify = "center", style = {'margin-bottom': "2rem"}),
                    dbc.Row(
                        dbc.Col(
                            dbc.Tabs([
                                dbc.Tab(dcc.Graph(id = 'hum-cluster-figure'), label = 'Clustering'),
                                dbc.Tab(dcc.Graph(id = 'hum-hist-figure'), label = 'Humidity Distribution'),
                                dbc.Tab(dcc.Graph(id = 'hum-comp-figure'), label = 'Variation Comparison')]))),
                    dbc.Row(
                        dbc.Col(
                            html.H3(children = "How it Works"), width = "auto"), justify = "center", style = {"margin-top": "5rem"}),
                    dbc.Row(
                        dbc.Col(
                            dbc.Accordion([
                                dbc.AccordionItem("Every 15 minutes a Linux server in Dustin's basement requests the current temperature for his zip code from a weather service API. The request is sent via Python script and scheduled with crontab.",
                                                  title = "1 - Current temperature is requested"),
                                dbc.AccordionItem("The current temperature, once retrieved, is timestamped and written to a PostgreSQL database. The same Python script that makes the API request also writes the temperature to the database hosted on Bit.io.",
                                                  title = "2 - Temperature is stored in database"),
                                dbc.AccordionItem("Every 5 minutes Heroku refreshes this dashboard to display the latest data for all measurements and visualizations. The dashboard itself is built in Python using Dash and Plotly, all database queries are written in SQL.",
                                                  title = "3 - Temperature data is queried and displayed in dashboard")]), width = 8), justify = "center", style = {"margin-bottom": "20rem"})]),
                dcc.Interval(id = 'interval-component', interval = 300 * 1000, n_intervals = 0)])

# Live Updates
hght = 625

## Daily Average Figure
@app.callback(Output('daily-figure', 'figure'),
              Input('interval-component', 'n_intervals'))
def update_daily_averages(n):
    ### Collect data
    df_daily = pd.read_sql(queries.daily, con = engine, parse_dates = 'date').sort_values('date')

    ### Build figure
    daily_fig = go.Figure()
    daily_fig.add_trace(go.Scatter(x = df_daily['date'], y = df_daily['temp'],
                                   name = "Daily Average",
                                   line=dict(color='rgba(247,168,1,0.65)', width=1),
                                   text = [item.strftime('%b %d, %Y') for item in df_daily['date']],
                                   hovertemplate = '''Date: %{text}<br>Avg: %{y:.2f}??F<extra></extra>'''))

    daily_fig.add_trace(go.Scatter(x = df_daily['date'], y = df_daily['moving_avg'],
                                   name = "10-Day SMA",
                                   line=dict(color='rgba(56,250,251,1)', width=4),
                                   text = [item.strftime('%b %d, %Y') for item in df_daily['date']],
                                   hovertemplate = '''Date: %{text}<br>Avg: %{y:.2f}??F<extra></extra>'''))

    daily_fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='white',
                            showlegend = True, title_text = 'Average Daily Temperature',
                            xaxis=dict(rangeslider=dict(visible = True), type = "date", showgrid = False),
                            yaxis=dict(gridcolor = '#444444'),
                            yaxis_title = "Temperature in ??F",
                            height = hght)

    return daily_fig

## Daily High Low Figure
@app.callback(Output('high-low-figure', 'figure'),
              Input('interval-component', 'n_intervals'))
def update_daily_high_low(n):
    ### Collect Data
    df_hl = pd.read_sql(queries.daily_hl, con = engine)

    ### Build figure
    hl_fig = go.Figure()
    hl_fig.add_trace(go.Scatter(x = df_hl['min'], y = df_hl['max'], mode = "markers",
                                marker=dict(color='rgba(56,250,251,1)'),
                                text = [item.strftime('%b %d, %Y') for item in df_hl['date']],
                                hovertemplate = '''Date: %{text}<br>Max: %{y:.2f}??F<br>Min: %{x:.2f}??F<extra></extra>'''))

    hl_fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='white',
                            showlegend = False, title_text = 'Daily Highs and Lows',
                            yaxis_title = "Maximum Temperature in ??F",
                            xaxis_title = "Minimum Temperature in ??F",
                            yaxis = dict(gridcolor = '#444444'),
                            height = hght,
                            xaxis = dict(gridcolor = '#444444'))

    return hl_fig

## Last Week Figure
@app.callback(Output('weekly-figure', 'figure'),
              Input('interval-component', 'n_intervals'))
def update_weekly(n):
    ### Collect Data
    df_wk = pd.read_sql(queries.weekly, con = engine)

    ### Low
    low = df_wk.loc[df_wk.temp == df_wk.temp.min()]

    ### High
    high = df_wk.loc[df_wk.temp == df_wk.temp.max()]

    ### Build Figure
    wk_fig = go.Figure()
    wk_fig.add_trace(go.Scatter(x = df_wk['date'], y = df_wk['temp'],
                                   line=dict(color='rgba(56,250,251,1)', width=2),
                                   text = [item.strftime('%b %d, %Y %H:%M%p') for item in df_wk['date']],
                                   hovertemplate = '''Date and Time: %{text}<br>Temp: %{y:.2f}??F<extra></extra>'''))

    wk_fig.add_trace(go.Scatter(x = low['date'], y = low['temp'], mode = "markers",
                                   marker=dict(color='rgba(52,152,219,1)', size = 25, symbol = 'arrow-down'),
                                   text = [item.strftime('%b %d, %Y %H:%M%p') for item in low['date']],
                                   hovertemplate = '''<b>Weekly Low</b><br>Date and Time: %{text}<br>Temp: %{y:.2f}??F<extra></extra>'''))

    wk_fig.add_trace(go.Scatter(x = high['date'], y = high['temp'], mode = "markers",
                                   marker=dict(color='rgba(231,76,60,1)', size = 25, symbol = 'arrow-up'),
                                   text = [item.strftime('%b %d, %Y %H:%M%p') for item in high['date']],
                                   hovertemplate = '''<b>Weekly High</b><br>Date and Time: %{text}<br>Temp: %{y:.2f}??F<extra></extra>'''))

    wk_fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='white',
                            showlegend = False, title_text = 'Last Seven Days',
                            xaxis=dict(rangeslider=dict(visible = True), type = "date", showgrid = False),
                            yaxis=dict(gridcolor = '#444444'),
                            height = hght,
                            yaxis_title = "Temperature in ??F")

    return wk_fig

## Current Temperature
@app.callback(Output('current-temp', 'children'),
              Input('interval-component', 'n_intervals'))
def update_current_temp(n):
    ### Get Data
    cur_temp = pd.read_sql(queries.current_temp, con = engine, parse_dates = 'date')['temp'][0]

    return "The Current Temperature at Dustin's House is {0:.1f}??F".format(cur_temp)

## Record Low
@app.callback(Output('low-temp', 'children'),
              Output('low-temp-date', 'children'),
              Input('interval-component', 'n_intervals'))
def update_record_low(n):
    ### Get Data
    record_low = pd.read_sql(queries.low, con = engine)

    ### Transform
    rl_temp = "{0:.1f}??F".format(record_low['temp'][0])
    rl_date = str(record_low['date'][0].strftime('%B %d, %Y'))

    return rl_temp, rl_date

## Record High
@app.callback(Output('high-temp', 'children'),
              Output('high-temp-date', 'children'),
              Input('interval-component', 'n_intervals'))
def update_record_high(n):
    ### Get Data
    record_high = pd.read_sql(queries.high, con = engine)

    ### Transform
    rh_temp = "{0:.1f}??F".format(record_high['temp'][0])
    rh_date = str(record_high['date'][0].strftime('%B %d, %Y'))

    return rh_temp, rh_date

## Humidity Testing
@app.callback(Output('hum-cluster-figure', 'figure'),
              Output('hum-hist-figure', 'figure'),
              Output('hum-comp-figure', 'figure'),
              Output('writeup', 'children'),
              Input('interval-component', 'n_intervals'))
def update_hum_tests(n):
    ### Get Data
    df = (pd.read_sql(queries.hum_cluster, con = engine, parse_dates = 'date')
            .assign(ah_scaled = lambda x: StandardScaler().fit_transform(x.avg_humidity.array.reshape(-1,1)),
                    st_scaled = lambda x: StandardScaler().fit_transform(x.std_temp.array.reshape(-1,1)),
                    cluster = lambda x: KMeans(3).fit_predict(x[['ah_scaled','st_scaled']])))

    ### Clustering
    clusters = df.cluster.sort_values().unique()
    colors = ['rgba(56,250,251,1)', 'rgba(247,168,1,1)','rgba(0,255,117,1)']
    hovertemp = '''Date: %{text}<br>Avg Humidity: %{x:.2f}%<br>Std Dev of Temp: %{y:.2f}??F<extra></extra>'''

    hum_fig = go.Figure()

    for cluster in clusters:
        hum_fig.add_trace(go.Scatter(x = df.loc[df.cluster == cluster]['avg_humidity'],
                                     y = df.loc[df.cluster == cluster]['std_temp'],
                                     mode = "markers",
                                     name = str('Cluster '+ str(cluster)),
                                     text = [item.strftime('%b %d, %Y') for item in df.loc[df.cluster == cluster]['date']],
                                     hovertemplate = hovertemp,
                                     marker = {'color': colors[cluster]}))

    hum_fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='white',
                          showlegend = True, title_text = 'Humidity and Variation in Temperature',
                          yaxis_title = "Standard Deviation of Temperature in ??F",
                          xaxis_title = "Average Humidity in %",
                          yaxis = dict(gridcolor = '#444444'),
                          height = hght,
                          xaxis = dict(gridcolor = '#444444'))

    ### Histogram
    hum_hist = go.Figure()

    hum_hist.add_trace(go.Histogram(x = df.avg_humidity, marker_color = 'rgba(56,250,251,0.75)'))

    hum_hist.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='white',
                           title_text = 'Distibution of Average Humidity', yaxis_title = "Count of Days",
                           xaxis_title = "Average Humidity in %", yaxis = dict(gridcolor = '#444444'),
                           height = hght,
                           xaxis = dict(gridcolor = '#444444'))

    hum_hist.add_vline(x = df.avg_humidity.quantile(.75), line_width = 4, line_dash = "dot",
                       line_color = 'rgba(247,168,1,1)',
                       annotation_text = '75th Percentile = '+ str(df.avg_humidity.quantile(.75)))

    ### Violin
    test_fig = go.Figure()

    df_test = df.assign(high = lambda x: ['High Humidity Days' if item >= x.avg_humidity.quantile(.75) else 'Normal' for item in x.avg_humidity],
                        normal = 'All Days')

    test_fig.add_trace(go.Violin(x = df_test.normal, y = df_test.std_temp,
                                 name = 'All Days', box_visible = True,
                                 meanline_visible = True,
                                 line_color = 'rgba(56,250,251,1)',
                                 points = 'all'))

    test_fig.add_trace(go.Violin(x = df_test.loc[df_test.high == 'High Humidity Days']['high'],
                                 y = df_test.loc[df_test.high == 'High Humidity Days']['std_temp'],
                                 name = 'High Humidity Days', box_visible = True,
                                 meanline_visible = True,
                                 line_color = 'rgba(247,168,1,1)',
                                 points = 'all'))

    test_fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='white',
                           title_text = 'High Humidity Temperature Variation Compared to All Days',
                           yaxis_title = "Standard Deviation of Temperature in ??F",
                           yaxis = dict(gridcolor = '#444444'),
                           height = hght,
                           xaxis = dict(showgrid = False))

    ### writeup
    count = len(df_test)
    all_std = df_test.std_temp.mean()
    per_75 = df_test.avg_humidity.quantile(.75)
    count_high = len(df_test.loc[df_test.high == "High Humidity Days"])
    high_std = df_test.loc[df_test.high == "High Humidity Days"]['std_temp'].mean()

    writeup_text = (f'''There are currently {count} days with humidity data in the dataset, the average standard deviation of the temperature for those days is {all_std:.2f}??F''' +
                    f''', and the 75th percentile of the humidity percentage is {per_75:.2f}%. There are {count_high} days with an average humidity at or above''' +
                    f''' the 75th percentile, having an average standard deviation of the temperature of {high_std:.2f}??F.''')

    return hum_fig, hum_hist, test_fig, writeup_text

if __name__ == '__main__':
   app.run_server(debug=True)
