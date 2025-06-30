import requests
from server import mcp
from urllib.parse import quote_plus
from features.alphavantage.api import AlphaVantageAPI, TickerData
from config.env import ALPHAVANTAGE_API_KEY


@mcp.tool()
def get_stock_price(symbol: str) -> float:
    """Get the price of a stock ticket symbol via alphavantage API"""
    print(f"Getting stock price for {symbol}")
    url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={ALPHAVANTAGE_API_KEY}"
    response = requests.get(url)
    data = response.json()
    return data


@mcp.tool()
def get_ticker_overview(symbol: str) -> TickerData:
    """Get the overview of a stock ticket symbol via alphavantage API"""
    return AlphaVantageAPI.get_ticker_overview(symbol)

@mcp.tool()
def get_stock_sticker(search_string: str) -> str:
    """Get the stock ticker symbol for a given search string via alphavantage API"""
    print(f"Getting stock ticker symbol for {search_string}")

    search_string = quote_plus(search_string)
    url = f"https://www.alphavantage.co/query?function=SYMBOL_SEARCH&keywords={search_string}&apikey={ALPHAVANTAGE_API_KEY}"
    response = requests.get(url)
    data = response.json()

    if data["bestMatches"]:
        return data["bestMatches"][0]["1. symbol"]
    else:
        return "No stock ticker symbol found"