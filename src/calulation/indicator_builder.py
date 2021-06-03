from typing import List
import pandas as pd

class IndicatorBuilder:
    def __init__(self):
        pass

    def build_(self, df: pd.DataFrame):
        pass


def build_indicatrors(_df: pd.DataFrame, indicator_builders: List[IndicatorBuilder]) -> pd.DataFrame:
    df = _df.copy()
    for indicator_builder in indicator_builders:
        # print(f"Build {indicator_builder}")
        indicator_builder.build_(df)
    return df
