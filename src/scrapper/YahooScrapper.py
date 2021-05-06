import os

import requests
import pandas as pd
from datetime import datetime, timedelta

from src.model.StockModel import StockModel


class YahooScrapper:
    def __init__(self):
        pass

    def _fetch_data(self, s: StockModel, p1: datetime, p2: datetime, interval: str):
        period1 = int(p1.timestamp())
        period2 = int(p2.timestamp())
        url = "https://query1.finance.yahoo.com/v8/finance/chart/{symbol.symbol}?&period1={period1:d}&period2={period2:d}&interval={interval}" \
            .format(symbol=s, period1=period1, period2=period2, interval=interval)

        #print(url)
        rsp = requests.get(url)
        json = rsp.json()

        timestamp = json['chart']['result'][0]['timestamp']
        low = json['chart']['result'][0]['indicators']['quote'][0]['low']
        close = json['chart']['result'][0]['indicators']['quote'][0]['close']
        open = json['chart']['result'][0]['indicators']['quote'][0]['open']
        volume = json['chart']['result'][0]['indicators']['quote'][0]['volume']
        high = json['chart']['result'][0]['indicators']['quote'][0]['high']

        r = list(zip(timestamp, low, close, open, high, volume))
        # print(r)
        df = pd.DataFrame(r, columns=['timestamp', 'low', 'close', 'open', 'high', 'volume'])
        #df['symbol'] = symbol
        df['date'] = df.apply(lambda x: datetime.utcfromtimestamp(x[0]), axis=1)
        df = df[['date', 'low', 'close', 'open', 'high', 'volume']]
        df.set_index('date', inplace=True, drop=False)
        df.dropna(inplace=True)
        # print('Complete', symbol)

        df['low'] = df['low'].apply(lambda x: round(x, 3))
        df['close'] = df['close'].apply(lambda x: round(x, 3))
        df['open'] = df['open'].apply(lambda x: round(x, 3))
        df['high'] = df['high'].apply(lambda x: round(x, 3))
        df['volume'] = df['volume'].astype('int64', copy=False)
        df.index = pd.to_datetime(df.index)
        return df

    def download_latest_minutes(self, symbol: StockModel):
        end = datetime.utcnow()
        start = end - timedelta(days=7)
        return self._fetch_data(symbol, start, end, "1m")

    def download_days(self, symbol: StockModel):
        end = datetime.utcnow()
        start = end - timedelta(days=9999)
        return self._fetch_data(symbol, start, end, "1d")

    def download_minutes_for_day(self, symbol: StockModel, day: datetime):
        end_time = datetime(year=day.year, month=day.month, day=day.day, hour=0, minute=0, microsecond=0, tzinfo=datetime.timezone.utc)
        start_time = end_time - timedelta(hours=24)
        return self._fetch_data(symbol, start_time, end_time, "1m")