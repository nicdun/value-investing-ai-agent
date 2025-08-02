import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any
from .model import (
    FundamentalData,
    StockMetaData,
    BalanceSheetReport,
    CashFlowReport,
    IncomeStatementReport,
    CalculatedMetrics,
)


class PersistentCache:
    """Persistent file-based cache for responses using strongly-typed models."""

    def __init__(self, cache_file_path: str = "cache/alpha_vantage_cache.json"):
        # Initialize cache dictionaries
        self._overview_cache: dict[str, StockMetaData] = {}
        self._balance_sheet_cache: dict[str, list[BalanceSheetReport]] = {}
        self._cash_flow_cache: dict[str, list[CashFlowReport]] = {}
        self._income_statement_cache: dict[str, list[IncomeStatementReport]] = {}
        self._calculated_metrics_cache: dict[str, list[CalculatedMetrics]] = {}
        self._exchange_rate_cache: dict[str, float] = {}
        self._symbol_search_cache: dict[str, dict] = {}  # symbol -> stock_data mapping

        # Set up cache file path
        self.cache_file_path = Path(cache_file_path)
        self.cache_file_path.parent.mkdir(parents=True, exist_ok=True)

        # Load existing cache data
        self._load_from_file()

    def _save_to_file(self):
        """Save current cache state to JSON file."""
        try:
            # Convert Pydantic models to dictionaries for JSON serialization
            cache_data = {
                "overview": {
                    symbol: data.model_dump() if data else None
                    for symbol, data in self._overview_cache.items()
                },
                "balance_sheet": {
                    symbol: [report.model_dump() for report in reports]
                    if reports
                    else []
                    for symbol, reports in self._balance_sheet_cache.items()
                },
                "cash_flow": {
                    symbol: [report.model_dump() for report in reports]
                    if reports
                    else []
                    for symbol, reports in self._cash_flow_cache.items()
                },
                "income_statement": {
                    symbol: [report.model_dump() for report in reports]
                    if reports
                    else []
                    for symbol, reports in self._income_statement_cache.items()
                },
                "calculated_metrics": {
                    symbol: [metric.model_dump() for metric in metrics]
                    if metrics
                    else []
                    for symbol, metrics in self._calculated_metrics_cache.items()
                },
                "symbol_search": {
                    symbol: stock_data
                    for symbol, stock_data in self._symbol_search_cache.items()
                },
                "exchange_rate": self._exchange_rate_cache,
                "last_updated": datetime.now().isoformat(),
                "version": "1.0",
            }

            # Write to temporary file first, then rename for atomic operation
            temp_file = self.cache_file_path.with_suffix(".tmp")
            with open(temp_file, "w", encoding="utf-8") as f:
                json.dump(cache_data, f, indent=2, ensure_ascii=False)

            # Atomic rename
            temp_file.replace(self.cache_file_path)

        except Exception as e:
            print(f"Warning: Failed to save cache to {self.cache_file_path}: {e}")

    def _load_from_file(self):
        """Load cache data from JSON file."""
        if not self.cache_file_path.exists():
            print(
                f"Cache file {self.cache_file_path} doesn't exist. Starting with empty cache."
            )
            return

        try:
            with open(self.cache_file_path, "r", encoding="utf-8") as f:
                cache_data = json.load(f)

            # Validate cache file structure
            if not isinstance(cache_data, dict) or "version" not in cache_data:
                print(f"Warning: Invalid cache file format. Starting with empty cache.")
                return

            # Load overview data
            if "overview" in cache_data:
                for symbol, data_dict in cache_data["overview"].items():
                    if data_dict:
                        try:
                            self._overview_cache[symbol] = StockMetaData(**data_dict)
                        except Exception as e:
                            print(
                                f"Warning: Failed to load overview data for {symbol}: {e}"
                            )

            # Load balance sheet data
            if "balance_sheet" in cache_data:
                for symbol, reports_list in cache_data["balance_sheet"].items():
                    if reports_list:
                        try:
                            self._balance_sheet_cache[symbol] = [
                                BalanceSheetReport(**report_dict)
                                for report_dict in reports_list
                            ]
                        except Exception as e:
                            print(
                                f"Warning: Failed to load balance sheet data for {symbol}: {e}"
                            )

            # Load cash flow data
            if "cash_flow" in cache_data:
                for symbol, reports_list in cache_data["cash_flow"].items():
                    if reports_list:
                        try:
                            self._cash_flow_cache[symbol] = [
                                CashFlowReport(**report_dict)
                                for report_dict in reports_list
                            ]
                        except Exception as e:
                            print(
                                f"Warning: Failed to load cash flow data for {symbol}: {e}"
                            )

            # Load income statement data
            if "income_statement" in cache_data:
                for symbol, reports_list in cache_data["income_statement"].items():
                    if reports_list:
                        try:
                            self._income_statement_cache[symbol] = [
                                IncomeStatementReport(**report_dict)
                                for report_dict in reports_list
                            ]
                        except Exception as e:
                            print(
                                f"Warning: Failed to load income statement data for {symbol}: {e}"
                            )

            # Load calculated metrics data
            if "calculated_metrics" in cache_data:
                for symbol, metrics_list in cache_data["calculated_metrics"].items():
                    if metrics_list:
                        try:
                            self._calculated_metrics_cache[symbol] = [
                                CalculatedMetrics(**metric_dict)
                                for metric_dict in metrics_list
                            ]
                        except Exception as e:
                            print(
                                f"Warning: Failed to load calculated metrics for {symbol}: {e}"
                            )

            # Load symbol search data
            if "symbol_search" in cache_data:
                for symbol, stock_data in cache_data["symbol_search"].items():
                    if stock_data:
                        try:
                            self._symbol_search_cache[symbol] = stock_data
                        except Exception as e:
                            print(
                                f"Warning: Failed to load symbol search data for '{symbol}': {e}"
                            )

            # Load exchange rate data
            if "exchange_rate" in cache_data:
                self._exchange_rate_cache = cache_data["exchange_rate"]

            # Print cache statistics
            total_symbols = len(self.get_cached_symbols())
            total_overview = len(self._overview_cache)
            total_balance_sheet = sum(
                len(reports) for reports in self._balance_sheet_cache.values()
            )
            total_cash_flow = sum(
                len(reports) for reports in self._cash_flow_cache.values()
            )
            total_income_statement = sum(
                len(reports) for reports in self._income_statement_cache.values()
            )
            total_symbol_searches = len(self._symbol_search_cache)
            total_exchange_rate = len(self._exchange_rate_cache)

            print(f"Loaded cache from {self.cache_file_path}:")
            print(f"  - {total_symbols} symbols")
            print(f"  - {total_overview} overview records")
            print(f"  - {total_balance_sheet} balance sheet reports")
            print(f"  - {total_cash_flow} cash flow reports")
            print(f"  - {total_income_statement} income statement reports")
            print(f"  - {total_symbol_searches} cached stock symbols for search")
            print(f"  - {total_exchange_rate} exchange rate records")

            if "last_updated" in cache_data:
                print(f"  - Last updated: {cache_data['last_updated']}")

        except Exception as e:
            print(f"Warning: Failed to load cache from {self.cache_file_path}: {e}")
            print("Starting with empty cache.")

    def _merge_financial_reports(
        self,
        existing: list[BalanceSheetReport | CashFlowReport | IncomeStatementReport]
        | None,
        new_data: list[BalanceSheetReport | CashFlowReport | IncomeStatementReport],
    ) -> list[BalanceSheetReport | CashFlowReport | IncomeStatementReport]:
        """Merge existing and new financial report data, avoiding duplicates based on fiscal_date_ending."""
        if not existing:
            return new_data

        # Create a set of existing fiscal dates for O(1) lookup
        existing_dates = {report.fiscal_date_ending for report in existing}

        # Only add reports that don't exist yet
        merged = existing.copy()
        merged.extend(
            [
                report
                for report in new_data
                if report.fiscal_date_ending not in existing_dates
            ]
        )
        return merged

    def _merge_calculated_metrics(
        self,
        existing: list[CalculatedMetrics] | None,
        new_data: list[CalculatedMetrics],
    ) -> list[CalculatedMetrics]:
        """Merge existing and new calculated metrics data, avoiding duplicates based on fiscal_date_ending."""
        if not existing:
            return new_data

        # Create a set of existing fiscal dates for O(1) lookup
        existing_dates = {metric.fiscal_date_ending for metric in existing}

        # Only add metrics that don't exist yet
        merged = existing.copy()
        merged.extend(
            [
                metric
                for metric in new_data
                if metric.fiscal_date_ending not in existing_dates
            ]
        )
        return merged

    # Overview/MetaData methods
    def get_overview(self, symbol: str) -> StockMetaData | None:
        """Get cached overview data if available."""
        return self._overview_cache.get(symbol)

    def set_overview(self, symbol: str, data: StockMetaData):
        """Cache overview data and save to file."""
        self._overview_cache[symbol] = data
        self._save_to_file()

    # Balance Sheet methods
    def get_balance_sheet(self, symbol: str) -> list[BalanceSheetReport] | None:
        """Get cached balance sheet data if available."""
        return self._balance_sheet_cache.get(symbol)

    def set_balance_sheet(self, symbol: str, data: list[BalanceSheetReport]):
        """Append new balance sheet data to cache and save to file."""
        self._balance_sheet_cache[symbol] = self._merge_financial_reports(
            self._balance_sheet_cache.get(symbol), data
        )
        self._save_to_file()

    # Cash Flow methods
    def get_cash_flow(self, symbol: str) -> list[CashFlowReport] | None:
        """Get cached cash flow data if available."""
        return self._cash_flow_cache.get(symbol)

    def set_cash_flow(self, symbol: str, data: list[CashFlowReport]):
        """Append new cash flow data to cache and save to file."""
        self._cash_flow_cache[symbol] = self._merge_financial_reports(
            self._cash_flow_cache.get(symbol), data
        )
        self._save_to_file()

    # Income Statement methods
    def get_income_statement(self, symbol: str) -> list[IncomeStatementReport] | None:
        """Get cached income statement data if available."""
        return self._income_statement_cache.get(symbol)

    def set_income_statement(self, symbol: str, data: list[IncomeStatementReport]):
        """Append new income statement data to cache and save to file."""
        self._income_statement_cache[symbol] = self._merge_financial_reports(
            self._income_statement_cache.get(symbol), data
        )
        self._save_to_file()

    # Calculated Metrics methods
    def get_calculated_metrics(self, symbol: str) -> list[CalculatedMetrics] | None:
        """Get cached calculated metrics if available."""
        return self._calculated_metrics_cache.get(symbol)

    def set_calculated_metrics(self, symbol: str, data: list[CalculatedMetrics]):
        """Append new calculated metrics to cache and save to file."""
        self._calculated_metrics_cache[symbol] = self._merge_calculated_metrics(
            self._calculated_metrics_cache.get(symbol), data
        )
        self._save_to_file()

    # Exchange Rate methods
    def get_exchange_rate(self, symbol: str) -> float | None:
        """Get cached exchange rate if available."""
        return self._exchange_rate_cache.get(symbol)

    def set_exchange_rate(self, symbol: str, exchange_rate: float):
        """Cache exchange rate and save to file."""
        self._exchange_rate_cache[symbol] = exchange_rate
        self._save_to_file()

    # Symbol Search methods
    def search_symbols(self, query: str) -> list[dict] | None:
        """
        Search for symbols in cache that match the query by symbol or company name.
        Returns matching results or None if no matches found.
        """
        if not self._symbol_search_cache:
            return None

        query_lower = query.lower().strip()
        matches = []

        for symbol, stock_data in self._symbol_search_cache.items():
            # Check if query matches symbol (case-insensitive)
            if query_lower == symbol.lower():
                matches.append(stock_data)
                continue

            # Check if query matches company name (case-insensitive, partial match)
            company_name = stock_data.get("2. name", "").lower()
            if company_name and (
                query_lower in company_name or company_name in query_lower
            ):
                matches.append(stock_data)
                continue

            # Check if query is a partial match of symbol
            if query_lower in symbol.lower():
                matches.append(stock_data)

        return matches if matches else None

    def add_symbol_results(self, results: list[dict]):
        """
        Add symbol search results to cache, storing each result by its symbol.
        Merges with existing data to avoid duplicates.
        """
        for result in results:
            symbol = result.get("1. symbol")
            if symbol:
                # Store the complete result keyed by symbol
                self._symbol_search_cache[symbol] = result

        self._save_to_file()

    # Utility methods
    def has_cached_data(self, symbol: str, data_type: str) -> bool:
        """Check if specific data type is cached for a symbol."""
        cache_map = {
            "overview": self._overview_cache,
            "balance_sheet": self._balance_sheet_cache,
            "cash_flow": self._cash_flow_cache,
            "income_statement": self._income_statement_cache,
            "calculated_metrics": self._calculated_metrics_cache,
        }

        cache = cache_map.get(data_type)
        if cache is None:
            return False

        return symbol in cache and cache[symbol] is not None

    def clear_cache(self, symbol: str | None = None):
        """Clear cache for a specific symbol or all symbols and save to file."""
        if symbol:
            # Clear specific symbol
            self._overview_cache.pop(symbol, None)
            self._balance_sheet_cache.pop(symbol, None)
            self._cash_flow_cache.pop(symbol, None)
            self._income_statement_cache.pop(symbol, None)
            self._calculated_metrics_cache.pop(symbol, None)
        else:
            # Clear all caches
            self._overview_cache.clear()
            self._balance_sheet_cache.clear()
            self._cash_flow_cache.clear()
            self._income_statement_cache.clear()
            self._calculated_metrics_cache.clear()
            self._symbol_search_cache.clear()

        self._save_to_file()

    def get_cached_symbols(self) -> list[str]:
        """Get list of all cached symbols."""
        all_symbols = set()
        all_symbols.update(self._overview_cache.keys())
        all_symbols.update(self._balance_sheet_cache.keys())
        all_symbols.update(self._cash_flow_cache.keys())
        all_symbols.update(self._income_statement_cache.keys())
        all_symbols.update(self._calculated_metrics_cache.keys())
        return sorted(list(all_symbols))

    def get_cache_info(self) -> dict[str, Any]:
        """Get information about the current cache state."""
        return {
            "cache_file": str(self.cache_file_path),
            "file_exists": self.cache_file_path.exists(),
            "total_symbols": len(self.get_cached_symbols()),
            "data_counts": {
                "overview": len(self._overview_cache),
                "balance_sheet_reports": sum(
                    len(reports) for reports in self._balance_sheet_cache.values()
                ),
                "cash_flow_reports": sum(
                    len(reports) for reports in self._cash_flow_cache.values()
                ),
                "income_statement_reports": sum(
                    len(reports) for reports in self._income_statement_cache.values()
                ),
                "calculated_metrics": sum(
                    len(metrics) for metrics in self._calculated_metrics_cache.values()
                ),
                "symbol_search_symbols": len(self._symbol_search_cache),
            },
            "symbol_search_cache": {
                symbol: stock_data.get("2. name", "Unknown")
                for symbol, stock_data in self._symbol_search_cache.items()
            },
            "file_size_bytes": self.cache_file_path.stat().st_size
            if self.cache_file_path.exists()
            else 0,
        }


_cache = PersistentCache()


def get_cache() -> PersistentCache:
    """Get the global cache instance."""
    return _cache
