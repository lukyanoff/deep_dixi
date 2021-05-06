import os
from datetime import datetime, timedelta
from os import path
import numpy as np

import pandas as pd

from src.model.StockModel import StockModel


class FileOhlcRepository:
    def __init__(self, root_folder, log):
        self._root_folder = root_folder
        self._log = log
        pass

    def write_data(self, prefix: str, symbol: StockModel, df: pd.DataFrame):
        dataframes = df.groupby(pd.Grouper(key='date', freq='D'))
        for day, df_day in dataframes:
            df_day_for_writing = df_day[['low', 'close', 'open', 'high', 'volume']]

            file_folder = f"{self._root_folder}/{prefix}/{symbol.exchange}/{symbol.symbol}"
            os.makedirs(file_folder, mode=0o777, exist_ok=True)

            file_name = f"{file_folder}/{day.year}-{day.month:02d}-{day.day:02d}.bz2"
            df_day_for_writing.to_csv(file_name, sep="\t", compression="bz2", line_terminator="\n")
            #self._log.msg("Write file", file=file_name)

    def _read_data(self, file_name: str):
        df = pd.read_csv(file_name, sep="\t", compression="bz2")
        df.set_index('date', inplace=True, drop=False)
        return df

    def read_data(self,  prefix: str, symbol: StockModel, begin_date: datetime, end_date: datetime):

        assert begin_date < end_date

        dfs_active = []
        current_date = begin_date
        # iterate files and prevent infinitive loop
        for i in range(365*100):

            if current_date > end_date:
                break

            file = f"{self._root_folder}/{prefix}/{symbol.exchange}/{symbol.symbol}/{current_date.year}-{current_date.month:02d}-{current_date.day:02d}.bz2"
            if path.exists(file):
                df = self._read_data(file)
                df['date']= pd.to_datetime(df['date'])
                dfs_active.append(df)
                #self._log.msg("Load file", file=file)
            else:
                #self._log.msg("File not found", file=file)
                pass

            current_date = current_date + timedelta(hours=24)

        df_original = pd.concat(dfs_active)
        df_original.index = pd.to_datetime(df_original.index)
        df_original.volume = df_original.volume.astype(np.int64)
        return df_original
