#!/usr/bin/env python3
"""
Created on 2021-12-26 16:47

@author: johannes
"""
import pandas as pd
import numpy as np


wind_directions = (
    'N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE',
    'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW'
)
windir_mapper = tuple(
    (d, (i * 22.5) + 11.25) for i, d in enumerate(wind_directions)
)


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


def get_windframe(df):
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
