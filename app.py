# imports
import dash
from dash import html, dcc
from datetime import datetime
from sqlalchemy import create_engine
#from config import pgs
import pandas as pd

# get minimum time
engine = create_engine(pgs)

min_time = (pd.read_sql('Select min(date) from "dkelly-proj/cbus_temps"."temp_log";',
                        con = engine, parse_dates = 'date')['min'][0]
                        .strftime('%B %d, %Y'))

app = dash.Dash(__name__)
server = app.server

app.layout = html.Div([html.H1(children="Collecting Data Since " + str(min_time), className="hello")])

#if __name__ == '__main__':
#    app.run_server(debug=True)
