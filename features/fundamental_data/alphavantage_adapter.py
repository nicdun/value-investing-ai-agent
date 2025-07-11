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


class DataResult:
    """Container for API results with source information."""

    def __init__(self, data, from_cache: bool, cache_timestamp: str = None):
        self.data = data
        self.from_cache = from_cache
        self.cache_timestamp = cache_timestamp
        self.source = "cache" if from_cache else "API"


class AlphaVantageAPI:
    @staticmethod
    def get_ticker_symbol(stock_name: str) -> DataResult:
        """Search for ticker symbol by company name with intelligent caching."""
        # Check cache first - search by symbol or company name
        cached_results = cache.search_symbols(stock_name)
        if cached_results:
            return DataResult(cached_results, from_cache=True)

        print(f"Searching for stock symbol: {stock_name}")
        try:
            url = f"https://www.alphavantage.co/query?function=SYMBOL_SEARCH&keywords={stock_name}&apikey={ALPHAVANTAGE_API_KEY}"
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()

            # Extract best matches
            best_matches = data.get("bestMatches", [])

            # Cache the individual symbol results for future intelligent matching
            if best_matches:
                cache.add_symbol_results(best_matches)

            return DataResult(best_matches, from_cache=False)

        except Exception as e:
            print(f"Error searching for symbol '{stock_name}': {e}")
            return DataResult([], from_cache=False)

    @staticmethod
    def get_ticker_overview(symbol: str) -> DataResult:
        """Get company overview data with caching."""
        # Check cache first
        overview = cache.get_overview(symbol)
        if overview:
            cache_info = cache.get_cache_info()
            cache_timestamp = (
                cache_info.get("overview", {})
                .get(symbol, {})
                .get("timestamp", "unknown")
            )
            return DataResult(
                overview, from_cache=True, cache_timestamp=cache_timestamp
            )

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

            return DataResult(overview, from_cache=False)

        except Exception as e:
            print(f"Error fetching overview for {symbol}: {e}")
            return DataResult(None, from_cache=False)

    @staticmethod
    def get_balance_sheet(symbol: str) -> DataResult:
        """Get balance sheet data with caching."""
        # Check cache first
        cached_data = cache.get_balance_sheet(symbol)
        if cached_data:
            cache_info = cache.get_cache_info()
            cache_timestamp = (
                cache_info.get("balance_sheet", {})
                .get(symbol, {})
                .get("timestamp", "unknown")
            )
            return DataResult(
                cached_data, from_cache=True, cache_timestamp=cache_timestamp
            )

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

            return DataResult(balance_sheet_reports, from_cache=False)

        except Exception as e:
            print(f"Error fetching balance sheet for {symbol}: {e}")
            return DataResult([], from_cache=False)

    @staticmethod
    def get_cash_flow(symbol: str) -> DataResult:
        """Get cash flow data with caching."""
        # Check cache first
        cached_data = cache.get_cash_flow(symbol)
        if cached_data:
            cache_info = cache.get_cache_info()
            cache_timestamp = (
                cache_info.get("cash_flow", {})
                .get(symbol, {})
                .get("timestamp", "unknown")
            )
            return DataResult(
                cached_data, from_cache=True, cache_timestamp=cache_timestamp
            )

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

            return DataResult(cash_flow_reports, from_cache=False)

        except Exception as e:
            print(f"Error fetching cash flow for {symbol}: {e}")
            return DataResult([], from_cache=False)

    @staticmethod
    def get_income_statement(symbol: str) -> DataResult:
        """Get income statement data with caching."""
        # Check cache first
        cached_data = cache.get_income_statement(symbol)
        if cached_data:
            cache_info = cache.get_cache_info()
            cache_timestamp = (
                cache_info.get("income_statement", {})
                .get(symbol, {})
                .get("timestamp", "unknown")
            )
            return DataResult(
                cached_data, from_cache=True, cache_timestamp=cache_timestamp
            )

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

            return DataResult(income_statement_reports, from_cache=False)

        except Exception as e:
            print(f"Error fetching income statement for {symbol}: {e}")
            return DataResult([], from_cache=False)

    @staticmethod
    def get_comprehensive_data(symbol: str) -> FundamentalData:
        """Get all available data for a symbol, checking cache first, then fetching from API if not cached."""
        # Overview
        overview_result = AlphaVantageAPI.get_ticker_overview(symbol)
        overview = overview_result.data

        # Balance Sheet
        balance_sheet_result = AlphaVantageAPI.get_balance_sheet(symbol)
        balance_sheet = balance_sheet_result.data

        # Cash Flow
        cash_flow_result = AlphaVantageAPI.get_cash_flow(symbol)
        cash_flow = cash_flow_result.data

        # Income Statement
        income_statement_result = AlphaVantageAPI.get_income_statement(symbol)
        income_statement = income_statement_result.data

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
