#!/usr/bin/env python3
"""
Created on 2022-01-29 15:27

@author: johannes
"""

RAIN_MAPPER = {
    'rainh': ['date', 'hour'],
    'raind': ['date'],
    'rainw': ['week'],
    'rainm': ['month'],
    'raint': ['year']
}


def get_rainframe(df, parameter):
    """Return a grouped dataframe based on the timing attribute."""
    if not df.empty:
        return df.groupby(
            [df['timestamp'].dt.__getattribute__(t_spec)
             for t_spec in RAIN_MAPPER.get(parameter)]
        ).max().reset_index(drop=True)
    else:
        return df
