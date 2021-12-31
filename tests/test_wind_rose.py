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
import numpy as np
import pathlib
import time


df_example = px.data.wind()
print(df_example.head())

wind_directions = (
    'N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE',
    'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW'
)
windir_mapper = tuple((d, (i * 22.5) + 11.25) for i, d in enumerate(wind_directions))


def get_direction(x):
    """Filter function."""
    for direction, upper_bounds in windir_mapper:
        if x < upper_bounds:
            return direction
    if x >= windir_mapper[-1][1] and ~np.isnan(x):
        return 'N'
    else:
        return np.nan


def get_speed_range(x):
    """Doc."""
    if x == np.floor(x):
        return f'{int(x)}-{int(x)+1}'
    else:
        return f'{int(np.floor(x))}-{int(np.ceil(x))}'


def get_production_dataframe(df):
    """Doc."""
    combos = df[['direction', 'strength']].apply(tuple, axis=1)
    unique_combos = sorted(combos.unique())
    data = {c: [] for c in ('direction', 'strength', 'frequency')}
    nr_obs = float(len(combos))
    for strength in sorted(df['strength'].unique()):
        for windir in wind_directions:
            tup = (windir, strength)
            data['direction'].append(windir)
            data['strength'].append(strength)
            if tup in unique_combos:
                boolean = combos == tup
                data['frequency'].append(boolean.sum() / nr_obs * 100)
            else:
                data['frequency'].append(0)

    return pd.DataFrame(data)


PATH = pathlib.Path(__file__).parent.parent
DATA_PATH = PATH.joinpath("data").resolve()

df = pd.read_feather(DATA_PATH.joinpath('testdata'))
df['timestamp'] = df['timestamp'].apply(pd.Timestamp)


boolean = ~pd.isnull(df['winsp']) & ~pd.isnull(df['windir']) & (df['winsp'] > 0.)
df_wind = df.loc[boolean, ['winsp', 'windir']].reset_index(drop=True)
df_wind['direction'] = df_wind['windir'].apply(lambda x: get_direction(x))
df_wind['strength'] = df_wind['winsp'].apply(lambda x: get_speed_range(x))

df_prod = get_production_dataframe(df_wind)


# fig = px.bar_polar(df_prod, r="frequency", theta="direction",
#                    color="strength", template="plotly_dark",
#                    color_discrete_sequence=px.colors.sequential.Viridis)
fig = px.bar_polar(r=df_prod["frequency"], theta=df_prod["direction"],
                   color=df_prod["strength"], template="plotly_dark",
                   color_discrete_sequence=px.colors.sequential.Viridis)


app = dash.Dash()
app.layout = html.Div([
    dcc.Graph(figure=fig)
])


if __name__ == "__main__":
    app.run_server(debug=True)
