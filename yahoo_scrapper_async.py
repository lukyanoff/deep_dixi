import pandas as pd

from structlog import get_logger
from tqdm import tqdm
from src.repository.FileOhlcRepository import FileOhlcRepository
from src.repository.SymbolRepository import SymbolRepository
from src.scrapper.YahooScrapper import YahooScrapper

pd.options.display.max_columns = None
pd.options.display.max_rows = None

from multiprocessing import Pool

def download(symbol):
    try:
        #print('Begin pooling')
        logger = get_logger()
        scrapper = YahooScrapper()
        ohlc_repository = FileOhlcRepository("d:/E2/_temp/stock", logger)
        df = scrapper.download_latest_minutes(symbol)
        ohlc_repository.write_data("yahoo", symbol, df)
    except Exception as ex:
        print(ex)
        pass


def main():
    logger = get_logger()
    symbol_repository = SymbolRepository(logger)
    symbols = symbol_repository.get_avalible_stocks()

    with Pool(25) as p:
        p.map(download, tqdm(symbols))

    print('Exit')

if __name__ == '__main__':
    main()
