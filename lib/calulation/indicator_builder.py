from talib import ATR, SMA, DEMA, TEMA, EMA, LINEARREG, ROC, ADX, MINUS_DI, PLUS_DI, STOCH, RSI, STDDEV, LINEARREG_ANGLE
from finta import TA
from typing import List
import pandas as pd
import numpy as np

# from lib.calulation.ta import replace_outliers
from lib.const import EPSILON





# def normilized_roc(items, n):
#     roc = ROC(items, n)
#     roc = roc.fillna(0)
#     roc, _, _ = replace_outliers(roc)
#     roc = roc / 50
#     return roc

class IndicatorBuilder:
    def __init__(self):
        pass

    def build_(self, df: pd.DataFrame):
        pass


class TemaBuilder(IndicatorBuilder):
    def __init__(self, n: int, row: str = 'close'):
        self._n = n
        self._row = row
        pass

    def _key(self):
        return f"tema(col:'{self._row}', n:{self._n})"

    def build_(self, df: pd.DataFrame):
        df[self._key()] = TEMA(df[self._row], self._n)

    def __str__(self):
        return self._key()


class MacdBuilder(IndicatorBuilder):
    def __init__(self, slow: int, fast: int, smooth: int, row: str = 'close'):
        self._row = row;
        self._slow = slow
        self._fast = fast
        self._smooth = smooth

    def _key(self, p):
        return f"macd{p}(row:'{self._row}', fast:{self._fast}, slow:{self._slow}, k:{self._smooth})"

    def build_(self, df: pd.DataFrame):
        ma_fast = TEMA(df[self._row], self._fast)
        ma_slow = TEMA(df[self._row], self._slow)

        ma_fast_na = ma_fast.fillna(0)
        ma_slow_na = ma_slow.fillna(0)

        macd = ma_fast_na - ma_slow_na
        macd_smooth = TEMA(macd, self._smooth)
        macd_hist = macd - macd_smooth
        # df[self._key('')] = macd
        # df[self._key('_smooth')] = macd_smooth
        df[self._key('_hist')] = macd_hist

        # for roc in rocs:
        #     #df[f"{self._key('')}_roc({roc})"] = ROC(macd, roc)
        #     # df[f"{self._key('_smooth')}_roc({roc})"] = ROC(macd_smooth, roc)
        #     df[f"{self._key('_hist')}_roc({roc})"] = ROC(macd_hist, roc)

    def __str__(self):
        return self._key('')


class VortexNormBuilder(IndicatorBuilder):
    def __init__(self, n: int):
        self._n = n

    def _key_positive(self):
        return f"vortex_positive(n:{self._n})"

    def _key_negative(self):
        return f"vortex_negative(n:{self._n})"

    def _key(self):
        return f"vortex(n:{self._n})"

    def _normilize_valie(self, items):
        def f(v):
            value = v
            if v > 1.5:
                value = 1.5
            if v < 0.5:
                value = 0.5
            return value - 0.5

        return list(map(f, items))

    def build_(self, df: pd.DataFrame):
        d = df[['close', 'open', 'high', 'low']]
        d.reset_index(inplace=True, drop=True)
        d = TA.VORTEX(d, self._n)
        vp = d['VIp'].values
        vn = d['VIm'].values

        df[self._key_positive()] = self._normilize_valie(vp)
        df[self._key_negative()] = self._normilize_valie(vn)
        df.fillna(0, inplace=True)

        # for roc in rocs:
        #     df[(f'{self._key_positive()}_roc({roc})')] = normilized_roc(df[self._key_positive()], roc)
        #     df[(f'{self._key_negative()}_roc({roc})')] = normilized_roc(df[self._key_negative()], roc)

    def __str__(self):
        return self._key_positive()


class VortexBuilder(IndicatorBuilder):
    def __init__(self, n: int = 14, rocs=[]):
        self._n = n
        self._rocs = rocs

    def _key_positive(self):
        return f"vortex_positive(n:{self._n})"

    def _key_negative(self):
        return f"vortex_negative(n:{self._n})"

    def _key(self):
        return f"vortex(n:{self._n})"

    def build_(self, df: pd.DataFrame):
        d = df[['close', 'open', 'high', 'low']]
        d.reset_index(inplace=True, drop=True)
        d = TA.VORTEX(d, self._n)
        vp = d['VIp'].values
        vn = d['VIm'].values

        df[self._key_positive()] = vp
        df[self._key_negative()] = vn
        df.fillna(0, inplace=True)

        for roc in self._rocs:
            df[(f'{self._key_positive()}_roc({roc})')] = ROC(df[self._key_positive()], roc)
            df[(f'{self._key_negative()}_roc({roc})')] = ROC(df[self._key_negative()], roc)

    def __str__(self):
        return self._key_positive()





class RsiBuilder(IndicatorBuilder):
    def __init__(self, n: int, smooth: int, rocs=[]):
        self._n = n
        self._smooth = smooth
        self._rocs = rocs

    def _key(self, suffix=''):
        return f"rsi{suffix}(n:{self._n}, smooth:{self._smooth})"

    def build_(self, df: pd.DataFrame):
        rsi = RSI(df['close'], timeperiod=self._n)
        rsi_sm = SMA(rsi, self._smooth)

        df[self._key('')] = rsi
        df[self._key('_smooth')] = rsi_sm

        for roc in self._rocs:
            # df[f"{self._key('')}_roc({roc})"] = ROC(rsi, roc)
            df[f"{self._key('_smooth')}_roc({roc})"] = ROC(rsi_sm, roc)

    def __str__(self):
        return self._key()


class Roc(IndicatorBuilder):
    def __init__(self, property: str, n: int = 2):
        self._n = n
        self._property = property

    def _key(self):
        return f"ROC(col:'{self._property}', n:{self._n})"

    def build_(self, df: pd.DataFrame):
        df[self._key()] = ROC(df[self._property], self._n)

    def __str__(self):
        return self._key()


def build_indicatrors(_df: pd.DataFrame, indicator_builders: List[IndicatorBuilder]) -> pd.DataFrame:
    df = _df.copy()
    for indicator_builder in indicator_builders:
        # print(f"Build {indicator_builder}")
        indicator_builder.build_(df)
    return df
