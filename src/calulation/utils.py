import numpy as np
import math

from tqdm import tqdm




def normilize_data_(df, basic_price, basic_volume):
    df['close'] = df['close'] / basic_price
    df['open'] = df['open'] / basic_price
    df['high'] = df['high'] / basic_price
    df['low'] = df['low'] / basic_price

    df['volume'] = np.log2(df['volume'] / basic_volume)


def replace_outliers(c, N=3):
    m = c.mean()
    s = c.std()

    def f(a):
        z = (a - m) / s
        if z > N:
            return m + (N * s)
        elif z < (-1 * N):
            return m - (N * s)
        else:
            return a

    return c.apply(f)


def symetric_log(a, P=2):
    if a == 0: return 0
    if a > 0: return math.log(a + 1, P)
    return -1 * math.log((-1 * a) + 1, P)


def replace_outliers_0_centered_with_log(c, n=2):
    def f(value):
        return symetric_log(value, n)

    return c.apply(f)


def replace_outliers_0_centered(c, n=3):
    abs_values = np.abs(c)
    s = abs_values.std()
    max_value = n * s

    def f(value):
        value_abs = abs(value)
        value_sign = np.sign(value)
        z = value_abs / s
        if z > n:
            return value_sign * max_value
        else:
            return value

    return c.apply(f)


def replace_outliers_with_percentile(c, p=99):
    abs_values = np.abs(c)
    max_value = np.percentile(abs_values, p)

    def f(value):
        value_abs = abs(value)
        value_sign = np.sign(value)
        if value_abs > max_value:
            return max_value * value_sign
        else:
            return value

    return c.apply(f)


def log_roc(ser, n=2, p=99):
    from talib import ROC
    v = ROC(ser, n)
    v = v.replace(np.inf, 0)
    v = v.fillna(0)
    v = replace_outliers_0_centered_with_log(v)
    v = v.round(2)
    v = replace_outliers_with_percentile(v, p)
    v = v / 20  # normilize to [-0.5 .. 0.5]
    return v


def slice_df(df, l):
    for start_index in range(0, len(df)):
        stop_index = start_index + l
        if stop_index < len(df):
            yield df.iloc[start_index:stop_index].copy()
        else:
            break


import numpy as np
import pandas as pd

from scipy.signal import argrelextrema


def crossing_up(a, b, pos=np.int(0), neg=np.nan):
    diff = a < b
    diff_forward = diff.shift(1)
    crossover = pd.Series(np.where(diff - diff_forward == 1, pos, neg), index=a.index)
    return crossover


def crossing_down(a, b, pos=np.int(0), neg=np.nan):
    return crossing_up(b, a, pos, neg)


def count_after_0(s):
    v = s.apply(lambda a: 0 if a == 0 else np.nan)
    v = v.ffill(0) + v.groupby(v.notnull().cumsum()).cumcount()
    v = v.fillna(-1)
    return v.astype('int')


def _extremum(s, n, comparer):
    d = s.copy()
    d = d.apply(lambda a: np.nan)

    ilocs_min = argrelextrema(s.values, comparer, order=n)[0]
    d.iloc[ilocs_min] = 1
    d.iloc[[0, -1]] = np.nan  # reset first and last points
    # print(d)

    return d


def minima(s, n=2):
    return _extremum(s, n, np.less)


def maxima(s, n=2):
    return _extremum(s, n, np.greater_equal)


# df.count_test.plot(figsize=(20,8))
# df['min_flag'] = df['min'].apply(lambda a: a>=1)
# df['max_flag'] = df['max'].apply(lambda a: a>=1)
# df[df['min_flag']].count_test.plot(style='.', lw=10, color='red', marker="v");
# df[df['max_flag']].count_test.plot(style='.', lw=10, color='green', marker="^");


def percentage(base, value):
    return ((value - base) * 100) / base


def percentage1(base, value):
    return ((value - base)) / base


def get_long_profit_and_loss(_df, l, open_indicator='close', profit_indicator='high', loss_indicator='low'):
    df = _df.copy()
    df['profit'] = np.nan
    df['loss'] = np.nan
    data = df.to_dict('records')
    max_len = len(data) - l
    for start in range(l, max_len - 1):
        stop = min(start + l, max_len)
        items = data[start + 1:stop]

        profit_values = list(map(lambda a: a[profit_indicator], items))
        max_value = max(profit_values)
        data[start]['profit'] = percentage1(data[start][open_indicator], max_value)

        loss_values = list(map(lambda a: a[loss_indicator], items))
        min_value = min(loss_values)
        data[start]['loss'] = percentage1(data[start][open_indicator], min_value) * -1

    profit = list(map(lambda a: a['profit'], data))
    loss = list(map(lambda a: a['loss'], data))
    return profit, loss


def calculate_scalping_for_long_fast(_df, profit: float, risk: float, period: int):
    df = _df.copy()
    df['long_rate'] = 0
    #df['result_long_position'] = 0
    data = df.to_dict('records')
    for open_position_index in range(len(data) - 1):
        #logger.msg("Calculate", data=data[open_position_index]['date'] )
        open_position_price = data[open_position_index]['high']
        stop_loss_price = open_position_price - open_position_price * risk
        take_profit_price = open_position_price + open_position_price * profit

        close_position_max_index = min(len(data), open_position_index + period)
        position = 0
        for close_position_index in range(open_position_index + 1, close_position_max_index):
            # update shared vars
            position = position + 1

            # check stop_loss
            low_price = data[close_position_index]['low']
            if low_price <= stop_loss_price:
                data[open_position_index]['long_rate'] = -1
                break

            # check take profit
            high_price = data[close_position_index]['high']
            if high_price >= take_profit_price:
                data[open_position_index]['long_rate'] = 1
                break

    df_ = pd.DataFrame(data)
    df_.set_index('date', inplace=True, drop=False)
    return df_['long_rate']

def calculate_scalping_for_short_fast(_df, profit: float, risk: float, period: int):
    df = _df.copy()
    df['short_rate'] = 0
    #df['result_short_position'] = 0
    data = df.to_dict('records')
    for open_position_index in range(len(data) - 1):
        #logger.msg("Calculate", data=data[open_position_index]['date'] )
        open_position_price = data[open_position_index ]['low']
        stop_loss_price = open_position_price + open_position_price * risk
        take_profit_price = open_position_price - open_position_price * profit

        close_position_max_index = min(len(data), open_position_index + period)
        position = 0
        for close_position_index in range(open_position_index + 1, close_position_max_index):
            # update shared vars
            position = position + 1

            # check stop_loss
            high_price = data[close_position_index]['high']
            if high_price >= stop_loss_price:
                data[open_position_index]['short_rate'] = -1
                break

            # check take profit
            low_price = data[close_position_index]['low']
            if low_price <= take_profit_price:
                data[open_position_index]['short_rate'] = 1
                break

    df_ = pd.DataFrame(data)
    df_.set_index('date', inplace=True, drop=False)
    return df_['short_rate']

#######
def get_all_stocks():
    import csv
    from src.model.StockModel import StockModel
    with open('./_data/watchlist1.txt', newline='') as csvfile:
        records = list(csv.reader(csvfile, delimiter=','))[0]
        for s in records:
            yield StockModel.parse(s)


#######
# scale dataset
from sklearn.preprocessing import StandardScaler
import urllib
import pickle
raw_columns = {'date', 'low', 'close', 'high', 'open', 'volume', 'profit', 'loss'}

def _get_scaler_file_name(col):
    encoded_col = urllib.parse.quote(col)
    file_name = f"./.temp/scaler/{encoded_col}.json"
    return file_name

def fit_scalers(df):
    for col in tqdm(df.columns):
        if col in raw_columns:
            continue

        scaler = StandardScaler(with_mean=False)
        scaler.fit(df[[col]])
        file_name = _get_scaler_file_name(col)
        pickle.dump(scaler, open(file_name, 'wb'))


#%%

from pickle import dump, load
import urllib

def scaler_df(_df):
    df = _df.copy()
    for col in df.columns:
        if col in raw_columns:
            continue

        file_name = _get_scaler_file_name(col)

        scaler = load(open(file_name, 'rb'))
        df[[col]] = scaler.transform(df[[col]])
        df[col] = df[col] / 8

    return df