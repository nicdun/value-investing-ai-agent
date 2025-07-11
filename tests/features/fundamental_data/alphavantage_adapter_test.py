import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime
import requests

from features.fundamental_data.alphavantage_adapter import AlphaVantageAPI
from features.fundamental_data.model import (
    FundamentalData,
    StockMetaData,
    BalanceSheetReport,
    CashFlowReport,
    IncomeStatementReport,
)


class TestAlphaVantageAPI:
    """Test suite for AlphaVantageAPI class."""

    @pytest.fixture
    def clean_cache(self):
        """Clear cache before and after each test."""
        AlphaVantageAPI.clear_cache()
        yield
        AlphaVantageAPI.clear_cache()

    @pytest.fixture
    def mock_overview_response(self):
        """Mock API response for ticker overview."""
        return {
            "Symbol": "AAPL",
            "AssetType": "Common Stock",
            "Name": "Apple Inc",
            "Description": "Apple Inc. is an American multinational technology company.",
            "CIK": "320193",
            "Exchange": "NASDAQ",
            "Currency": "USD",
            "Country": "USA",
            "Sector": "TECHNOLOGY",
            "Industry": "ELECTRONIC COMPUTERS",
            "Address": "ONE INFINITE LOOP, CUPERTINO, CA, US",
            "OfficialSite": "https://www.apple.com",
            "FiscalYearEnd": "September",
            "LatestQuarter": "2024-03-31",
            "MarketCapitalization": "3000000000000",
            "EBITDA": "130000000000",
            "PERatio": "28.5",
            "PEGRatio": "1.5",
            "BookValue": "4.0",
            "DividendPerShare": "0.95",
            "DividendYield": "0.0045",
            "EPS": "6.0",
            "RevenuePerShareTTM": "250.0",
            "ProfitMargin": "0.25",
            "OperatingMarginTTM": "0.30",
            "ReturnOnAssetsTTM": "0.20",
            "ReturnOnEquityTTM": "0.75",
            "RevenueTTM": "383000000000",
            "GrossProfitTTM": "170000000000",
            "DilutedEPSTTM": "6.0",
            "QuarterlyEarningsGrowthYOY": "0.05",
            "QuarterlyRevenueGrowthYOY": "0.02",
            "AnalystTargetPrice": "200.0",
            "AnalystRatingStrongBuy": "5",
            "AnalystRatingBuy": "15",
            "AnalystRatingHold": "5",
            "AnalystRatingSell": "1",
            "AnalystRatingStrongSell": "0",
            "TrailingPE": "28.5",
            "ForwardPE": "25.0",
            "PriceToSalesRatioTTM": "7.8",
            "PriceToBookRatio": "45.0",
            "EVToRevenue": "7.5",
            "EVToEBITDA": "23.0",
            "Beta": "1.2",
            "52WeekHigh": "200.0",
            "52WeekLow": "150.0",
            "50DayMovingAverage": "180.0",
            "200DayMovingAverage": "175.0",
            "SharesOutstanding": "15500000000",
            "SharesFloat": "15400000000",
            "PercentInsiders": "0.07",
            "PercentInstitutions": "61.0",
            "DividendDate": "2024-08-15",
            "ExDividendDate": "2024-08-09",
        }

    @pytest.fixture
    def mock_balance_sheet_response(self):
        """Mock API response for balance sheet."""
        return {
            "symbol": "AAPL",
            "annualReports": [
                {
                    "fiscalDateEnding": "2023-09-30",
                    "reportedCurrency": "USD",
                    "totalAssets": "352755000000",
                    "totalCurrentAssets": "143566000000",
                    "cashAndCashEquivalentsAtCarryingValue": "29965000000",
                    "totalLiabilities": "290437000000",
                    "totalShareholderEquity": "62146000000",
                }
            ],
            "quarterlyReports": [
                {
                    "fiscalDateEnding": "2024-03-31",
                    "reportedCurrency": "USD",
                    "totalAssets": "365725000000",
                    "totalCurrentAssets": "135405000000",
                    "cashAndCashEquivalentsAtCarryingValue": "25770000000",
                }
            ],
        }

    @pytest.fixture
    def mock_cash_flow_response(self):
        """Mock API response for cash flow."""
        return {
            "symbol": "AAPL",
            "annualReports": [
                {
                    "fiscalDateEnding": "2023-09-30",
                    "reportedCurrency": "USD",
                    "operatingCashflow": "110543000000",
                    "cashflowFromInvestment": "-3705000000",
                    "cashflowFromFinancing": "-108488000000",
                }
            ],
            "quarterlyReports": [
                {
                    "fiscalDateEnding": "2024-03-31",
                    "reportedCurrency": "USD",
                    "operatingCashflow": "28168000000",
                    "cashflowFromInvestment": "-3705000000",
                }
            ],
        }

    @pytest.fixture
    def mock_income_statement_response(self):
        """Mock API response for income statement."""
        return {
            "symbol": "AAPL",
            "annualReports": [
                {
                    "fiscalDateEnding": "2023-09-30",
                    "reportedCurrency": "USD",
                    "totalRevenue": "383285000000",
                    "grossProfit": "169148000000",
                    "operatingIncome": "114301000000",
                    "netIncome": "96995000000",
                }
            ],
            "quarterlyReports": [
                {
                    "fiscalDateEnding": "2024-03-31",
                    "reportedCurrency": "USD",
                    "totalRevenue": "90753000000",
                    "grossProfit": "41863000000",
                    "netIncome": "23636000000",
                }
            ],
        }

    @pytest.fixture
    def mock_symbol_search_response(self):
        """Mock API response for symbol search."""
        return {
            "bestMatches": [
                {
                    "1. symbol": "AAPL",
                    "2. name": "Apple Inc",
                    "3. type": "Equity",
                    "4. region": "United States",
                    "5. marketOpen": "09:30",
                    "6. marketClose": "16:00",
                    "7. timezone": "UTC-04",
                    "8. currency": "USD",
                    "9. matchScore": "1.0000",
                }
            ]
        }

    # Test get_ticker_symbol
    def test_get_ticker_symbol_success(self, mock_symbol_search_response):
        """Test successful ticker symbol search."""
        with patch(
            "features.fundamental_data.alphavantage_adapter.requests.get"
        ) as mock_get:
            mock_get.return_value.json.return_value = mock_symbol_search_response

            result = AlphaVantageAPI.get_ticker_symbol("Apple")

            assert result == mock_symbol_search_response["bestMatches"]
            mock_get.assert_called_once()
            assert "SYMBOL_SEARCH" in mock_get.call_args[0][0]
            assert "keywords=Apple" in mock_get.call_args[0][0]

    # Test get_ticker_overview
    def test_get_ticker_overview_success(self, clean_cache, mock_overview_response):
        """Test successful ticker overview retrieval."""
        with patch(
            "features.fundamental_data.alphavantage_adapter.requests.get"
        ) as mock_get:
            mock_get.return_value.json.return_value = mock_overview_response
            mock_get.return_value.raise_for_status.return_value = None

            result = AlphaVantageAPI.get_ticker_overview("AAPL")

            # The method actually returns a StockMetaData, not FundamentalData
            assert isinstance(result, StockMetaData)
            assert result.symbol == "AAPL"
            assert result.name == "Apple Inc"
            assert result.market_capitalization == "3000000000000"
            mock_get.assert_called_once()
            assert "OVERVIEW" in mock_get.call_args[0][0]

    def test_get_ticker_overview_uses_cache(self, clean_cache, mock_overview_response):
        """Test that ticker overview uses cache on second call."""
        with patch(
            "features.fundamental_data.alphavantage_adapter.requests.get"
        ) as mock_get:
            mock_get.return_value.json.return_value = mock_overview_response
            mock_get.return_value.raise_for_status.return_value = None

            # First call - should hit API
            result1 = AlphaVantageAPI.get_ticker_overview("AAPL")

            # Second call - should use cache
            result2 = AlphaVantageAPI.get_ticker_overview("AAPL")

            # API should only be called once
            assert mock_get.call_count == 1
            assert result1.symbol == result2.symbol
            assert result1.name == result2.name

    def test_get_ticker_overview_api_error(self, clean_cache):
        """Test ticker overview handles API errors gracefully."""
        with patch(
            "features.fundamental_data.alphavantage_adapter.requests.get"
        ) as mock_get:
            mock_get.side_effect = requests.RequestException("API Error")

            result = AlphaVantageAPI.get_ticker_overview("INVALID")

            # Returns None on error
            assert result is None

    # Test get_balance_sheet
    def test_get_balance_sheet_success(self, clean_cache, mock_balance_sheet_response):
        """Test successful balance sheet retrieval."""
        with patch(
            "features.fundamental_data.alphavantage_adapter.requests.get"
        ) as mock_get:
            mock_get.return_value.json.return_value = mock_balance_sheet_response
            mock_get.return_value.raise_for_status.return_value = None

            result = AlphaVantageAPI.get_balance_sheet("AAPL")

            assert isinstance(result, list)
            assert len(result) == 2  # 1 annual + 1 quarterly
            assert all(isinstance(report, BalanceSheetReport) for report in result)
            assert result[0].fiscal_date_ending == "2023-09-30"
            assert result[0].total_assets == "352755000000"
            mock_get.assert_called_once()
            assert "BALANCE_SHEET" in mock_get.call_args[0][0]

    def test_get_balance_sheet_uses_cache(
        self, clean_cache, mock_balance_sheet_response
    ):
        """Test that balance sheet uses cache on second call."""
        with patch(
            "features.fundamental_data.alphavantage_adapter.requests.get"
        ) as mock_get:
            mock_get.return_value.json.return_value = mock_balance_sheet_response
            mock_get.return_value.raise_for_status.return_value = None

            # First call - should hit API
            result1 = AlphaVantageAPI.get_balance_sheet("AAPL")

            # Second call - should use cache
            result2 = AlphaVantageAPI.get_balance_sheet("AAPL")

            # API should only be called once
            assert mock_get.call_count == 1
            assert len(result1) == len(result2)
            assert result1[0].fiscal_date_ending == result2[0].fiscal_date_ending

    def test_get_balance_sheet_api_error(self, clean_cache):
        """Test balance sheet handles API errors gracefully."""
        with patch(
            "features.fundamental_data.alphavantage_adapter.requests.get"
        ) as mock_get:
            mock_get.side_effect = requests.RequestException("API Error")

            result = AlphaVantageAPI.get_balance_sheet("INVALID")

            assert isinstance(result, list)
            assert len(result) == 0

    # Test get_cash_flow
    def test_get_cash_flow_success(self, clean_cache, mock_cash_flow_response):
        """Test successful cash flow retrieval."""
        with patch(
            "features.fundamental_data.alphavantage_adapter.requests.get"
        ) as mock_get:
            mock_get.return_value.json.return_value = mock_cash_flow_response
            mock_get.return_value.raise_for_status.return_value = None

            result = AlphaVantageAPI.get_cash_flow("AAPL")

            assert isinstance(result, list)
            assert len(result) == 2  # 1 annual + 1 quarterly
            assert all(isinstance(report, CashFlowReport) for report in result)
            assert result[0].fiscal_date_ending == "2023-09-30"
            assert result[0].operating_cashflow == "110543000000"
            mock_get.assert_called_once()
            assert "CASH_FLOW" in mock_get.call_args[0][0]

    def test_get_cash_flow_uses_cache(self, clean_cache, mock_cash_flow_response):
        """Test that cash flow uses cache on second call."""
        with patch(
            "features.fundamental_data.alphavantage_adapter.requests.get"
        ) as mock_get:
            mock_get.return_value.json.return_value = mock_cash_flow_response
            mock_get.return_value.raise_for_status.return_value = None

            # First call - should hit API
            result1 = AlphaVantageAPI.get_cash_flow("AAPL")

            # Second call - should use cache
            result2 = AlphaVantageAPI.get_cash_flow("AAPL")

            # API should only be called once
            assert mock_get.call_count == 1
            assert len(result1) == len(result2)
            assert result1[0].operating_cashflow == result2[0].operating_cashflow

    # Test get_income_statement
    def test_get_income_statement_success(
        self, clean_cache, mock_income_statement_response
    ):
        """Test successful income statement retrieval."""
        with patch(
            "features.fundamental_data.alphavantage_adapter.requests.get"
        ) as mock_get:
            mock_get.return_value.json.return_value = mock_income_statement_response
            mock_get.return_value.raise_for_status.return_value = None

            result = AlphaVantageAPI.get_income_statement("AAPL")

            assert isinstance(result, list)
            assert len(result) == 2  # 1 annual + 1 quarterly
            assert all(isinstance(report, IncomeStatementReport) for report in result)
            assert result[0].fiscal_date_ending == "2023-09-30"
            assert result[0].total_revenue == "383285000000"
            mock_get.assert_called_once()
            assert "INCOME_STATEMENT" in mock_get.call_args[0][0]

    def test_get_income_statement_uses_cache(
        self, clean_cache, mock_income_statement_response
    ):
        """Test that income statement uses cache on second call."""
        with patch(
            "features.fundamental_data.alphavantage_adapter.requests.get"
        ) as mock_get:
            mock_get.return_value.json.return_value = mock_income_statement_response
            mock_get.return_value.raise_for_status.return_value = None

            # First call - should hit API
            result1 = AlphaVantageAPI.get_income_statement("AAPL")

            # Second call - should use cache
            result2 = AlphaVantageAPI.get_income_statement("AAPL")

            # API should only be called once
            assert mock_get.call_count == 1
            assert len(result1) == len(result2)
            assert result1[0].total_revenue == result2[0].total_revenue

    # Test get_comprehensive_data
    def test_get_comprehensive_data_success(
        self,
        clean_cache,
        mock_overview_response,
        mock_balance_sheet_response,
        mock_cash_flow_response,
        mock_income_statement_response,
    ):
        """Test successful comprehensive data retrieval."""
        with patch(
            "features.fundamental_data.alphavantage_adapter.requests.get"
        ) as mock_get:
            # Mock responses for different endpoints
            def side_effect(url):
                mock_response = MagicMock()
                mock_response.raise_for_status.return_value = None

                if "OVERVIEW" in url:
                    mock_response.json.return_value = mock_overview_response
                elif "BALANCE_SHEET" in url:
                    mock_response.json.return_value = mock_balance_sheet_response
                elif "CASH_FLOW" in url:
                    mock_response.json.return_value = mock_cash_flow_response
                elif "INCOME_STATEMENT" in url:
                    mock_response.json.return_value = mock_income_statement_response

                return mock_response

            mock_get.side_effect = side_effect

            result = AlphaVantageAPI.get_comprehensive_data("AAPL")

            assert isinstance(result, FundamentalData)
            assert result.symbol == "AAPL"
            assert result.overview.name == "Apple Inc"
            assert len(result.balance_sheet) == 2
            assert len(result.cash_flow) == 2
            assert len(result.income_statement) == 2
            assert result.last_updated is not None

            # Should call API 4 times (overview, balance sheet, cash flow, income statement)
            assert mock_get.call_count == 4

    def test_get_comprehensive_data_uses_cache(
        self, clean_cache, mock_overview_response
    ):
        """Test that comprehensive data uses cache when available."""
        with patch(
            "features.fundamental_data.alphavantage_adapter.requests.get"
        ) as mock_get:
            mock_get.return_value.json.return_value = mock_overview_response
            mock_get.return_value.raise_for_status.return_value = None

            # First call - populate cache
            result1 = AlphaVantageAPI.get_comprehensive_data("AAPL")

            # Second call - should use cache
            result2 = AlphaVantageAPI.get_comprehensive_data("AAPL")

            # Should only hit API once for overview (other data types would be empty)
            assert result1.symbol == result2.symbol
            assert result1.overview.name == result2.overview.name

    # Test cache management methods
    def test_clear_cache_all(self, clean_cache):
        """Test clearing all cache."""
        # Add some data to cache first
        with patch(
            "features.fundamental_data.alphavantage_adapter.requests.get"
        ) as mock_get:
            mock_get.return_value.json.return_value = {
                "Symbol": "AAPL",
                "Name": "Apple Inc",
            }
            mock_get.return_value.raise_for_status.return_value = None

            AlphaVantageAPI.get_ticker_overview("AAPL")

            # Verify cache has data
            assert AlphaVantageAPI.has_cached_data("AAPL", "overview")

            # Clear all cache
            AlphaVantageAPI.clear_cache()

            # Verify cache is empty
            assert not AlphaVantageAPI.has_cached_data("AAPL", "overview")

    def test_clear_cache_specific_symbol(self, clean_cache):
        """Test clearing cache for specific symbol."""
        with patch(
            "features.fundamental_data.alphavantage_adapter.requests.get"
        ) as mock_get:
            mock_get.return_value.json.return_value = {
                "Symbol": "AAPL",
                "Name": "Apple Inc",
            }
            mock_get.return_value.raise_for_status.return_value = None

            AlphaVantageAPI.get_ticker_overview("AAPL")

            mock_get.return_value.json.return_value = {
                "Symbol": "GOOGL",
                "Name": "Alphabet Inc",
            }
            AlphaVantageAPI.get_ticker_overview("GOOGL")

            # Verify both symbols are cached
            assert AlphaVantageAPI.has_cached_data("AAPL", "overview")
            assert AlphaVantageAPI.has_cached_data("GOOGL", "overview")

            # Clear cache for AAPL only
            AlphaVantageAPI.clear_cache("AAPL")

            # Verify only AAPL is cleared
            assert not AlphaVantageAPI.has_cached_data("AAPL", "overview")
            assert AlphaVantageAPI.has_cached_data("GOOGL", "overview")

    def test_get_cached_symbols(self, clean_cache):
        """Test getting list of cached symbols."""
        with patch(
            "features.fundamental_data.alphavantage_adapter.requests.get"
        ) as mock_get:
            mock_get.return_value.raise_for_status.return_value = None

            # Add multiple symbols to cache
            mock_get.return_value.json.return_value = {
                "Symbol": "AAPL",
                "Name": "Apple Inc",
            }
            AlphaVantageAPI.get_ticker_overview("AAPL")

            mock_get.return_value.json.return_value = {
                "Symbol": "GOOGL",
                "Name": "Alphabet Inc",
            }
            AlphaVantageAPI.get_ticker_overview("GOOGL")

            cached_symbols = AlphaVantageAPI.get_cached_symbols()

            assert "AAPL" in cached_symbols
            assert "GOOGL" in cached_symbols
            assert len(cached_symbols) >= 2

    def test_has_cached_data(self, clean_cache):
        """Test checking if data is cached."""
        # Initially no cache
        assert not AlphaVantageAPI.has_cached_data("AAPL", "overview")

        with patch(
            "features.fundamental_data.alphavantage_adapter.requests.get"
        ) as mock_get:
            mock_get.return_value.json.return_value = {
                "Symbol": "AAPL",
                "Name": "Apple Inc",
            }
            mock_get.return_value.raise_for_status.return_value = None

            AlphaVantageAPI.get_ticker_overview("AAPL")

            # Now should have cache
            assert AlphaVantageAPI.has_cached_data("AAPL", "overview")
            assert not AlphaVantageAPI.has_cached_data("AAPL", "balance_sheet")

    # Parametrized tests
    @pytest.mark.parametrize(
        "symbol,expected_calls",
        [
            ("AAPL", 1),
            ("GOOGL", 1),
            ("MSFT", 1),
        ],
    )
    def test_multiple_symbols_cached_separately(
        self, clean_cache, symbol, expected_calls
    ):
        """Test that different symbols are cached separately."""
        with patch(
            "features.fundamental_data.alphavantage_adapter.requests.get"
        ) as mock_get:
            mock_get.return_value.json.return_value = {
                "Symbol": symbol,
                "Name": f"{symbol} Inc",
            }
            mock_get.return_value.raise_for_status.return_value = None

            # First call for this symbol
            AlphaVantageAPI.get_ticker_overview(symbol)

            # Second call should use cache
            AlphaVantageAPI.get_ticker_overview(symbol)

            # Should only call API once per symbol
            assert mock_get.call_count == expected_calls

    @pytest.mark.parametrize(
        "data_type,method_name",
        [
            ("overview", "get_ticker_overview"),
            ("balance_sheet", "get_balance_sheet"),
            ("cash_flow", "get_cash_flow"),
            ("income_statement", "get_income_statement"),
        ],
    )
    def test_cache_behavior_for_different_data_types(
        self, clean_cache, data_type, method_name
    ):
        """Test that caching works for all data types."""
        with patch(
            "features.fundamental_data.alphavantage_adapter.requests.get"
        ) as mock_get:
            # Mock appropriate response based on data type
            if data_type == "overview":
                mock_response = {"Symbol": "AAPL", "Name": "Apple Inc"}
            else:
                mock_response = {
                    "symbol": "AAPL",
                    "annualReports": [
                        {"fiscalDateEnding": "2023-09-30", "reportedCurrency": "USD"}
                    ],
                }

            mock_get.return_value.json.return_value = mock_response
            mock_get.return_value.raise_for_status.return_value = None

            # Get method and call it
            method = getattr(AlphaVantageAPI, method_name)

            # First call
            result1 = method("AAPL")

            # Second call should use cache
            result2 = method("AAPL")

            # API should only be called once
            assert mock_get.call_count == 1

            # Results should be the same
            if data_type == "overview":
                assert result1.symbol == result2.symbol
            else:
                assert len(result1) == len(result2)
