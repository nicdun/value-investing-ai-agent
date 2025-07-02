from datetime import datetime
import requests
from config.env import ALPHAVANTAGE_API_KEY
from .model import FundamentalData

market_data_cache: dict[str, FundamentalData] = {
    "AAPL": FundamentalData(
        symbol="AAPL",
        last_updated=datetime.now().isoformat(),
        overview={
            "Symbol": "AAPL",
            "AssetType": "Common Stock",
            "Name": "Apple Inc",
            "Description": "Apple Inc. is an American multinational technology company that specializes in consumer electronics, computer software, and online services. Apple is the world's largest technology company by revenue (totalling $274.5 billion in 2020) and, since January 2021, the world's most valuable company. As of 2021, Apple is the world's fourth-largest PC vendor by unit sales, and fourth-largest smartphone manufacturer. It is one of the Big Five American information technology companies, along with Amazon, Google, Microsoft, and Facebook.",
            "CIK": "320193",
            "Exchange": "NASDAQ",
            "Currency": "USD",
            "Country": "USA",
            "Sector": "TECHNOLOGY",
            "Industry": "ELECTRONIC COMPUTERS",
            "Address": "ONE INFINITE LOOP, CUPERTINO, CA, US",
            "OfficialSite": "https://www.apple.com",
            "FiscalYearEnd": "September",
            "LatestQuarter": "2025-03-31",
            "MarketCapitalization": "3064377901000",
            "EBITDA": "138866000000",
            "PERatio": "32.01",
            "PEGRatio": "1.871",
            "BookValue": "4.471",
            "DividendPerShare": "1",
            "DividendYield": "0.0052",
            "EPS": "6.41",
            "RevenuePerShareTTM": "26.45",
            "ProfitMargin": "0.243",
            "OperatingMarginTTM": "0.31",
            "ReturnOnAssetsTTM": "0.238",
            "ReturnOnEquityTTM": "1.38",
            "RevenueTTM": "400366010000",
            "GrossProfitTTM": "186699006000",
            "DilutedEPSTTM": "6.41",
            "QuarterlyEarningsGrowthYOY": "0.078",
            "QuarterlyRevenueGrowthYOY": "0.051",
            "AnalystTargetPrice": "228.6",
            "AnalystRatingStrongBuy": "7",
            "AnalystRatingBuy": "21",
            "AnalystRatingHold": "16",
            "AnalystRatingSell": "2",
            "AnalystRatingStrongSell": "1",
            "TrailingPE": "32.01",
            "ForwardPE": "25.71",
            "PriceToSalesRatioTTM": "7.65",
            "PriceToBookRatio": "45.88",
            "EVToRevenue": "7.78",
            "EVToEBITDA": "22.43",
            "Beta": "1.211",
            "52WeekHigh": "259.47",
            "52WeekLow": "168.99",
            "50DayMovingAverage": "202.84",
            "200DayMovingAverage": "223.26",
            "SharesOutstanding": "14935800000",
            "SharesFloat": "14911481000",
            "PercentInsiders": "2.085",
            "PercentInstitutions": "62.901",
            "DividendDate": "2025-05-15",
            "ExDividendDate": "2025-05-12",
        },
    )
}


class AlphaVantageAPI:
    @staticmethod
    def get_ticker_symbol(stock_name: str) -> str:
        url = f"https://www.alphavantage.co/query?function=SYMBOL_SEARCH&keywords={stock_name}&apikey={ALPHAVANTAGE_API_KEY}"
        response = requests.get(url)
        data = response.json()
        return data["bestMatches"]

    @staticmethod
    def get_ticker_overview(symbol: str) -> FundamentalData:
        if (
            symbol not in market_data_cache
            or market_data_cache[symbol].overview is None
        ):
            print(f"Getting stock price for {symbol}")
            url = f"https://www.alphavantage.co/query?function=OVERVIEW&symbol={symbol}&apikey={ALPHAVANTAGE_API_KEY}"
            response = requests.get(url)
            data = response.json()
            last_updated_iso = datetime.now().isoformat()
            market_data_cache[symbol] = FundamentalData(
                symbol=symbol, overview=data, last_updated=last_updated_iso
            )
        return market_data_cache[symbol]

    @staticmethod
    def get_balance_sheet(symbol: str) -> list[dict]:
        if (
            symbol not in market_data_cache
            or market_data_cache[symbol].balance_sheet is None
        ):
            print(f"Getting balance sheet for {symbol}")
            url = f"https://www.alphavantage.co/query?function=BALANCE_SHEET&symbol={symbol}&apikey={ALPHAVANTAGE_API_KEY}"
            response = requests.get(url)
            data = response.json()
            return data
        return market_data_cache[symbol].balance_sheet

    @staticmethod
    def get_cash_flow(symbol: str) -> list[dict]:
        if (
            symbol not in market_data_cache
            or market_data_cache[symbol].cash_flow is None
        ):
            print(f"Getting cash flow for {symbol}")
            url = f"https://www.alphavantage.co/query?function=CASH_FLOW&symbol={symbol}&apikey={ALPHAVANTAGE_API_KEY}"
            response = requests.get(url)
            data = response.json()
            return data
        return market_data_cache[symbol].cash_flow

    @staticmethod
    def get_income_statement(symbol: str) -> list[dict]:
        if (
            symbol not in market_data_cache
            or market_data_cache[symbol].income_statement is None
        ):
            print(f"Getting income statement for {symbol}")
            url = f"https://www.alphavantage.co/query?function=INCOME_STATEMENT&symbol={symbol}&apikey={ALPHAVANTAGE_API_KEY}"
            response = requests.get(url)
            data = response.json()
            return data
        return market_data_cache[symbol].income_statement
