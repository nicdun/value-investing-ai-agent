import requests
from mcp_server import mcp
from urllib.parse import quote_plus
from features.fundamental_data.alphavantage_adapter import AlphaVantageAPI
from features.fundamental_data.model import FundamentalData
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
def get_ticker_overview(symbol: str) -> FundamentalData:
    """Get the overview of a stock ticket symbol via alphavantage API"""
    return AlphaVantageAPI.get_ticker_overview(symbol)


@mcp.tool()
def get_stock_ticker(search_string: str) -> str:
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


@mcp.tool()
def get_ticker_balance_sheet(symbol: str) -> FundamentalData:
    """Get the balance sheet of a stock ticket symbol via alphavantage API"""
    return AlphaVantageAPI.get_balance_sheet(symbol)


@mcp.tool()
def get_ticker_cash_flow(symbol: str) -> FundamentalData:
    """Get the cash flow of a stock ticket symbol via alphavantage API"""
    return AlphaVantageAPI.get_cash_flow(symbol)


@mcp.tool()
def get_ticker_income_statement(symbol: str) -> FundamentalData:
    """Get the income statement of a stock ticket symbol via alphavantage API"""
    return AlphaVantageAPI.get_income_statement(symbol)
