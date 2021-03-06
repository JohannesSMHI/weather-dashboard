#!/usr/bin/env python3
"""
Created on 2021-12-23 13:27

@author: johannes
"""
import os
from dotenv import load_dotenv
from pathlib import Path
import copy
import json
import dash
import pandas as pd
from flask import request, jsonify
from dash.dependencies import Input, Output, ClientsideFunction
from dash import dcc
from dash import html
import dash_leaflet as leaflet
import plotly.express as px

from controls import (
    PARAMETERS,
    FORECAST_PARAMETERS,
    TIMING_OPTIONS,
    UNITS,
    TILE_URL,
    FIGURE_KWARGS,
)
from data_handler.handler import DataBaseHandler, ForecastHandler
from data_handler import windy, rainy

load_dotenv(dotenv_path=Path(__file__).parent.joinpath('.env'))


fc_handler = ForecastHandler(time_zone='Europe/Stockholm')
db_handler = DataBaseHandler(time_zone='Europe/Stockholm')
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
        color="#768DB7"
    ),
    xaxis=dict(
        gridcolor="#768DB7",
    ),
    yaxis=dict(
        gridcolor="#768DB7",
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
            return f'{db_handler.get_last_parameter_value(parameter)} {UNITS.get(parameter)}'
    except TypeError:
        return '-'


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
                                                "utm_weather_icon5.png")
                                        ),
                                    ),
                                    html.H1(
                                        "Utmadernas väderstation",
                                        style={"marginBottom": "0px",
                                               'textAlign': 'center'},
                                    ),
                                    html.H6(get_last_timestamp_text()),
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
                                    'color': '#768DB7',
                                    'background-color': '#1b2444',
                                    'font-color': '#768DB7',
                                    'border-color': '#768DB7',
                                }
                            ),
                            html.P("Välj tidsperiod:", className="control_label"),
                            dcc.Dropdown(
                                id="timing",
                                options=timing_options,
                                value=start_timing,
                                className="dcc_control",
                                style={
                                    'color': '#768DB7',
                                    'background-color': '#1b2444',
                                    'font-color': '#768DB7',
                                    'border-color': '#768DB7',
                                }
                            ),
                            html.P(" ", className="control_label"),
                            dcc.Loading(
                                id="loading",
                                type="default",
                                children=html.Div(id="loading-output")
                            ),
                            # html.P("Dynamisk tidsfiltrering:", className="control_label"),
                            # dcc.DatePickerRange(
                            #     id='my-date-picker-range',
                            #     min_date_allowed=ts_range_tst[0],
                            #     max_date_allowed=ts_range_tst[-1],
                            #     initial_visible_month=ts_range_tst[0],
                            #     end_date=ts_range_tst[-1],
                            #     display_format='YYYY-MM-DD',
                            #     className="dcc_control",
                            # )
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
                                            html.P("Regn - 24h")
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
                            leaflet.Map(children=[
                                leaflet.TileLayer(url=TILE_URL),  # maxZoom=11,
                                leaflet.CircleMarker(center=[57.386052, 12.295565],
                                                     color='#33ffe6',
                                                     children=[leaflet.Tooltip("Utmaderna")])
                            ], center=[57.354, 12.209], zoom=8,
                                style={
                                    'width': '100%', 'height': '50vh', 'margin': "auto",
                                    "display": "flex", "position": "relative",
                                    "flexDirection": "column"
                                }
                            ),
                        ],
                        className="pretty_container four columns",
                        id="station-map",
                    ),
                    html.Div(
                        [dcc.Graph(id="wind_rose_graph")],
                        id="WindRoseGraphContainer",
                        className="pretty_container eight columns",
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
    if parameter != 'presrel':
        # Dummy fix.
        para = parameter
    else:
        para = 'presabs'

    df = db_handler.get_parameter_data_for_time_period(
        'timestamp', para, time_period=timing
    )
    df['timestamp'] = df['timestamp'].apply(pd.Timestamp)

    if parameter == 'presrel':
        # Dummy fix. 56 m above sea level = + 7 hpa for the relative pressure.
        df[para] += 7
        df.rename(columns={para: parameter}, inplace=True)
    elif parameter.startswith('rain'):
        df = rainy.get_rainframe(df, parameter)

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


app.layout = serve_layout

# Create callbacks
app.clientside_callback(
    ClientsideFunction(namespace="clientside", function_name="resize"),
    Output("output-clientside", "children"),
    [
        Input("weather_graph", "figure"),
        Input("wind_rose_graph", "figure")
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
    if timing in ('day', 'days3') and parameter in FORECAST_PARAMETERS:
        df_forecast = filter_forecast(parameter, timing)
        data.append(
            dict(
                **FIGURE_KWARGS.get('rainh_fc'),
                x=df_forecast["timestamp"],
                y=df_forecast[y_parameter],
                name='Prognos',
            )
        )
        if parameter == 'rainh':
            data += [
                dict(
                    **FIGURE_KWARGS.get('rainhmax_fc'),
                    x=df_forecast["timestamp"],
                    y=df_forecast['rainhmin'],
                    name='Prognos - Min',
                ),
                dict(
                    **FIGURE_KWARGS.get('rainhmax_fc'),
                    x=df_forecast["timestamp"],
                    y=df_forecast['rainhmax'],
                    name='Prognos - Max',
                ),
            ]

    layout_count["title"] = "{} ({})".format(PARAMETERS.get(y_parameter, ''),
                                             UNITS.get(y_parameter, ''))
    layout_count['yaxis']["title"] = UNITS.get(y_parameter, '')
    if timing == 'day':
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
            linecolor='#768DB7',
            gridcolor="#768DB7"
        ),
        radialaxis=dict(
            side="counterclockwise",
            showline=True,
            linecolor='#768DB7',
            gridcolor="#768DB7",
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
         'font': {'family': 'verdana', 'color': '#768DB7'}}
    )

    return figure


if __name__ == "__main__":
    app.run_server(debug=True)
