#!/usr/bin/env python3
"""
Created on 2021-12-23 13:27

@author: johannes
"""

TILE_URL = 'https://{s}.basemaps.cartocdn.com/rastertiles/dark_nolabels/{z}/{x}/{y}.png'

TIME_FIELDS = dict(
    timestamp='Tidsstämpel',
    year='År',
    month='Månad',
    day='Dag',
    hour='Timma',
)


TIMING_OPTIONS = dict(
    day='24h',
    week='Vecka',
    month='Månad',
    quartile='Kvartal',
    halfyear='Halvår',
    fullyear='Helår',
    thisyear='I år',
)


PARAMETERS = dict(
    intemp='Temperatur - Inne',
    outtemp='Temperatur - Ute',
    outhumi='Luftfuktighet',
    outdew='Daggpunkt',
    outfeel='Temperatur - Känns som',
    winsp='Vindhastighet',
    gust='Byvind',
    windir='Vindriktning',
    presabs='Lufttryck - Absolut',
    presrel='Lufttryck - Relativt',
    rainh='Regn - Timma',
    raind='Regn - Dag',
    rainw='Regn - Vecka',
    rainm='Regn - Månad',
    raint='Regn - Totalt',
)

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
