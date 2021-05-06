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
  if a==0: return 0
  if a > 0: return math.log(a+1, P)
  return -1 * math.log((-1*a)+1, P)

def replace_outliers_0_centered_with_log(c, n = 2):
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
    return v

def simple_roc(ser, n=2, p=99):
    from talib import ROC
    v = ROC(ser, n) / 100
    v = v.replace(np.inf, 0)
    v = v.fillna(0)
    v = v.round(2)
    v = replace_outliers_with_percentile(v, p)
    return v

