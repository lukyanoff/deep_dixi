import numpy as np
from src.calulation.indicator_builder import build_indicatrors
from src.iterator import take_each_n
from src.model import StockModel
from src.repository.FileOhlcRepository import FileOhlcRepository
from src.scrapper.YahooScrapper import YahooScrapper
from tqdm import tqdm

# from src.calulation.dataframe_utils import slice_df
# from src.calulation.ta import percentage
from datetime import datetime, timedelta
import src.calulation.utils as ta_utils
from src.calulation.indicator_builder import build_indicatrors
from src.calulation.BollingerBand import BollingerBand
from src.calulation.PpoBuilder import PpoBuilder
from src.calulation.RsiBuilder import RsiBuilder
from src.calulation.VortexBuilder import VortexBuilder
from src.calulation.TemaBuilder import TemaBuilder


def get_1min_data(symbol):
    from structlog import get_logger
    logger = get_logger()
    stop_date = datetime.utcnow()
    start_date = stop_date - timedelta(days=365)
    ohlc_repository = FileOhlcRepository("d:/E2/_temp/stock", logger)
    df_original = ohlc_repository.read_data("yahoo", symbol, start_date, stop_date)

    df_original = df_original[df_original['volume'] > 0]
    return df_original


def get_1day_data(symbol):
    yahoo_scrapper = YahooScrapper()
    df_1day = yahoo_scrapper.download_days(symbol)
    return df_1day


def is_slice_has_price_spike(df, threshold):
    max_value = df.close.max()
    min_value = df.close.min()
    return abs(ta_utils.percentage(max_value, min_value)) > threshold



TIME_FORMAT = "%m-%d-%Y %H-%M-%S"

def get_inidicators():
    rocs = [] # 2, 5, 10

    ppos = []
    l = [5, 12, 24, 32, 64, 128, 256, 512] # 2048
    for slow in l:
        for fast in l:
            if fast < slow:
                ppos.append(PpoBuilder(slow=slow, fast=fast, smooth=5, rocs=rocs))

    property = 'close'
    indicators = [
        VortexBuilder(14, rocs=rocs),
        VortexBuilder(24, rocs=rocs),
        VortexBuilder(32, rocs=rocs),

        RsiBuilder(14, 8, rocs=rocs),
        RsiBuilder(24, 8,  rocs=rocs),
        RsiBuilder(32, 5,  rocs=rocs),

        BollingerBand(property=property, n=14, rocs=rocs),
        BollingerBand(property=property, n=24, rocs=rocs),
        BollingerBand(property=property, n=32, rocs=rocs)
    ]

    indicators.extend(ppos)
    return indicators

from src.calulation.utils import calculate_scalping_for_long_fast, calculate_scalping_for_short_fast
def generate_sliced_data_set_v1(symbol: StockModel):
    df_1min = get_1min_data(symbol)
    print(f"Load {len(df_1min)} items")
    df_1min['profit'] = calculate_scalping_for_long_fast(df_1min, 0.5 / 100, 0.25 / 100, 30)
    df_1min = df_1min.dropna()
    indicators = get_inidicators()

    # generate batches
    all_slices = ta_utils.slice_df(df_1min, 4000) # 10000
    slices = take_each_n(all_slices, 1000)
    for slice in slices:
        if is_slice_has_price_spike(slice, 50):
            continue

        basic_price = slice.iloc[-1].close
        basic_volume = slice.iloc[-1].volume
        ta_utils.normilize_data_(slice, basic_price, basic_volume)

        min1_df_with_indicators = build_indicatrors(slice, indicators)
        min1_df_with_indicators = min1_df_with_indicators.iloc[2000:-1]

        min1_df_with_indicators = min1_df_with_indicators.dropna()
        min1_df_with_indicators = ta_utils.scaler_df(min1_df_with_indicators)
        min1_df_with_indicators = min1_df_with_indicators.drop(columns=["date", "close", "open", "date", "high", "low", "volume"])

        small_slices = ta_utils.slice_df(min1_df_with_indicators, 60)
        for s in small_slices:
             d = s.to_dict('list')
             d['profit'] = d['profit'][-1]
             # d['loss'] = d['loss'][-1]
             yield d

def generate_sliced_data_set_v2(symbol: StockModel):
    df_1min = get_1min_data(symbol)
    print(f"Load {len(df_1min)} items")
    df_1min['profit'], df_1min['loss'] = ta_utils.get_long_profit_and_loss(df_1min, l=15)
    df_1min = df_1min.dropna()
    indicators = get_inidicators()

    # generate batches
    all_slices = ta_utils.slice_df(df_1min, 4000)
    slices = take_each_n(all_slices, 2000)
    for slice in slices:
        if is_slice_has_price_spike(slice, 50):
            continue

        basic_price = slice.iloc[0].low
        basic_volume = slice.iloc[0].volume
        ta_utils.normilize_data_(slice, basic_price, basic_volume)

        min1_df_with_indicators = build_indicatrors(slice, indicators)
        min1_df_with_indicators = min1_df_with_indicators.iloc[2000:-1]

        min1_df_with_indicators = min1_df_with_indicators.dropna()
        min1_df_with_indicators = min1_df_with_indicators.drop(columns=["date", "close", "open", "date", "high",  "low", "volume"])
        min1_df_with_indicators = ta_utils.scaler_df(min1_df_with_indicators)

        items = min1_df_with_indicators.to_dict('records')
        for s in items:
             yield s

