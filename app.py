# imports
import dash
from dash import html, dcc
from datetime import datetime
from sqlalchemy import create_engine
from config import pgs
import pandas as pd
import os
import plotly.graph_objects as go

# get minimum time
#pgs = os.environ['pgs']
engine = create_engine(pgs)

# Header
min_time = (pd.read_sql('Select min(date) from "dkelly-proj/cbus_temps"."temp_log";',
                        con = engine, parse_dates = 'date')['min'][0]
                        .strftime('%B %d, %Y'))

# Line Graph
## Query
sql = '''Select date_trunc('day', date) "date", avg(temp) "temp"
from "dkelly-proj/cbus_temps"."temp_log"
group by 1
order by 1;'''
df_daily = pd.read_sql(sql, con = engine, parse_dates = 'date').sort_values('date')

## Graph
fig = go.Figure()
fig.add_trace(go.Scatter(x = df_daily['date'], y = df_daily['temp']))

app = dash.Dash(__name__)
#server = app.server

app.layout = html.Div([html.H1(children="Collecting Data Since " + str(min_time), className="hello"),
                       html.H2(children="Average Daily Temperature"),
                       dcc.Graph(figure = fig)])

if __name__ == '__main__':
   app.run_server(debug=True)
