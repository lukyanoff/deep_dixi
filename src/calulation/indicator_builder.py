from talib import ATR, SMA, DEMA, TEMA, EMA, LINEARREG, ROC, ADX, MINUS_DI, PLUS_DI, STOCH, RSI, STDDEV, LINEARREG_ANGLE
from finta import TA
from typing import List
import pandas as pd
import numpy as np
from tqdm import tqdm
from sklearn.preprocessing import StandardScaler
import torch
class IndicatorBuilder:
    def __init__(self):
        pass

    def build_(self, df: pd.DataFrame):
        pass

    # def _get_scaler(self, name):
    #     scaler = StandardScaler()
    #     try:
    #         params = torch.load(f"./data/scalers/{name}.zip")
    #         scaler.set_params(params)
    #     except IOError as e:
    #         print(e)
    #     return scaler
    #
    # def _save_scaler(self, name, scaler):
    #     params = scaler.get_params(deep=True)
    #     torch.save(f"./data/scalers/{name}.zip", params)


def build_indicatrors(_df: pd.DataFrame, indicator_builders: List[IndicatorBuilder]) -> pd.DataFrame:
    df = _df.copy()
    for indicator_builder in indicator_builders:
        # print(f"Build {indicator_builder}")
        indicator_builder.build_(df)
    return df
