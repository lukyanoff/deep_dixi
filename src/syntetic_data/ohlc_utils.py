import pandas as pd
import numpy as np

def raw(df_):
    return df_

def swap_on_verical(df_):
    def _invert(s, avr_price):
        s = s - avr_price
        s = s * -1
        s = s + avr_price
        return s

    df = df_.copy()

    min_price = df['low'].min()
    max_price = df['high'].max()
    avr_price = (max_price + min_price) / 2

    df['low'] = _invert(df_['high'], avr_price)
    df['high'] = _invert(df_['low'], avr_price)
    df['open'] = _invert(df_['open'], avr_price)
    df['close'] = _invert(df_['close'], avr_price)
    return df

def swap_on_horizontal(df_):
    arr = df_.to_dict(orient='list')
    df = df_.copy()
    df['open'] = arr['open'][::-1]
    df['close'] = arr['close'][::-1]
    df['high'] = arr['high'][::-1]
    df['low'] = arr['low'][::-1]
    df['volume'] = arr['volume'][::-1]
    return df

def swap_on_verical_and_horizont(df_):
    return swap_on_horizontal(swap_on_verical(df_))