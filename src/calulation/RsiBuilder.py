from src.calulation.indicator_builder import IndicatorBuilder
from talib import SMA, TEMA, ROC, RSI
import pandas as pd
import numpy as np

from src.calulation.utils import replace_outliers_0_centered_with_log, replace_outliers_with_percentile, log_roc, simple_roc


class RsiBuilder(IndicatorBuilder):
    def __init__(self, n: int, smooth: int, rocs=[]):
        self._n = n
        self._smooth = smooth
        self._rocs = rocs

    def _key(self, suffix=''):
        return f"rsi{suffix}(n:{self._n}, smooth:{self._smooth})"

    def build_(self, df: pd.DataFrame):
        rsi = RSI(df['close'], timeperiod=self._n)
        rsi = rsi.replace(np.inf, 0)
        rsi = rsi.fillna(0)

        rsi_smooth = TEMA(rsi, self._smooth)
        rsi_smooth = rsi_smooth.fillna(0)

        # rsi_hist = replace_outliers_0_centered_with_log((rsi - rsi_smooth)*100)
        # rsi_hist = replace_outliers_with_percentile(rsi_hist, 99.9)

        df[self._key('')] = rsi
        df[self._key('_smooth')] = rsi_smooth
        # df[self._key('_hist')] = rsi_hist


        for roc in self._rocs:
            df[f"{self._key('')}_logroc({roc})"] = log_roc(rsi, roc)
            df[f"{self._key('_smooth')}_logroc({roc})"] = log_roc(rsi_smooth, roc)
            # df[f"{self._key('_hist')}_logroc({roc})"] = simple_roc(rsi_hist, roc, p=99.99)

    def __str__(self):
        return self._key()