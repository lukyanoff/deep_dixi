from src.calulation.indicator_builder import IndicatorBuilder
import pandas as pd
from finta import TA

from src.calulation.utils import log_roc, replace_outliers

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

        d['VIp'] = d['VIp'].fillna(0)
        d['VIm'] = d['VIm'].fillna(0)

        d['VIp'] = replace_outliers(d['VIp'])
        d['VIm'] = replace_outliers(d['VIm'])

        d['VIp'] = d['VIp'] - 0.5
        d['VIm'] = d['VIm'] - 0.5

        df[self._key_positive()] = d['VIp'].values
        df[self._key_negative()] = d['VIm'].values

        for roc in self._rocs:
            df[(f'{self._key_positive()}_logroc({roc})')] = log_roc(df[self._key_positive()], roc, p=99.9)
            df[(f'{self._key_negative()}_logroc({roc})')] = log_roc(df[self._key_negative()], roc, p=99.9)



    def __str__(self):
        return self._key_positive()