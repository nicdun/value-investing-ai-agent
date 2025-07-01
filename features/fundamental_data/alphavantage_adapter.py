
from datetime import datetime
import requests
from config.env import ALPHAVANTAGE_API_KEY
from .model import FundamentalData

market_data_cache: dict[str, FundamentalData] = {}

class AlphaVantageAPI:

    @staticmethod
    def get_ticker_symbol(stock_name: str) -> str:
        url = f"https://www.alphavantage.co/query?function=SYMBOL_SEARCH&keywords={stock_name}&apikey={ALPHAVANTAGE_API_KEY}"
        response = requests.get(url)
        data = response.json()
        return data["bestMatches"]
    
    @staticmethod
    def get_ticker_overview(symbol: str) -> FundamentalData:
        if symbol not in market_data_cache or market_data_cache[symbol].overview is None:
            print(f"Getting stock price for {symbol}")
            url = f"https://www.alphavantage.co/query?function=OVERVIEW&symbol={symbol}&apikey={ALPHAVANTAGE_API_KEY}"
            response = requests.get(url)
            data = response.json()
            last_updated_iso = datetime.now().isoformat()
            market_data_cache[symbol] = FundamentalData(
                symbol=symbol,
                overview=data,
                last_updated=last_updated_iso
            )
        return market_data_cache[symbol]

    @staticmethod
    def get_balance_sheet(symbol: str) -> list[dict]:
        if symbol not in market_data_cache or market_data_cache[symbol].balance_sheet is None:
            print(f"Getting balance sheet for {symbol}")
            url = f"https://www.alphavantage.co/query?function=BALANCE_SHEET&symbol={symbol}&apikey={ALPHAVANTAGE_API_KEY}"
            response = requests.get(url)
            data = response.json()
            return data
        return market_data_cache[symbol].balance_sheet
    
    @staticmethod
    def get_cash_flow(symbol: str) -> list[dict]:
        if symbol not in market_data_cache or market_data_cache[symbol].cash_flow is None:
            print(f"Getting cash flow for {symbol}")
            url = f"https://www.alphavantage.co/query?function=CASH_FLOW&symbol={symbol}&apikey={ALPHAVANTAGE_API_KEY}"
            response = requests.get(url)
            data = response.json()
            return data
        return market_data_cache[symbol].cash_flow
    
    @staticmethod
    def get_income_statement(symbol: str) -> list[dict]:
        if symbol not in market_data_cache or market_data_cache[symbol].income_statement is None:
            print(f"Getting income statement for {symbol}")
            url = f"https://www.alphavantage.co/query?function=INCOME_STATEMENT&symbol={symbol}&apikey={ALPHAVANTAGE_API_KEY}"
            response = requests.get(url)
            data = response.json()
            return data
        return market_data_cache[symbol].income_statement