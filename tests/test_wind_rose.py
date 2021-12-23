#!/usr/bin/env python3
"""
Created on 2021-12-23 16:52

@author: johannes
"""
import dash
from dash import dcc
from dash import html
import plotly.express as px
import pandas as pd
import pathlib


for i, d in enumerate(('N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE',
                       'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW')):

    m = i * 22.5
    lower = m - 11.25 if d != 'N' else 360 - 11.25
    upper = m + 11.25
    print(lower, upper)

df_example = px.data.wind()
print(df_example.head())
PATH = pathlib.Path(__file__).parent.parent
DATA_PATH = PATH.joinpath("data").resolve()

df = pd.read_feather(DATA_PATH.joinpath('testdata'))
df['timestamp'] = df['timestamp'].apply(pd.Timestamp)


boolean = ~pd.isnull(df['winsp']) & ~pd.isnull(df['windir'])
df_wind = df.loc[boolean, ['winsp', 'windir']].reset_index(drop=True)




# fig = px.bar_polar(df, r="frequency", theta="direction",
#                    color="strength", template="plotly_dark",
#                    color_discrete_sequence= px.colors.sequential.Plasma_r)
#
# app = dash.Dash()
# app.layout = html.Div([
#     dcc.Graph(figure=fig)
# ])
#
#
# if __name__ == "__main__":
#     app.run_server(debug=True)
