from src.calulation.indicator_builder import IndicatorBuilder
from talib import TEMA, STDDEV
import pandas as pd

from src.calulation.utils import  replace_outliers_with_percentile, log_roc

class BollingerBand(IndicatorBuilder):
    def __init__(self, property: str = 'close', n: int = 14, rocs=[]):
        self._n = n
        self._property = property
        self._rocs = rocs

    def _key(self, suffix):
        return f"BB{suffix}(col:'{self._property}', n:{self._n})"

    def build_(self, df: pd.DataFrame):
        std = STDDEV(df[self._property])
        std = std.fillna(0)
        std = replace_outliers_with_percentile(std, 99) *100

        sma = TEMA(df[self._property])
        sma = sma.fillna(0)

        bb_percent = 100 * (df[self._property] - sma) / std
        bb_percent = replace_outliers_with_percentile(bb_percent, 99)

        df[self._key("_STDDEV")] = std
        df[self._key("_%")] = bb_percent

        for roc in self._rocs:
            df[f"{self._key('_STDDEV')}_logroc({roc})"] = log_roc(std, roc)
            df[f"{self._key('_')}_logroc({roc})"] = log_roc(bb_percent, roc)


    def __str__(self):
        return self._key()