from dataclasses import dataclass


@dataclass
class StockModel:
    symbol: str
    exchange: str = None

    @staticmethod
    def parse(str):
        exchange, symbol = str.split(':')
        return StockModel(exchange=exchange, symbol=symbol)

    def __str__(self) -> str:
        return f"{self.exchange}:{self.symbol}"

