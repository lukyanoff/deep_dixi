import requests

from lib.model.StockModel import StockModel
from typing import List

class SymbolRepository:
    def __init__(self, log):
        self._log = log
        pass

    def get_avalible_stocks(self) -> List[StockModel]:
        headers = {
            'authority': 'scanner.tradingview.com',
            'accept': 'text/plain, */*; q=0.01',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36',
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'origin': 'https://www.tradingview.com',
            'sec-fetch-site': 'same-site',
            'sec-fetch-mode': 'cors',
            'sec-fetch-dest': 'empty',
            'referer': 'https://www.tradingview.com/',
            'accept-language': 'en-US,en;q=0.9,ru;q=0.8,uk;q=0.7,fr;q=0.6,et;q=0.5',
            'cookie': '_ga=GA1.2.2089240020.1591585644; _gid=GA1.2.1660508559.1594869906; _gaexp=GAX1.2.JvcP6bisQLO-DIaUaELrUw.18542.1; _sp_ses.cf1a=*; sessionid=usgpr92o2b5howlzajj9giq2up8xu2rf; png=3bd67e51-9446-44f1-93d9-017342b07d1f; etg=3bd67e51-9446-44f1-93d9-017342b07d1f; cachec=3bd67e51-9446-44f1-93d9-017342b07d1f; tv_ecuid=3bd67e51-9446-44f1-93d9-017342b07d1f; _sp_id.cf1a=2ee6ddc0-1c8e-42b5-8d92-99da9cad4061.1591585643.48.1594948300.1594872911.970c75e9-6783-4536-ad20-235d154b2ad8',
        }

        data = '{"filter":[{"left":"relative_volume_10d_calc|1","operation":"nempty"}],"options":{"active_symbols_only":true,"lang":"en"},"symbols":{"query":{"types":[]},"tickers":[]},"columns":["name","premarket_close","premarket_change","premarket_gap","premarket_volume","close|1","change|1","volume|1","postmarket_close","postmarket_change","postmarket_volume","Recommend.All|1","market_cap_basic","description","name","subtype","update_mode|1","pricescale","minmov","fractional","minmove2"],"sort":{"sortBy":"relative_volume_10d_calc|1","sortOrder":"desc"},"range":[0,10000]}'

        response = requests.post('https://scanner.tradingview.com/america/scan', headers=headers, data=data)
        json = response.json()

        def map_result(i):
            s = i['s']
            items = s.split(':')
            return StockModel(exchange=items[0].upper(), symbol=items[1].upper())

        items = map(map_result, json['data'])

        def filter_result(i: StockModel):
            return i.exchange == "NASDAQ" or i.exchange == "NYSE"

        items = filter(filter_result, items)
        result = list(items)
        return result