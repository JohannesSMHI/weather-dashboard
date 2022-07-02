#!/usr/bin/env python3
"""
Created on 2021-12-23 13:27

@author: johannes
"""

TILE_URL = 'https://{s}.basemaps.cartocdn.com/rastertiles/dark_all/{z}/{x}/{y}.png'

TIME_FIELDS = dict(
    timestamp='Tidsstämpel',
    year='År',
    month='Månad',
    day='Dag',
    hour='Timma',
)


TIMING_OPTIONS = dict(
    day='24h (+ prognos)',
    days3='3 dagar (+ prognos)',
    week='Vecka (+ prognos)',
    month='Månad',
    quartile='Kvartal',
    halfyear='Halvår',
    fullyear='Helår',
    thisyear='I år',
)


PARAMETERS = dict(
    outtemp='Temperatur - Ute',
    intemp='Temperatur - Inne',
    rainh='Regn',
    # raind='Regn - Dag',
    # rainw='Regn - Vecka',
    # rainm='Regn - Månad',
    # raint='Regn - Totalt',
    # outdew='Daggpunkt',
    # outfeel='Temperatur - Känns som',
    winsp='Vindhastighet',
    gust='Byvind',
    windir='Vindriktning',
    outhumi='Luftfuktighet',
    presabs='Lufttryck - Absolut',
    presrel='Lufttryck - Relativt',
)

RAIN_PARA_CONTROL = dict(
    day='rainh',
    days3='rainh',
    week='rainh',
    month='raind',
    quartile='rainw',
    halfyear='rainw',
    thisyear='rainw',
    fullyear='rainm',
)


FORECAST_PARAMETERS = {
    'timestamp',
    'outtemp',
    'outhumi',
    'winsp',
    'gust',
    'windir',
    'presrel',
    'rainh',
}


UNITS = dict(
    intemp='°C',
    outtemp='°C',
    outhumi='%',
    outdew='°C',
    outfeel='°C',
    winsp='m/s',
    gust='m/s',
    windir='°',
    presabs='hPa',
    presrel='hPa',
    rainh='mm',
    raind='mm',
    rainw='mm',
    rainm='mm',
    raint='mm',
)


def get_line_kwargs():
    """Doc."""
    return {
        'type': 'scatter',
        'mode': 'lines+markers',
        'line': {
            'shape': "spline",
            'smoothing': 2,
            'width': 1,
            'color': "#33ffe6"
        },
        'marker': {'symbol': "circle-closed"}
    }


def get_line_zu350_kwargs():
    """Doc."""
    return {
        'type': 'scatter',
        'mode': 'lines+markers',
        'line': {
            'shape': "spline",
            'smoothing': 2,
            'width': 1,
            'color': "#02b305"
        },
        'marker': {'symbol': "circle-closed"}
    }


def get_line_zu500_kwargs():
    """Doc."""
    return {
        'type': 'scatter',
        'mode': 'lines+markers',
        'line': {
            'shape': "spline",
            'smoothing': 2,
            'width': 1,
            'color': "#f06429"
        },
        'marker': {'symbol': "circle-closed"}
    }


def get_scatter_kwargs():
    """Doc."""
    return {
        'type': 'scatter',
        'mode': 'markers',
        'marker': {'symbol': "circle-closed", 'color': "#33ffe6"}
    }


def get_bar_kwargs():
    """Doc."""
    return {
        'type': 'bar',
        'marker': {'color': "#33ffe6"}
    }


def get_forecast_kwargs():
    """Doc."""
    return {
        'type': "line",
        'mode': "lines",
        'line': {'shape': 'spline', 'smoothing': 2,
                 'width': 1, 'color': '#FFA245'}
    }


def get_rain_mima_forecast_kwargs():
    """Doc."""
    return {
        # 'stackgroup': 'rainy',
        'showlegend': False,
        'line': {'shape': "spline", 'smoothing': 2,
                 'width': 0, 'color': "#FFA245"},
    }


FIGURE_KWARGS = dict(
    intemp=get_line_kwargs(),
    outtemp=get_line_kwargs(),
    outhumi=get_line_kwargs(),
    outdew=get_line_kwargs(),
    outfeel=get_line_kwargs(),
    winsp=get_line_kwargs(),
    gust=get_line_kwargs(),
    windir=get_scatter_kwargs(),
    presabs=get_line_kwargs(),
    presrel=get_line_kwargs(),
    rainh=get_bar_kwargs(),
    raind=get_bar_kwargs(),
    rainw=get_bar_kwargs(),
    rainm=get_bar_kwargs(),
    raint=get_bar_kwargs(),
    fc=get_forecast_kwargs(),
    rainherrory_fc=get_rain_mima_forecast_kwargs(),
    rainhmin_fc=get_rain_mima_forecast_kwargs(),
    rainhmax_fc=get_rain_mima_forecast_kwargs(),
    zucchini_fc_350=get_line_zu350_kwargs(),
    zucchini_fc_500=get_line_zu500_kwargs(),
)
