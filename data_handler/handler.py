#!/usr/bin/env python3
"""
Created on 2021-11-27 09:52

@author: johannes
"""
import os
from pathlib import Path
import yaml
import sqlite3
import pandas as pd
import numpy as np


TIME_FMT = '%Y-%m-%d %H:%M:%S'

DAYS_MAPPER = {
    'day':  1,
    'days3': 3,
    'week': 7,
    'month': 30,
    'quartile': 90,
    'halfyear': 180,
    'fullyear': 365,
}


def get_db_conn():
    """
    https://docs.python.org/3/library/sqlite3.html#sqlite3-placeholders:~:text=import%20sqlite3%0A%0Acon%20%3D%20sqlite3.connect(%22%3Amemory%3A%22),%7D)%0Aprint(cur.fetchall())%0A%0Acon.close()
    """
    return sqlite3.connect(os.getenv('TSTWEATHERDB'))


def get_start_time(period, time_zone=None):
    """Doc."""
    today = pd.Timestamp.today(tz=time_zone or 'Europe/Stockholm')
    if period == 'thisyear':
        return pd.Timestamp(f'{today.year}0101').strftime(TIME_FMT)
    elif period in DAYS_MAPPER:
        return (today - pd.Timedelta(days=DAYS_MAPPER.get(period))
                ).strftime(TIME_FMT)
    else:
        # Return according to "day".
        return (today - pd.Timedelta(days=1)).strftime(TIME_FMT)


class DataBaseHandler:
    """Doc."""

    def __init__(self, time_zone=None):
        self.time_zone = time_zone or 'Europe/Stockholm'
        base = Path(__file__).parent
        with open(base.joinpath('resources/parameters.yaml').resolve()) as fd:
            data = yaml.load(fd, Loader=yaml.FullLoader)

        self.db_fields = set(data.get('db_fields'))
        self._start_time = None
        self._end_time = None
        self._app_timing = None

    def post(self, **kwargs):
        """Doc."""
        df = pd.DataFrame(
            {field: item for field, item in kwargs.items() if field in self.db_fields}
        )
        conn = get_db_conn()
        df.to_sql('weather', conn, if_exists='append', index=False)

    def get_data_for_time_period(self):
        """Doc."""
        conn = get_db_conn()
        return pd.read_sql(
            """select * from weather where timestamp between 
            '"""+self.start_time+"""%' and '"""+self.end_time+"""%'""",
            conn
        )

    def get_parameter_data_for_time_period(self, *args, time_period='day'):
        """Return dataframe based on parameter list.

        Args:
            args (str): iterable of parameters.
                        Eg. ('timestamp', 'outtemp', 'winsp')
            time_period (str): period according to TIMING_OPTIONS
                               (eg. "day", "week" or "month").
        """
        para_list = ', '.join(args)
        start_time = get_start_time(time_period, time_zone=self.time_zone)
        end_time = pd.Timestamp.today(tz=self.time_zone).strftime(TIME_FMT)
        conn = get_db_conn()
        return pd.read_sql(
            f"""select {para_list} from weather where timestamp between 
            '"""+start_time+"""' and '"""+end_time+"""'""",
            conn
        )

    @staticmethod
    def get():
        """Doc."""
        conn = get_db_conn()
        return pd.read_sql('select * from weather', conn)

    @staticmethod
    def get_time_log():
        """Doc."""
        conn = get_db_conn()
        query = """select timestamp from weather"""
        return pd.read_sql(query, conn).timestamp.to_list()

    def get_recent_time_log(self):
        """Doc."""
        conn = get_db_conn()
        return pd.read_sql(
            """select timestamp from weather where (timestamp like '"""+self.date_today+"""%' 
            or timestamp like '"""+self.date_yesterday+"""%')""",
            conn
        ).timestamp.to_list()

    @staticmethod
    def get_last_timestamp():
        """Doc."""
        conn = get_db_conn()
        try:
            return pd.read_sql(
                'select timestamp from weather order by rowid desc limit 1', conn
            )['timestamp'][0]
        except IndexError:
            return None

    @staticmethod
    def get_last_parameter_value(parameter):
        """Doc."""
        conn = get_db_conn()
        try:
            return pd.read_sql(
                f'select {parameter} from weather order by rowid desc limit 1', conn
            )[parameter][0]
        except IndexError:
            return None

    @property
    def today(self):
        """Return pandas TimeStamp for today."""
        return pd.Timestamp.today(tz=self.time_zone)

    @property
    def date_today(self):
        """Return date string of today."""
        return self.today.strftime('%Y-%m-%d')

    @property
    def date_yesterday(self):
        """Return date string of yesterday."""
        return (self.today - pd.Timedelta(days=1)).strftime('%Y-%m-%d')

    @property
    def start_time(self):
        """Return start of time window (pandas.Timestamp)"""
        return self._start_time

    @start_time.setter
    def start_time(self, period):
        if period == 'day':
            self._start_time = (self.today - pd.Timedelta(days=1)).strftime(TIME_FMT)
        elif period == 'days3':
            self._start_time = (self.today - pd.Timedelta(days=3)).strftime(TIME_FMT)
        elif period == 'week':
            self._start_time = (self.today - pd.Timedelta(days=7)).strftime(TIME_FMT)
        elif period == 'month':
            self._start_time = (self.today - pd.Timedelta(days=30)).strftime(TIME_FMT)
        elif period == 'quartile':
            self._start_time = (self.today - pd.Timedelta(days=90)).strftime(TIME_FMT)
        elif period == 'halfyear':
            self._start_time = (self.today - pd.Timedelta(days=180)).strftime(TIME_FMT)
        elif period == 'fullyear':
            self._start_time = (self.today - pd.Timedelta(days=365)).strftime(TIME_FMT)
        elif period == 'thisyear':
            self._start_time = pd.Timestamp(f'{self.today.year}0101').strftime(TIME_FMT)

    @property
    def end_time(self):
        """Return end of time window (pandas.Timestamp)"""
        return self._end_time

    @end_time.setter
    def end_time(self, period):
        if period == 'now':
            self._end_time = pd.Timestamp.today(tz=self.time_zone).strftime(TIME_FMT)
        else:
            self._end_time = pd.Timestamp(period).strftime(TIME_FMT)

    @property
    def app_timing(self):
        """Return app time spec."""
        return self._app_timing

    @app_timing.setter
    def app_timing(self, timing):
        self._app_timing = timing


def get_forecast_db_conn():
    """Doc."""
    return sqlite3.connect(os.getenv('FORECASTDB'))


class ForecastHandler:
    """Get weather forecast based SMHI model 'PMP3g' (grid size: 2.8 km).

    Data from SMHI:s open API.
    https://www.smhi.se/data/utforskaren-oppna-data/meteorologisk-prognosmodell-pmp3g-2-8-km-upplosning-api
    """

    def __init__(self, time_zone=None):
        self.time_zone = time_zone or 'Europe/Stockholm'

    def get_mean_value(self, parameter, time_period='day'):
        """Return mean value based on the given time period.

        Args:
            parameter (str): Parameter name. Eg. 'outtemp'
            time_period (str): period according to TIMING_OPTIONS
                               (eg. "day", "days3").
        """
        values = self.get_parameter_data_for_time_period(
            parameter, time_period=time_period)
        return np.nanmean(values[parameter])

    def get_parameter_data_for_time_period(self, *args, time_period='day'):
        """Return dataframe based on parameter list.

        Args:
            args (str): iterable of parameters.
                        Eg. ('timestamp', 'outtemp', 'winsp')
            time_period (str): period according to TIMING_OPTIONS
                               (eg. "day", "days3").
        """
        para_list = ', '.join(args)
        start_time = get_start_time(time_period, time_zone=self.time_zone)
        end_time = self.get_endtime(time_period)
        conn = get_forecast_db_conn()
        return pd.read_sql(
            f"""select {para_list} from forecast where timestamp between 
            '"""+start_time+"""' and '"""+end_time+"""'""",
            conn
        )

    def get_rolling_forecast_data(self, *args, time_period='day'):
        """Doc."""
        para_list = ', '.join(args)
        end_time = self.get_endtime(time_period, extra=1)
        start_time = self.today.strftime(TIME_FMT)
        conn = get_forecast_db_conn()
        return pd.read_sql(
            f"""select {para_list} from forecast where timestamp between 
                    '"""+start_time+"""' and '"""+end_time+ """'""",
            conn
        )

    def get_endtime(self, time_period, extra=0):
        """Doc."""
        if time_period == 'day':
            return (self.today + pd.Timedelta(days=1 + extra)).strftime(TIME_FMT)
        elif time_period == 'days3':
            return (self.today + pd.Timedelta(days=3 + extra)).strftime(TIME_FMT)
        elif time_period == 'week':
            return (self.today + pd.Timedelta(days=7 + extra)).strftime(TIME_FMT)

    @property
    def today(self):
        """Return pandas TimeStamp for today."""
        return pd.Timestamp.today(tz=self.time_zone)


class ZucchiniForcast:
    """Calculate the appropriate target weight for zucchini harvest."""

    def __init__(self):
        base = Path(__file__).parent
        self.zz = np.load(
            str(base.joinpath('resources/temp_array.npy').resolve()))
        self.xx, self.yy = np.meshgrid(np.arange(200, 501, 1),
                                       np.arange(200, 601, 1))
        self.min_temp = 12.6
        self.max_temp = 20.6

    def calculate(self, forcast_temp, target_weight=500):
        """Return harvest weight."""
        if forcast_temp < self.min_temp:
            forcast_temp = self.min_temp
            weight_sign = '>'
        elif forcast_temp > self.max_temp:
            forcast_temp = self.max_temp
            weight_sign = '<'
        else:
            weight_sign = ''
        temps_idx = np.logical_and(
            self.yy == int(target_weight), ~np.isnan(self.zz)
        )
        temps = self.zz[temps_idx]
        temp_value = temps[(np.abs(temps - forcast_temp)).argmin()]
        value = self.xx[np.logical_and(temps_idx, self.zz == temp_value)][0]
        return f'{weight_sign}{value} g'

    def calculate_array(self, forcast_temp, target_weight=500):
        """Return harvest weight."""
        forcast_temp = np.array(forcast_temp)
        forcast_temp = np.where(forcast_temp < self.min_temp,
                                self.min_temp, forcast_temp)
        forcast_temp = np.where(forcast_temp > self.max_temp,
                                self.max_temp, forcast_temp)
        temps_idx = np.logical_and(
            self.yy == int(target_weight), ~np.isnan(self.zz)
        )
        temps = self.zz[temps_idx]
        values = []
        for temp in forcast_temp:
            temp_value = temps[(np.abs(temps - temp)).argmin()]
            value = self.xx[np.logical_and(temps_idx, self.zz == temp_value)][0]
            values.append(value)
        return values
