from typing import List

from src.calulation.indicator_builder import IndicatorBuilder
from talib import TEMA
import pandas as pd
import numpy as np

from src.calulation.utils import replace_outliers_0_centered, replace_outliers_0_centered_with_log, \
    replace_outliers_with_percentile, log_roc


class PpoBuilder(IndicatorBuilder):
    # https://school.stockcharts.com/doku.php?id=technical_indicators:price_oscillators_ppo
    def __init__(self, slow: int, fast: int, smooth: int, row: str = 'close', rocs: List = []):
        assert slow > fast
        self._row = row;
        self._slow = slow
        self._fast = fast
        self._smooth = smooth
        self._rocs = rocs

        # self._scaler = preprocessing.StandardScaler()

    def _key(self, p):
        return f"ppo{p}(row='{self._row}', fast={self._fast}, slow={self._slow}, k={self._smooth})"

    def build_(self, df: pd.DataFrame):
        ma_fast = TEMA(df[self._row], self._fast)
        ma_slow = TEMA(df[self._row], self._slow)

        ma_fast_na = ma_fast.fillna(0)
        ma_slow_na = ma_slow.fillna(0)

        ppo = 100 * ((ma_fast_na - ma_slow_na) / ma_slow_na)
        ppo = ppo.replace(np.inf, 0)
        ppo = ppo.fillna(0)
        ppo = replace_outliers_with_percentile(ppo, 99)

        ppo_smooth = TEMA(ppo, self._smooth)
        # ppo_smooth = ppo_smooth.fillna(0)
        #
        # ppo_hist = replace_outliers_0_centered_with_log((ppo - ppo_smooth)*100)
        # ppo_hist = replace_outliers_with_percentile(ppo_hist, 99.5)

        #df[self._key('')] = ppo
        df[self._key('_smooth')] = ppo_smooth

        # df[self._key('_hist')] = ppo_hist

        # self._scaler = self._scaler.fit(ppo)
        # params = self._scaler.get_params(deep=True)

        # for roc in self._rocs:
        #     df[f"{self._key('')}_logroc({roc})"] = log_roc(ppo, roc)
        #     # df[f"{self._key('_smooth')}_logroc({roc})"] = log_roc(ppo_smooth, roc)
        #     # df[f"{self._key('_hist')}_logroc({roc})"] = log_roc(ppo_hist, roc)

    def __str__(self):
        return self._key('')