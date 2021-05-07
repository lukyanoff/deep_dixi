import numpy as np
import math


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
