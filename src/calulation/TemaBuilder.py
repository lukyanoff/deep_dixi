from src.calulation.indicator_builder import IndicatorBuilder
from talib import SMA, TEMA, ROC, RSI
import pandas as pd
import numpy as np

from src.calulation.utils import log_roc


class TemaBuilder(IndicatorBuilder):
    def __init__(self, n: int):
        self._n = n

    def _key(self, suffix=''):
        return f"tema(n={self._n})"

    def build_(self, df: pd.DataFrame):
        tema = TEMA(df['close'], timeperiod=self._n)
        tema = tema.fillna(0)
        df[self._key('')] = tema

        # for roc in self._rocs:
        #     df[f"{self._key('')}_logroc({roc})"] = log_roc(rsi, roc, p=99.9)
        #     # df[f"{self._key('_smooth')}_logroc({roc})"] = log_roc(rsi_smooth, roc, p=99.9)
        #     # df[f"{self._key('_hist')}_logroc({roc})"] = log_roc(rsi_hist, roc, p=99.99)

    def __str__(self):
        return self._key()