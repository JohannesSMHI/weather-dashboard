#!/usr/bin/env python3
"""
Created on 2021-12-23 15:09

@author: johannes

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
                                className="mini_container four columns",
                                id="cross-filter-options",
                            ),
                            html.Div(
                                [
                                    leaflet.Map(
                                        leaflet.TileLayer(url=TILE_URL, maxZoom=20,
                                                          attribution=TILE_ATTRB))
                                ],
                                # style={'margin': "auto", "display": "block", "position": "relative"},
                                className="pretty_container four columns",
                                id="station-map",
                            ),
                        ]
                    ),
"""
