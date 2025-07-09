from datetime import datetime
from .model import (
    FundamentalData,
    StockMetaData,
    BalanceSheetReport,
    CashFlowReport,
    IncomeStatementReport,
    CalculatedMetrics,
)


class Cache:
    """In-memory cache for responses using strongly-typed models."""

    def __init__(self):
        self._overview_cache: dict[str, StockMetaData] = {}
        self._balance_sheet_cache: dict[str, list[BalanceSheetReport]] = {}
        self._cash_flow_cache: dict[str, list[CashFlowReport]] = {}
        self._income_statement_cache: dict[str, list[IncomeStatementReport]] = {}
        self._calculated_metrics_cache: dict[str, list[CalculatedMetrics]] = {}

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
        """Cache overview data."""
        self._overview_cache[symbol] = data

    # Balance Sheet methods
    def get_balance_sheet(self, symbol: str) -> list[BalanceSheetReport] | None:
        """Get cached balance sheet data if available."""
        return self._balance_sheet_cache.get(symbol)

    def set_balance_sheet(self, symbol: str, data: list[BalanceSheetReport]):
        """Append new balance sheet data to cache."""
        self._balance_sheet_cache[symbol] = self._merge_financial_reports(
            self._balance_sheet_cache.get(symbol), data
        )

    # Cash Flow methods
    def get_cash_flow(self, symbol: str) -> list[CashFlowReport] | None:
        """Get cached cash flow data if available."""
        return self._cash_flow_cache.get(symbol)

    def set_cash_flow(self, symbol: str, data: list[CashFlowReport]):
        """Append new cash flow data to cache."""
        self._cash_flow_cache[symbol] = self._merge_financial_reports(
            self._cash_flow_cache.get(symbol), data
        )

    # Income Statement methods
    def get_income_statement(self, symbol: str) -> list[IncomeStatementReport] | None:
        """Get cached income statement data if available."""
        return self._income_statement_cache.get(symbol)

    def set_income_statement(self, symbol: str, data: list[IncomeStatementReport]):
        """Append new income statement data to cache."""
        self._income_statement_cache[symbol] = self._merge_financial_reports(
            self._income_statement_cache.get(symbol), data
        )

    # Calculated Metrics methods
    def get_calculated_metrics(self, symbol: str) -> list[CalculatedMetrics] | None:
        """Get cached calculated metrics if available."""
        return self._calculated_metrics_cache.get(symbol)

    def set_calculated_metrics(self, symbol: str, data: list[CalculatedMetrics]):
        """Append new calculated metrics to cache."""
        self._calculated_metrics_cache[symbol] = self._merge_calculated_metrics(
            self._calculated_metrics_cache.get(symbol), data
        )

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
        """Clear cache for a specific symbol or all symbols."""
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

    def get_cached_symbols(self) -> list[str]:
        """Get list of all cached symbols."""
        all_symbols = set()
        all_symbols.update(self._overview_cache.keys())
        all_symbols.update(self._balance_sheet_cache.keys())
        all_symbols.update(self._cash_flow_cache.keys())
        all_symbols.update(self._income_statement_cache.keys())
        all_symbols.update(self._calculated_metrics_cache.keys())
        return sorted(list(all_symbols))


# Global cache instance
_cache = Cache()


def get_cache() -> Cache:
    """Get the global cache instance."""
    return _cache
