#!/usr/bin/env python3
"""
Created on 2021-12-23 13:27

@author: johannes
"""
import os
from dotenv import load_dotenv
import copy
import json
import pathlib
import dash
import pandas as pd
from flask import request, jsonify
from dash.dependencies import Input, Output, State, ClientsideFunction
from dash import dcc
from dash import html
import dash_leaflet as leaflet
import plotly.express as px

import windy
from controls import (
    PARAMETERS,
    UNITS,
    TIME_FIELDS,
    TILE_URL,
    TILE_ATTRB,
)
from data_handler.handler import DataBaseHandler, DataHandler
load_dotenv()


db_handler = DataBaseHandler(time_zone='Europe/Stockholm')
# db_handler.start_time = 'quartile'
db_handler.start_time = 'halfyear'
db_handler.end_time = 'now'

data_source = DataHandler(data=db_handler.get_data_for_time_period())

app = dash.Dash(
    __name__,
    meta_tags=[{"name": "viewport", "content": "width=device-width"}],
)
app.title = "Gällingeväder"
server = app.server


@server.route('/time_log', methods=['GET'])
def get_time_log():
    """GET database time log."""
    headers = request.headers
    auth = headers.get('api_key')
    if auth == os.getenv('API_ACCESS_KEY'):
        recent = request.args.get('recent')
        if recent:
            log = db_handler.get_recent_time_log()
        else:
            log = db_handler.get_time_log()
        return jsonify({'time_log': log}), 200
    else:
        return jsonify({"message": "ERROR: Unauthorized"}), 401


@server.route('/import', methods=['PUT'])
def import_data():
    """POST data to database."""
    headers = request.headers
    auth = headers.get('api_key')
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

layout = dict(
    autosize=True,
    automargin=True,
    margin=dict(l=60, r=30, b=20, t=40),
    hovermode="closest",
    legend=dict(font=dict(size=10), orientation="h"),
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
    return "Senaste mätvärde: {}".format(data_source.df["timestamp"].iloc[-1].strftime('%Y-%m-%d  %H:%M'))


def get_last_parameter_value(parameter):
    if pd.isnull(data_source.df[parameter].iloc[-1]):
        return '-'
    else:
        return str(data_source.df[parameter].iloc[-1])


def serve_layout():
    return html.Div(
        [
            dcc.Store(id="aggregate_data"),
            # empty Div to trigger javascript file for graph resizing
            html.Div(id="output-clientside"),
            html.Div(
                [
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.H1(
                                        "Väderstation - Utmaderna",
                                        style={"marginBottom": "0px"},
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
                            html.Div(
                                [
                                    html.P("Välj parameter:", className="control_label"),
                                    dcc.Dropdown(
                                        id="parameters",
                                        options=parameter_options,
                                        # multi=True,
                                        value=list(PARAMETERS)[0],
                                        className="dcc_control",
                                        style={
                                            'color': '#768DB7',
                                            'background-color': '#1b2444',
                                            'font-color': '#768DB7',
                                            'border-color': '#768DB7',
                                        }
                                    )
                                ],
                                className="mini_container",
                                id="cross-filter-options",
                            ),
                            html.Div(
                                [dcc.Graph(id="wind_rose_graph")],
                                id="WindRoseGraphContainer",
                                className="pretty_container",
                            ),
                            # html.Div(
                            #     [
                            #         leaflet.Map(children=[
                            #             leaflet.TileLayer(url=TILE_URL, #maxZoom=11,
                            #                               attribution=TILE_ATTRB),
                            #             leaflet.CircleMarker(center=[57.386052, 12.295565],
                            #                                  color='#33ffe6', children=[leaflet.Tooltip("Utmaderna")])
                            #         ], center=[57.354, 12.209], zoom=8,
                            #             style={
                            #                 'width': '100%', 'height': '50vh', 'margin': "auto",
                            #                 "display": "flex", "position": "relative",
                            #                 "flexDirection": "column"
                            #             }
                            #         ),
                            #     ],
                            #     className="pretty_container",
                            #     id="station-map",
                            # )
                        ],
                        id="left-column",
                        className="four columns",
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
                            # html.Div(
                            #     [dcc.Graph(id="wind_rose_graph")],
                            #     id="WindRoseGraphContainer",
                            #     className="pretty_container",
                            # ),
                        ],
                        id="right-column",
                        className="eight columns",
                    ),
                ],
                className="row flex-display",
            ),
        ],
        id="mainContainer",
        style={"display": "flex", "flexDirection": "column"},
    )


app.layout = serve_layout


def filter_dataframe(df, parameter):
    """Doc."""
    # boolean = df['timestamp'] >= pd.Timestamp('2021-11-29')
    boolean = df['timestamp'].dt.date == pd.Timestamp('2021-08-10')
    return df.loc[
        boolean,
        ['timestamp', parameter]
    ]


def filter_wind_rose(df):
    """Doc."""
    boolean = ~pd.isnull(df['winsp']) & ~pd.isnull(df['windir']) & (df['winsp'] > 0.)
    df_wind = df.loc[boolean, ['winsp', 'windir']].reset_index(drop=True)
    df_wind['direction'] = df_wind['windir'].apply(lambda x: windy.get_direction(x))
    df_wind['strength'] = df_wind['winsp'].apply(lambda x: windy.get_speed_range(x))
    return windy.get_windframe(df_wind)


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
    Output("weather_graph", "figure"),
    [
        Input("parameters", "value"),
        # Input("timeing", "value"),
    ],
)
def make_figure(parameters):  #, timeing):
    """Doc."""
    df_selected = filter_dataframe(data_source.df, parameters)
    layout_count = copy.deepcopy(layout)
    y_parameter = df_selected.columns[1]
    df_selected.index = df_selected["timestamp"]
    data = [
        dict(
            type="scatter",
            mode="markers",
            x=df_selected.index,
            y=df_selected[y_parameter],
            name=UNITS.get(y_parameter, ''),
            opacity=0,
            hoverinfo="skip",
        ),
        dict(
            type="scatter",
            mode="lines+markers",
            line=dict(shape="spline", smoothing=2, width=1, color="#33ffe6"),
            marker=dict(symbol="circle-open"),
            x=df_selected.index,
            y=df_selected[y_parameter],
            name=UNITS.get(y_parameter, ''),
        ),
    ]

    layout_count["title"] = "{} ({})".format(PARAMETERS.get(y_parameter, ''),
                                             UNITS.get(y_parameter, ''))
    layout_count["dragmode"] = "select"
    layout_count["showlegend"] = False

    figure = dict(data=data, layout=layout_count)
    return figure


@app.callback(
    Output("wind_rose_graph", "figure"),
    [
        Input("parameters", "value"),
        # Input("timeing", "value"),
    ],
)
def make_wind_rose_figure(parameters):  #, timeing):
    """Doc."""
    df_selected = filter_wind_rose(data_source.df)

    figure = px.bar_polar(
        r=df_selected["frequency"], theta=df_selected["direction"], color=df_selected["strength"],
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
         'legend': {'font': {'size': 10}, 'orientation': 'h'},
         'title': 'Vindrosett',
         'paper_bgcolor': '#1b2444',
         'plot_bgcolor': '#1b2444',
         'font': {'family': 'verdana', 'color': '#768DB7'}}
    )

    return figure


if __name__ == "__main__":
    app.run_server(debug=True)
