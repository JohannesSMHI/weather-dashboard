#!/usr/bin/env python3
"""
Created on 2021-12-23 13:27

@author: johannes
"""
import copy
import pathlib
import dash
import pandas as pd
from dash.dependencies import Input, Output, State, ClientsideFunction
from dash import dcc
from dash import html
import dash_leaflet as leaflet

from controls import (
    PARAMETERS,
    UNITS,
    TIME_FIELDS,
    TILE_URL,
    TILE_ATTRB,
)

PATH = pathlib.Path(__file__).parent
DATA_PATH = PATH.joinpath("data").resolve()

app = dash.Dash(
    __name__,
    meta_tags=[{"name": "viewport", "content": "width=device-width"}],
)
app.title = "Gällingeväder"
server = app.server

# Create controls
parameter_options = [
    {"label": str(PARAMETERS[para]), "value": str(para)} for para in PARAMETERS
]

# Load data
df = pd.read_feather(DATA_PATH.joinpath('testdata'))
df['timestamp'] = df['timestamp'].apply(pd.Timestamp)

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
    return "Senaste mätvärde: {}".format(df["timestamp"].iloc[-1].strftime('%Y-%m-%d  %H:%M'))


def get_last_parameter_value(parameter):
    if pd.isnull(df[parameter].iloc[-1]):
        return '-'
    else:
        return str(df[parameter].iloc[-1])


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
                                [
                                    leaflet.Map(children=[
                                        leaflet.TileLayer(url=TILE_URL, #maxZoom=11,
                                                          attribution=TILE_ATTRB),
                                        leaflet.CircleMarker(center=[57.386052, 12.295565],
                                                             color='#33ffe6', children=[leaflet.Tooltip("Utmaderna")])
                                    ], center=[57.354, 12.209], zoom=10,
                                        style={
                                            'width': '100%', 'height': '50vh', 'margin': "auto",
                                            "display": "flex", "position": "relative",
                                            "flexDirection": "column"
                                        }
                                    ),
                                ],
                                className="pretty_container",
                                id="station-map",
                            )
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
    boolean = df['timestamp'].dt.date == pd.Timestamp('2020-08-10')
    return df.loc[
        boolean,
        ['timestamp', parameter]
    ]


# Create callbacks
app.clientside_callback(
    ClientsideFunction(namespace="clientside", function_name="resize"),
    Output("output-clientside", "children"),
    [Input("weather_graph", "figure")],
)


# Selectors -> count graph
@app.callback(
    Output("weather_graph", "figure"),
    [
        Input("parameters", "value"),
        # Input("timeing", "value"),
    ],
)
def make_figure(parameters):  #, timeing):
    """Doc."""
    layout_count = copy.deepcopy(layout)

    g = filter_dataframe(df, parameters)
    g.index = g["timestamp"]
    y_parameter = g.columns[1]

    data = [
        dict(
            type="scatter",
            mode="markers",
            x=g.index,
            y=g[y_parameter],
            name=UNITS.get(y_parameter, ''),
            opacity=0,
            hoverinfo="skip",
        ),
        dict(
            type="scatter",
            mode="lines+markers",
            line=dict(shape="spline", smoothing=2, width=1, color="#33ffe6"),
            marker=dict(symbol="circle-open"),
            x=g.index,
            y=g[y_parameter],
            name=UNITS.get(y_parameter, ''),
        ),
    ]

    layout_count["title"] = "{} ({})".format(PARAMETERS.get(y_parameter, ''),
                                             UNITS.get(y_parameter, ''))
    layout_count["dragmode"] = "select"
    layout_count["showlegend"] = False

    figure = dict(data=data, layout=layout_count)
    return figure


if __name__ == "__main__":
    app.run_server(debug=True)
