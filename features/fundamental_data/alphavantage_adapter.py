from datetime import datetime
import requests
from config.env import ALPHAVANTAGE_API_KEY
from .model import (
    FundamentalData,
    StockMetaData,
    BalanceSheetReport,
    CashFlowReport,
    IncomeStatementReport,
    CalculatedMetrics,
)
from .cache import get_cache

# Get the cache instance
cache = get_cache()

# Initialize with some default data
cache.set_overview(
    "AAPL",
    StockMetaData(
        symbol="AAPL",
        name="Apple Inc",
        description="Apple Inc. is an American multinational technology company that specializes in consumer electronics, computer software, and online services. Apple is the world's largest technology company by revenue (totalling $274.5 billion in 2020) and, since January 2021, the world's most valuable company. As of 2021, Apple is the world's fourth-largest PC vendor by unit sales, and fourth-largest smartphone manufacturer. It is one of the Big Five American information technology companies, along with Amazon, Google, Microsoft, and Facebook.",
        cik="320193",
        exchange="NASDAQ",
        currency="USD",
        country="USA",
        sector="TECHNOLOGY",
        industry="ELECTRONIC COMPUTERS",
        address="ONE INFINITE LOOP, CUPERTINO, CA, US",
        official_site="https://www.apple.com",
        fiscal_year_end="September",
        latest_quarter="2025-03-31",
        market_capitalization="3064377901000",
        ebitda="138866000000",
        pe_ratio="32.01",
        peg_ratio="1.871",
        book_value="4.471",
        dividend_per_share="1",
        dividend_yield="0.0052",
        eps="6.41",
        revenue_per_share_ttm="26.45",
        profit_margin="0.243",
        operating_margin_ttm="0.31",
        return_on_assets_ttm="0.238",
        return_on_equity_ttm="1.38",
        revenue_ttm="400366010000",
        gross_profit_ttm="186699006000",
        diluted_eps_ttm="6.41",
        quarterly_earnings_growth_yoy="0.078",
        quarterly_revenue_growth_yoy="0.051",
        analyst_target_price="228.6",
        analyst_rating_strong_buy="7",
        analyst_rating_buy="21",
        analyst_rating_hold="16",
        analyst_rating_sell="2",
        analyst_rating_strong_sell="1",
        trailing_pe="32.01",
        forward_pe="25.71",
        price_to_sales_ratio_ttm="7.65",
        price_to_book_ratio="45.88",
        ev_to_revenue="7.78",
        ev_to_ebitda="22.43",
        beta="1.211",
        week_52_high="259.47",
        week_52_low="168.99",
        day_50_moving_average="202.84",
        day_200_moving_average="223.26",
        shares_outstanding="14935800000",
        dividend_date="2025-05-15",
        ex_dividend_date="2025-05-12",
    ),
)

# Store the complete FundamentalData for AAPL
cache.set_fundamental_data(
    "AAPL",
    FundamentalData(
        symbol="AAPL",
        overview=cache.get_overview("AAPL"),
        last_updated=datetime.now().isoformat(),
    ),
)


class AlphaVantageAPI:
    @staticmethod
    def get_ticker_symbol(stock_name: str) -> str:
        """Search for ticker symbol by company name."""
        url = f"https://www.alphavantage.co/query?function=SYMBOL_SEARCH&keywords={stock_name}&apikey={ALPHAVANTAGE_API_KEY}"
        response = requests.get(url)
        data = response.json()
        return data["bestMatches"]

    @staticmethod
    def get_ticker_overview(symbol: str) -> FundamentalData:
        """Get company overview data with caching."""
        # Check if we have cached data
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
