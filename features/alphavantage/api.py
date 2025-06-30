from dataclasses import dataclass
from datetime import datetime
from typing import Dict
import requests
from config.env import ALPHAVANTAGE_API_KEY


@dataclass
class TickerData:
    symbol: str
    overview: dict
    last_updated: str

market_data_cache: Dict[str, TickerData] = {}

class AlphaVantageAPI:
    @staticmethod
    def get_ticker_overview(symbol: str) -> TickerData:
        if symbol not in market_data_cache:
            print(f"Getting stock price for {symbol}")
            url = f"https://www.alphavantage.co/query?function=OVERVIEW&symbol={symbol}&apikey={ALPHAVANTAGE_API_KEY}"
            response = requests.get(url)
            data = response.json()
            last_updated_iso = datetime.now().isoformat()
            market_data_cache[symbol] = TickerData(symbol=symbol, overview=data, last_updated=last_updated_iso)
        return market_data_cache[symbol]