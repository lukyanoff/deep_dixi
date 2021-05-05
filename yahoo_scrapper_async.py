from datetime import datetime
from structlog import get_logger
import pandas as pd

from structlog import get_logger
from tqdm import tqdm
from lib.repository.FileOhlcRepository import FileOhlcRepository
from lib.repository.SymbolRepository import SymbolRepository
from lib.scrapper.YahooScrapper import YahooScrapper

pd.options.display.max_columns = None
pd.options.display.max_rows = None

# create logger


from multiprocessing import Pool, Queue

def download(symbol):
    try:
        #print('Begin pooling')
        logger = get_logger()
        scrapper = YahooScrapper()
        ohlc_repository = FileOhlcRepository("d:/E2/_temp/stock", logger)
        df = scrapper.download_latest_minutes(symbol)
        ohlc_repository.write_data("yahoo", symbol, df)
    except:
        pass


def main():
    q = Queue()
    logger = get_logger()
    symbol_repository = SymbolRepository(logger)
    symbols = symbol_repository.get_avalible_stocks()

    with Pool(25) as p:
        p.map(download, tqdm(symbols))

    print('Exit')


if __name__ == '__main__':
    main()
