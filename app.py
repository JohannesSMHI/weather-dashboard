#!/usr/bin/env python3
"""
Created on 2021-12-23 13:27

@author: johannes
"""
import copy
import json
import os
from pathlib import Path

import dash
import numpy as np
import pandas as pd
import plotly.express as px
from dash import dcc
from dash import html
from dash.dependencies import Input, Output, ClientsideFunction
from dotenv import load_dotenv
from flask import request, jsonify

from controls import (
    PARAMETERS,
    RAIN_PARA_CONTROL,
    FORECAST_PARAMETERS,
    TIMING_OPTIONS,
    UNITS,
    FIGURE_KWARGS,
)
from data_handler import windy, rainy
from data_handler.handler import (
    DataBaseHandler,
    ForecastHandler,
    ZucchiniForcast
)

load_dotenv(dotenv_path=Path(__file__).parent.joinpath('.env'))


fc_handler = ForecastHandler(time_zone='Europe/Stockholm')
db_handler = DataBaseHandler(time_zone='Europe/Stockholm')
zu_handler = ZucchiniForcast()

start_timing = 'day'
db_handler.start_time = start_timing
db_handler.end_time = 'now'
db_handler.app_timing = start_timing

app = dash.Dash(
    __name__,
    meta_tags=[{"name": "viewport", "content": "width=device-width"}],
)
app.title = "Gällingeväder"
server = app.server


@server.route('/time_log/', methods=['GET'])
def get_time_log():
    """GET database time log."""
    headers = request.headers
    auth = headers.get('apikey')
    if auth == os.getenv('API_ACCESS_KEY'):
        recent = request.args.get('recent')
        if recent and recent != 'false':
            log = db_handler.get_recent_time_log()
        else:
            log = db_handler.get_time_log()
        return jsonify({'time_log': log}), 200
    else:
        return jsonify({"message": "ERROR: Unauthorized"}), 401


@server.route('/import/', methods=['PUT'])
def import_data():
    """POST data to database."""
    headers = request.headers
    auth = headers.get('apikey')
    if auth == os.getenv('API_ACCESS_KEY'):
        record = json.loads(request.data)
        db_handler.post(**record)
        return jsonify({"message": "OK: data imported"}), 200
    else:
        return jsonify({"message": "ERROR: Unauthorized"}), 401


# Create controls
parameter_options = [
    {"label": str(PARAMETERS[para]), "value": str(para)} for para in PARAMETERS
]
timing_options = [
    {"label": str(TIMING_OPTIONS[para]), "value": str(para)} for para in TIMING_OPTIONS
]


layout = dict(
    autosize=True,
    automargin=True,
    margin=dict(l=60, r=30, b=20, t=40),
    hovermode="x unified",
    dragmode="select",
    legend=dict(
        font=dict(size=12),
        orientation="h",
        x=0,
        y=0.99,
    ),
    title="Översikt",
    paper_bgcolor='#1b2444',
    plot_bgcolor='#1b2444',
    font=dict(
        family="verdana",
        color="#9CB2D9"
    ),
    xaxis=dict(
        gridcolor="#9CB2D9",
    ),
    yaxis=dict(
        gridcolor="#9CB2D9",
    )
)


def get_last_timestamp_text():
    """Doc."""
    try:
        return "Senaste mätvärde: {}".format(
            pd.Timestamp(
                db_handler.get_last_timestamp()
            ).strftime('%Y-%m-%d  %H:%M')
        )
    except TypeError:
        return "Inga mätvärden ännu."


def get_last_parameter_value(parameter):
    """Doc."""
    try:
        if pd.isnull(db_handler.get_last_parameter_value(parameter)):
            return '-'
        else:
            return f'{db_handler.get_last_parameter_value(parameter)} ' \
                   f'{UNITS.get(parameter)}'
    except TypeError:
        return '-'


def get_forecast_harvest_weight(target_weight=500):
    """Doc."""
    try:
        mean_value = fc_handler.get_mean_value('outtemp')
        harvest_weight = zu_handler.calculate(mean_value,
                                              target_weight=target_weight)
        return harvest_weight
    except TypeError:
        return '-'


def get_forecast_harvest_text():
    weight = get_forecast_harvest_weight(target_weight=350)
    return f'Aktuell skördvikt (EKO-zucchini): {weight} - 350 g'


def get_forecast_harvest_info_box(target_weight=500):
    weight = get_forecast_harvest_weight(target_weight=target_weight)
    return f'{weight} - {target_weight} g'


def get_temp_forecast_text():
    mean_temp = fc_handler.get_mean_value('outtemp')
    return f'Kommande dygnsmedeltemperatur {round(mean_temp, 1)}'


def serve_layout():
    """Doc."""
    return html.Div(
        [
            dcc.Store(id="aggregate_data"),
            html.Div(id="output-clientside"),
            html.Div(
                [
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Div(
                                        className="div-logo",
                                        children=html.Img(
                                            className="logo",
                                            src=app.get_asset_url(
                                                # "utm_weather_icon5.png")
                                                "utm_weather_icon_new.png")
                                        ),
                                    ),
                                    html.H1(
                                        "Utmadernas väderstation",
                                        style={"marginBottom": "0px",
                                               'textAlign': 'center',
                                               'color': '#1b2444'},
                                    ),
                                    html.H6(get_last_timestamp_text(),
                                            style={'color': '#1b2444'}),
                                    html.H6(get_forecast_harvest_text(),
                                            style={'color': '#1b2444'})
                                ]
                            )
                        ],
                        className="two-half column",
                        id="title",
                    ),
                ],
                id="header",
                className="row flex-display",
                style={"marginBottom": "25px"},
            ),
            html.Div(
                [
                    html.Div(
                        [
                            html.P("Välj parameter:", className="control_label"),
                            dcc.Dropdown(
                                id="parameters",
                                options=parameter_options,
                                value=list(PARAMETERS)[0],
                                className="dcc_control",
                                style={
                                    'color': '#9CB2D9',
                                    'background-color': '#1b2444',
                                    'font-color': '#9CB2D9',
                                    'border-color': '#9CB2D9',
                                }
                            ),
                            html.P("Välj tidsperiod:", className="control_label"),
                            dcc.Dropdown(
                                id="timing",
                                options=timing_options,
                                value=start_timing,
                                className="dcc_control",
                                style={
                                    'color': '#9CB2D9',
                                    'background-color': '#1b2444',
                                    'font-color': '#9CB2D9',
                                    'border-color': '#9CB2D9',
                                }
                            ),
                            html.P(" ", className="control_label"),
                            dcc.Loading(
                                id="loading",
                                type="default",
                                children=html.Div(id="loading-output")
                            ),
                        ],
                        className="pretty_container four columns",
                        id="cross-filter-options",
                    ),
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Div(
                                        [
                                            html.H6(get_last_parameter_value('outtemp'),
                                                    id="text_outtemp"),
                                            html.P("Temperatur")
                                        ],
                                        id="id_outtemp",
                                        className="mini_container",
                                    ),
                                    html.Div(
                                        [
                                            html.H6(get_last_parameter_value('winsp'),
                                                    id="text_winsp"),
                                            html.P("Vindhastighet")
                                        ],
                                        id="id_winsp",
                                        className="mini_container",
                                    ),
                                    html.Div(
                                        [
                                            html.H6(get_last_parameter_value('raind'),
                                                    id="text_raind"),
                                            html.P("Regn - idag")
                                        ],
                                        id="id_raind",
                                        className="mini_container",
                                    ),
                                    html.Div(
                                        [
                                            html.H6(get_last_parameter_value('presabs'),
                                                    id="text_presabs"),
                                            html.P("Lufttryck (abs)")
                                        ],
                                        id="id_presabs",
                                        className="mini_container",
                                    ),
                                ],
                                id="info-container",
                                className="row container-display",
                            ),
                            html.Div(
                                [dcc.Graph(id="weather_graph")],
                                id="weatherGraphContainer",
                                className="pretty_container",
                            ),
                        ],
                        id="right-column",
                        className="eight columns",
                    ),
                ],
                className="row flex-display",
            ),
            html.Div(
                [
                    html.Div(
                        [
                            html.Div(
                                [dcc.Graph(id="wind_rose_graph")],
                                id="WindRoseGraphContainer",
                                className="pretty_container_wind four columns",
                            )
                        ],
                        className="pretty_container four columns",
                        id="roses",
                    ),
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Div(
                                        [
                                            html.H6(get_forecast_harvest_info_box(target_weight=350),
                                                    id="harvest_350"),
                                            html.P("Målvikt: 350 g")
                                        ],
                                        id="id_350",
                                        className="mini_container",
                                    ),
                                    html.Div(
                                        [
                                            html.H6(get_forecast_harvest_info_box(target_weight=400),
                                                    id="harvest_400"),
                                            html.P("Målvikt: 400 g")
                                        ],
                                        id="id_400",
                                        className="mini_container",
                                    ),
                                    html.Div(
                                        [
                                            html.H6(get_forecast_harvest_info_box(target_weight=450),
                                                    id="harvest_450"),
                                            html.P("Målvikt: 450 g")
                                        ],
                                        id="id_450",
                                        className="mini_container",
                                    ),
                                    html.Div(
                                        [
                                            html.H6(get_forecast_harvest_info_box(target_weight=500),
                                                    id="harvest_500"),
                                            html.P("Målvikt: 500 g")
                                        ],
                                        id="id_500",
                                        className="mini_container",
                                    ),
                                ],
                                id="zucchini-info-container",
                                className="row container-display",
                            ),
                            html.Div(
                                [dcc.Graph(id="zucchini_graph")],
                                id="zucchiniGraphContainer",
                                className="pretty_container",
                            ),
                        ],
                        id="zucchini-right-column",
                        className="eight columns",
                    ),
                ],
                className="row flex-display",
            ),
        ],
        id="mainContainer",
        style={"display": "flex", "flexDirection": "column"},
    )


def filter_dataframe(parameter, timing):
    """Doc."""
    if parameter == 'presrel':
        # Dummy fix.
        para = 'presabs'
    elif parameter.startswith('rain'):
        para = RAIN_PARA_CONTROL.get(timing)
    else:
        para = parameter

    df = db_handler.get_parameter_data_for_time_period(
        'timestamp', para, time_period=timing
    )
    df['timestamp'] = df['timestamp'].apply(pd.Timestamp)

    if parameter == 'presrel':
        # Dummy fix. 56 m above sea level = + 7 hpa for the relative pressure.
        df[para] += 7
        df.rename(columns={para: parameter}, inplace=True)
    elif para.startswith('rain'):
        df = rainy.get_rainframe(df, para)

    return df


def filter_harvest_temperature(timing):
    """Doc."""
    params = ['timestamp', 'outtemp']
    df = fc_handler.get_rolling_forecast_data(
        *params, time_period=timing
    )
    df['timestamp'] = df['timestamp'].apply(pd.Timestamp)
    df['meantemp'] = np.nan
    delta = pd.Timedelta(days=1)
    for row in df.itertuples():
        boolean = (df['timestamp'] >= row.timestamp) & \
                  (df['timestamp'] <= (row.timestamp + delta))
        df['meantemp'].iloc[row.Index] = np.nanmean(df.loc[boolean, 'outtemp'])
    return df


def filter_forecast(parameter, timing):
    """Doc."""
    params = ['timestamp', parameter]
    if parameter == 'rainh':
        params += ['rainhmin', 'rainhmax']

    df = fc_handler.get_parameter_data_for_time_period(
        *params, time_period=timing
    )
    df['timestamp'] = df['timestamp'].apply(pd.Timestamp)
    return df


def filter_wind_rose(timing):
    """Doc."""
    df = db_handler.get_parameter_data_for_time_period(
        'winsp', 'windir', time_period=timing
    )
    boolean = ~pd.isnull(df['winsp']) & ~pd.isnull(df['windir']) & (df['winsp'] > 0.)
    df_wind = df.loc[boolean, ['winsp', 'windir']].reset_index(drop=True)
    df_wind['direction'] = df_wind['windir'].apply(lambda x: windy.get_direction(x))
    df_wind['strength'] = df_wind['winsp'].apply(lambda x: windy.get_speed_range(x))
    return windy.get_windframe(df_wind)


RAIN_TITLE = {
    'rainh': 'Regn - Timma',
    'raind': 'Regn - Dag',
    'rainw': 'Regn - Vecka',
    'rainm': 'Regn - Månad',
}


def get_fig_title(para):
    """Doc."""
    if para.startswith('rain'):
        return "{} ({})".format(RAIN_TITLE.get(para, ''), UNITS.get(para, ''))
    else:
        return "{} ({})".format(PARAMETERS.get(para, ''), UNITS.get(para, ''))


app.layout = serve_layout

# Create callbacks
app.clientside_callback(
    ClientsideFunction(namespace="clientside", function_name="resize"),
    Output("output-clientside", "children"),
    [
        Input("weather_graph", "figure"),
        Input("wind_rose_graph", "figure"),
        Input("zucchini_graph", "figure"),
    ],
)


@app.callback(
    Output("loading-output", "children"),
    Input("timing", "value")
)
def input_triggers_spinner(timing):
    """Doc."""
    db_handler.start_time = timing
    db_handler.app_timing = timing
    return None


@app.callback(
    Output("weather_graph", "figure"),
    [
        Input("parameters", "value"),
        Input("timing", "value"),
    ],
)
def make_figure(parameter, timing):
    """Doc."""
    df_selected = filter_dataframe(parameter, timing)
    layout_count = copy.deepcopy(layout)
    y_parameter = df_selected.columns[1]
    data = [
        dict(
            **FIGURE_KWARGS.get(parameter, {}),
            x=df_selected["timestamp"],
            y=df_selected[y_parameter],
            name='Observationer',
        )
    ]
    if timing in ('day', 'days3', 'week') and parameter in FORECAST_PARAMETERS:
        df_forecast = filter_forecast(parameter, timing)
        data.append(
            dict(
                **FIGURE_KWARGS.get('fc'),
                x=df_forecast["timestamp"],
                y=df_forecast[y_parameter],
                name='Prognos - SMHI',
            )
        )
        if parameter == 'rainh':
            data += [
                dict(
                    **FIGURE_KWARGS.get('rainherrory_fc'),
                    x=df_forecast["timestamp"],
                    y=df_forecast[y_parameter],
                    name='Felmarginal',
                    error_y=dict(
                        type='data',
                        thickness=.8,
                        symmetric=False,
                        array=df_forecast['rainhmax']-df_forecast[y_parameter],
                        arrayminus=df_forecast[y_parameter]-df_forecast['rainhmin']
                    )
                ),
            ]

    layout_count["title"] = get_fig_title(y_parameter)
    layout_count['yaxis']["title"] = UNITS.get(y_parameter, '')
    if timing == 'day':
        layout_count['xaxis']['tickformat'] = "%b-%d %H:%M"

    figure = dict(data=data, layout=layout_count)
    return figure


@app.callback(
    Output("zucchini_graph", "figure"),
    [
        Input("timing", "value"),
    ],
)
def make_zucchini_figure(timing):
    """Doc."""
    if timing not in ('day', 'days3', 'week'):
        timing = 'week'

    layout_count = copy.deepcopy(layout)
    df_selected = filter_harvest_temperature(timing)
    df_selected['zucchini_fc_350'] = zu_handler.calculate_array(
        df_selected['meantemp'], target_weight=350)
    df_selected['zucchini_fc_500'] = zu_handler.calculate_array(
        df_selected['meantemp'], target_weight=500)
    data = [
        dict(
            **FIGURE_KWARGS.get('zucchini_fc_350', {}),
            x=df_selected["timestamp"],
            y=df_selected['zucchini_fc_350'],
            name='Målvikt 350 g',
        ),
        dict(
            **FIGURE_KWARGS.get('zucchini_fc_500', {}),
            x=df_selected["timestamp"],
            y=df_selected['zucchini_fc_500'],
            name='Målvikt 500 g',
        )
    ]

    layout_count["title"] = 'Prognoser för skördningsvikter (zucchini)'
    layout_count['yaxis']["title"] = 'Lägsta skördevikt (gram)'
    if timing in {'day', 'days3'}:
        layout_count['xaxis']['tickformat'] = "%b-%d %H:%M"

    figure = dict(data=data, layout=layout_count)
    return figure


@app.callback(
    Output("wind_rose_graph", "figure"),
    [
        Input("timing", "value"),
    ],
)
def make_wind_rose_figure(timing):
    """Doc."""
    df_selected = filter_wind_rose(timing)

    figure = px.bar_polar(
        r=df_selected["frequency"],
        theta=df_selected["direction"],
        color=df_selected["strength"],
        color_discrete_sequence=px.colors.sequential.Viridis,
    )
    figure.update_polars(
        bgcolor='#1b2444',
        angularaxis=dict(
            showline=True,
            linecolor='#9CB2D9',
            gridcolor="#9CB2D9"
        ),
        radialaxis=dict(
            side="counterclockwise",
            showline=True,
            linecolor='#9CB2D9',
            gridcolor="#9CB2D9",
        )
    )
    figure.update_layout(
        {
         'margin': {'l': 60, 'r': 30, 'b': 20, 't': 40},
         'legend': {'font': {'size': 10},
                    'orientation': 'h',
                    'title': 'Vindhastighet (m/s)'},
         'title': 'Vindrosett', 'title_x': .5,
         'paper_bgcolor': '#1b2444',
         'plot_bgcolor': '#1b2444',
         'font': {'family': 'verdana', 'color': '#9CB2D9'}}
    )

    return figure


if __name__ == "__main__":
    app.run_server(debug=True)
