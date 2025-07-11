from datetime import datetime
import requests
from config.env import ALPHAVANTAGE_API_KEY
from .model import (
    FundamentalData,
    StockMetaData,
    BalanceSheetReport,
    CashFlowReport,
    IncomeStatementReport,
)
from .cache import get_cache

# Get the cache instance
cache = get_cache()


class AlphaVantageAPI:
    @staticmethod
    def get_ticker_symbol(stock_name: str) -> str:
        """Search for ticker symbol by company name."""
        url = f"https://www.alphavantage.co/query?function=SYMBOL_SEARCH&keywords={stock_name}&apikey={ALPHAVANTAGE_API_KEY}"
        response = requests.get(url)
        data = response.json()
        return data["bestMatches"]

    @staticmethod
    def get_ticker_overview(symbol: str) -> StockMetaData:
        """Get company overview data with caching."""

        overview = cache.get_overview(symbol)
        if overview:
            return overview

        print(f"Getting stock overview for {symbol}")
        try:
            url = f"https://www.alphavantage.co/query?function=OVERVIEW&symbol={symbol}&apikey={ALPHAVANTAGE_API_KEY}"
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()

            # Transform API response to StockMetaData model
            overview = StockMetaData(**data)

            # Cache the overview data
            cache.set_overview(symbol, overview)

            return overview

        except Exception as e:
            print(f"Error fetching overview for {symbol}: {e}")
            return None

    @staticmethod
    def get_balance_sheet(symbol: str) -> list[BalanceSheetReport]:
        """Get balance sheet data with caching."""
        # Check cache first
        cached_data = cache.get_balance_sheet(symbol)
        if cached_data:
            return cached_data

        print(f"Getting balance sheet for {symbol}")
        try:
            url = f"https://www.alphavantage.co/query?function=BALANCE_SHEET&symbol={symbol}&apikey={ALPHAVANTAGE_API_KEY}"
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()

            # Transform API response to BalanceSheetReport models
            balance_sheet_reports = []

            # Process annual reports
            if "annualReports" in data:
                for report in data["annualReports"]:
                    balance_sheet_reports.append(BalanceSheetReport(**report))

            # Process quarterly reports
            if "quarterlyReports" in data:
                for report in data["quarterlyReports"]:
                    balance_sheet_reports.append(BalanceSheetReport(**report))

            # Cache the data
            cache.set_balance_sheet(symbol, balance_sheet_reports)

            return balance_sheet_reports

        except Exception as e:
            print(f"Error fetching balance sheet for {symbol}: {e}")
            return []

    @staticmethod
    def get_cash_flow(symbol: str) -> list[CashFlowReport]:
        """Get cash flow data with caching."""
        # Check cache first
        cached_data = cache.get_cash_flow(symbol)
        if cached_data:
            return cached_data

        print(f"Getting cash flow for {symbol}")
        try:
            url = f"https://www.alphavantage.co/query?function=CASH_FLOW&symbol={symbol}&apikey={ALPHAVANTAGE_API_KEY}"
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()

            # Transform API response to CashFlowReport models
            cash_flow_reports = []

            # Process annual reports
            if "annualReports" in data:
                for report in data["annualReports"]:
                    cash_flow_reports.append(CashFlowReport(**report))

            # Process quarterly reports
            if "quarterlyReports" in data:
                for report in data["quarterlyReports"]:
                    cash_flow_reports.append(CashFlowReport(**report))

            # Cache the data
            cache.set_cash_flow(symbol, cash_flow_reports)

            return cash_flow_reports

        except Exception as e:
            print(f"Error fetching cash flow for {symbol}: {e}")
            return []

    @staticmethod
    def get_income_statement(symbol: str) -> list[IncomeStatementReport]:
        """Get income statement data with caching."""
        # Check cache first
        cached_data = cache.get_income_statement(symbol)
        if cached_data:
            return cached_data

        print(f"Getting income statement for {symbol}")
        try:
            url = f"https://www.alphavantage.co/query?function=INCOME_STATEMENT&symbol={symbol}&apikey={ALPHAVANTAGE_API_KEY}"
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()

            # Transform API response to IncomeStatementReport models
            income_statement_reports = []

            # Process annual reports
            if "annualReports" in data:
                for report in data["annualReports"]:
                    income_statement_reports.append(IncomeStatementReport(**report))

            # Process quarterly reports
            if "quarterlyReports" in data:
                for report in data["quarterlyReports"]:
                    income_statement_reports.append(IncomeStatementReport(**report))

            # Cache the data
            cache.set_income_statement(symbol, income_statement_reports)

            return income_statement_reports

        except Exception as e:
            print(f"Error fetching income statement for {symbol}: {e}")
            return []

    @staticmethod
    def get_comprehensive_data(symbol: str) -> FundamentalData:
        """Get all available data for a symbol, checking cache first, then fetching from API if not cached."""
        # Overview
        overview = cache.get_overview(symbol)
        if not overview:
            overview = AlphaVantageAPI.get_ticker_overview(symbol)

        # Balance Sheet
        balance_sheet = cache.get_balance_sheet(symbol)
        if not balance_sheet:
            balance_sheet = AlphaVantageAPI.get_balance_sheet(symbol)

        # Cash Flow
        cash_flow = cache.get_cash_flow(symbol)
        if not cash_flow:
            cash_flow = AlphaVantageAPI.get_cash_flow(symbol)

        # Income Statement
        income_statement = cache.get_income_statement(symbol)
        if not income_statement:
            income_statement = AlphaVantageAPI.get_income_statement(symbol)

        # Calculated Metrics (assume only in cache)
        calculated_metrics = cache.get_calculated_metrics(symbol)

        return FundamentalData(
            symbol=symbol,
            overview=overview,
            balance_sheet=balance_sheet,
            cash_flow=cash_flow,
            income_statement=income_statement,
            calculated_metrics=calculated_metrics,
            last_updated=datetime.now().isoformat(),
        )

    @staticmethod
    def clear_cache(symbol: str | None = None):
        """Clear cache for a specific symbol or all symbols."""
        cache.clear_cache(symbol)

    @staticmethod
    def get_cached_symbols() -> list[str]:
        """Get list of all cached symbols."""
        return cache.get_cached_symbols()

    @staticmethod
    def has_cached_data(symbol: str, data_type: str) -> bool:
        """Check if specific data type is cached for a symbol."""
        return cache.has_cached_data(symbol, data_type)
