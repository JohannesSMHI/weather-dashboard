#!/usr/bin/env python3
"""
Created on 2021-12-23 13:37

@author: johannes
"""
import pandas as pd
import pathlib
import pandas as pd


PATH = pathlib.Path(__file__).parent.parent
DATA_PATH = PATH.joinpath("data").resolve()

df = pd.read_feather(DATA_PATH.joinpath('testdata'))
df['timestamp'] = df['timestamp'].apply(pd.Timestamp)

dates = df[['year', 'month', 'day']].apply(lambda x: '{}-{}-{}'.format(*x), axis=1)

df_selected = df.loc[dates == '2020-8-10', :]
