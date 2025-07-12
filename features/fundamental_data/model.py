from pydantic import BaseModel, Field, ConfigDict, field_validator
from datetime import datetime


def to_camel(string: str) -> str:
    """Convert snake_case to camelCase."""
    components = string.split("_")
    return components[0] + "".join(word.capitalize() for word in components[1:])


def to_camel_capitalize(string: str) -> str:
    """Convert snake_case to camelCase."""
    components = string.split("_")
    return "".join(word.capitalize() for word in components)


def parse_float_or_none(value: str) -> float | None:
    """Parse a value to float, handling 'None' strings and other edge cases."""
    if value is None:
        return None
    if isinstance(value, str):
        if value.strip() in ["", "None", "N/A", "--", "null"]:
            return None
        try:
            return float(value)
        except (ValueError, TypeError):
            return None
    if isinstance(value, (int, float)):
        return float(value)
    return None


class StockMetaData(BaseModel):
    """Stock metadata and overview information."""

    model_config = ConfigDict(
        alias_generator=to_camel_capitalize,
        populate_by_name=True,  # Allow both camelCase and snake_case during parsing
    )

    symbol: str = Field(alias="Symbol")
    name: str = Field(alias="Name")
    description: str | None = None
    asset_type: str | None = None
    cik: str | None = None
    exchange: str | None = None
    currency: str | None = None
    country: str | None = None
    sector: str | None = None
    industry: str | None = None
    address: str | None = None
    official_site: str | None = None
    fiscal_year_end: str | None = None
    latest_quarter: str | None = None
    market_capitalization: float | None = None
    ebitda: float | None = None
    pe_ratio: float | None = None
    peg_ratio: float | None = None
    book_value: float | None = None
    dividend_per_share: float | None = None
    dividend_yield: float | None = None
    eps: float | None = None
    revenue_per_share_ttm: float | None = None
    profit_margin: float | None = None
    operating_margin_ttm: float | None = None
    return_on_assets_ttm: float | None = None
    return_on_equity_ttm: float | None = None
    revenue_ttm: float | None = None
    gross_profit_ttm: float | None = None
    diluted_eps_ttm: float | None = None
    quarterly_earnings_growth_yoy: float | None = None
    quarterly_revenue_growth_yoy: float | None = None
    analyst_target_price: float | None = None
    analyst_rating_strong_buy: float | None = None
    analyst_rating_buy: float | None = None
    analyst_rating_hold: float | None = None
    analyst_rating_sell: float | None = None
    analyst_rating_strong_sell: float | None = None
    trailing_pe: float | None = None
    forward_pe: float | None = None
    price_to_sales_ratio_ttm: float | None = None
    price_to_book_ratio: float | None = None
    ev_to_revenue: float | None = None
    ev_to_ebitda: float | None = None
    beta: float | None = None
    week_52_high: float | None = Field(default=None, alias="52WeekHigh")
    week_52_low: float | None = Field(default=None, alias="52WeekLow")
    day_50_moving_average: float | None = Field(
        default=None, alias="50DayMovingAverage"
    )
    day_200_moving_average: float | None = Field(
        default=None, alias="200DayMovingAverage"
    )
    shares_outstanding: float | None = None
    shares_float: float | None = None
    percent_insiders: float | None = None
    percent_institutions: float | None = None
    dividend_date: str | None = None
    ex_dividend_date: str | None = None

    @field_validator(
        "market_capitalization",
        "ebitda",
        "pe_ratio",
        "peg_ratio",
        "book_value",
        "dividend_per_share",
        "dividend_yield",
        "eps",
        "revenue_per_share_ttm",
        "profit_margin",
        "operating_margin_ttm",
        "return_on_assets_ttm",
        "return_on_equity_ttm",
        "revenue_ttm",
        "gross_profit_ttm",
        "diluted_eps_ttm",
        "quarterly_earnings_growth_yoy",
        "quarterly_revenue_growth_yoy",
        "analyst_target_price",
        "analyst_rating_strong_buy",
        "analyst_rating_buy",
        "analyst_rating_hold",
        "analyst_rating_sell",
        "analyst_rating_strong_sell",
        "trailing_pe",
        "forward_pe",
        "price_to_sales_ratio_ttm",
        "price_to_book_ratio",
        "ev_to_revenue",
        "ev_to_ebitda",
        "beta",
        "week_52_high",
        "week_52_low",
        "day_50_moving_average",
        "day_200_moving_average",
        "shares_outstanding",
        "shares_float",
        "percent_insiders",
        "percent_institutions",
        mode="before",
    )
    @classmethod
    def validate_float_fields(cls, v: str) -> float | None:
        return parse_float_or_none(v)


class FinancialReport(BaseModel):
    """Base class for financial reports."""

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,  # Allow both camelCase and snake_case during parsing
    )

    fiscal_date_ending: str
    quarter_report: bool = False
    annual_report: bool = False
    reported_currency: str


class IncomeStatementReport(FinancialReport):
    gross_profit: float | None = None
    total_revenue: float | None = None
    cost_of_revenue: float | None = None
    cost_of_goods_and_services_sold: float | None = None
    operating_income: float | None = None
    selling_general_and_administrative: float | None = None
    research_and_development: float | None = None
    operating_expenses: float | None = None
    investment_income_net: float | None = None
    net_interest_income: float | None = None
    interest_income: float | None = None
    interest_expense: float | None = None
    non_interest_income: float | None = None
    other_non_operating_income: float | None = None
    depreciation: float | None = None
    depreciation_and_amortization: float | None = None
    income_before_tax: float | None = None
    income_tax_expense: float | None = None
    interest_and_debt_expense: float | None = None
    net_income_from_continuing_operations: float | None = None
    comprehensive_income_net_of_tax: float | None = None
    ebit: float | None = None
    ebitda: float | None = None
    net_income: float | None = None

    @field_validator(
        "gross_profit",
        "total_revenue",
        "cost_of_revenue",
        "cost_of_goods_and_services_sold",
        "operating_income",
        "selling_general_and_administrative",
        "research_and_development",
        "operating_expenses",
        "investment_income_net",
        "net_interest_income",
        "interest_income",
        "interest_expense",
        "non_interest_income",
        "other_non_operating_income",
        "depreciation",
        "depreciation_and_amortization",
        "income_before_tax",
        "income_tax_expense",
        "interest_and_debt_expense",
        "net_income_from_continuing_operations",
        "comprehensive_income_net_of_tax",
        "ebit",
        "ebitda",
        "net_income",
        mode="before",
    )
    @classmethod
    def validate_float_fields(cls, v: str) -> float | None:
        return parse_float_or_none(v)


class BalanceSheetReport(FinancialReport):
    total_assets: float | None = None
    total_current_assets: float | None = None
    cash_and_cash_equivalents_at_carrying_value: float | None = None
    cash_and_short_term_investments: float | None = None
    inventory: float | None = None
    current_net_receivables: float | None = None
    total_non_current_assets: float | None = None
    property_plant_equipment: float | None = None
    accumulated_depreciation_amortization_ppe: float | None = None
    intangible_assets: float | None = None
    intangible_assets_excluding_goodwill: float | None = None
    goodwill: float | None = None
    investments: float | None = None
    long_term_investments: float | None = None
    short_term_investments: float | None = None
    other_current_assets: float | None = None
    other_non_current_assets: float | None = None
    total_liabilities: float | None = None
    total_current_liabilities: float | None = None
    current_accounts_payable: float | None = None
    deferred_revenue: float | None = None
    current_debt: float | None = None
    short_term_debt: float | None = None
    total_non_current_liabilities: float | None = None
    capital_lease_obligations: float | None = None
    long_term_debt: float | None = None
    current_long_term_debt: float | None = None
    long_term_debt_noncurrent: float | None = None
    short_long_term_debt_total: float | None = None
    other_current_liabilities: float | None = None
    other_non_current_liabilities: float | None = None
    total_shareholder_equity: float | None = None
    treasury_stock: float | None = None
    retained_earnings: float | None = None
    common_stock: float | None = None
    common_stock_shares_outstanding: float | None = None

    @field_validator(
        "total_assets",
        "total_current_assets",
        "cash_and_cash_equivalents_at_carrying_value",
        "cash_and_short_term_investments",
        "inventory",
        "current_net_receivables",
        "total_non_current_assets",
        "property_plant_equipment",
        "accumulated_depreciation_amortization_ppe",
        "intangible_assets",
        "intangible_assets_excluding_goodwill",
        "goodwill",
        "investments",
        "long_term_investments",
        "short_term_investments",
        "other_current_assets",
        "other_non_current_assets",
        "total_liabilities",
        "total_current_liabilities",
        "current_accounts_payable",
        "deferred_revenue",
        "current_debt",
        "short_term_debt",
        "total_non_current_liabilities",
        "capital_lease_obligations",
        "long_term_debt",
        "current_long_term_debt",
        "long_term_debt_noncurrent",
        "short_long_term_debt_total",
        "other_current_liabilities",
        "other_non_current_liabilities",
        "total_shareholder_equity",
        "treasury_stock",
        "retained_earnings",
        "common_stock",
        "common_stock_shares_outstanding",
        mode="before",
    )
    @classmethod
    def validate_float_fields(cls, v: str) -> float | None:
        return parse_float_or_none(v)


class CashFlowReport(FinancialReport):
    operating_cashflow: float | None = None
    payments_for_operating_activities: float | None = None
    proceeds_from_operating_activities: float | None = None
    change_in_operating_liabilities: float | None = None
    change_in_operating_assets: float | None = None
    depreciation_depletion_and_amortization: float | None = None
    capital_expenditures: float | None = None
    change_in_receivables: float | None = None
    change_in_inventory: float | None = None
    profit_loss: float | None = None
    cashflow_from_investment: float | None = None
    cashflow_from_financing: float | None = None
    proceeds_from_repayments_of_short_term_debt: float | None = None
    payments_for_repurchase_of_common_stock: float | None = None
    payments_for_repurchase_of_equity: float | None = None
    payments_for_repurchase_of_preferred_stock: float | None = None
    dividend_payout: float | None = None
    dividend_payout_common_stock: float | None = None
    dividend_payout_preferred_stock: float | None = None
    proceeds_from_issuance_of_common_stock: float | None = None
    proceeds_from_issuance_of_long_term_debt_and_capital_securities: float | None = None
    proceeds_from_issuance_of_preferred_stock: float | None = None
    proceeds_from_repurchase_of_equity: float | None = None
    proceeds_from_sale_of_treasury_stock: float | None = None
    change_in_cash_and_cash_equivalents: float | None = None
    change_in_exchange_rate: float | None = None
    net_income: float | None = None

    @field_validator(
        "operating_cashflow",
        "payments_for_operating_activities",
        "proceeds_from_operating_activities",
        "change_in_operating_liabilities",
        "change_in_operating_assets",
        "depreciation_depletion_and_amortization",
        "capital_expenditures",
        "change_in_receivables",
        "change_in_inventory",
        "profit_loss",
        "cashflow_from_investment",
        "cashflow_from_financing",
        "proceeds_from_repayments_of_short_term_debt",
        "payments_for_repurchase_of_common_stock",
        "payments_for_repurchase_of_equity",
        "payments_for_repurchase_of_preferred_stock",
        "dividend_payout",
        "dividend_payout_common_stock",
        "dividend_payout_preferred_stock",
        "proceeds_from_issuance_of_common_stock",
        "proceeds_from_issuance_of_long_term_debt_and_capital_securities",
        "proceeds_from_issuance_of_preferred_stock",
        "proceeds_from_repurchase_of_equity",
        "proceeds_from_sale_of_treasury_stock",
        "change_in_cash_and_cash_equivalents",
        "change_in_exchange_rate",
        "net_income",
        mode="before",
    )
    @classmethod
    def validate_float_fields(cls, v: str) -> float | None:
        return parse_float_or_none(v)


class CalculatedMetrics(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )

    fiscal_date_ending: str
    quarter: int | None = None
    year: int
    pe_ratio: float | None = None
    fcf_yield: float | None = None
    ebitda_multiple: float | None = None
    roe: float | None = None
    roa: float | None = None
    debt_to_equity: float | None = None
    current_ratio: float | None = None
    quick_ratio: float | None = None
    interest_coverage: float | None = None
    gross_margin: float | None = None
    operating_margin: float | None = None
    net_margin: float | None = None

    @field_validator(
        "pe_ratio",
        "fcf_yield",
        "ebitda_multiple",
        "roe",
        "roa",
        "debt_to_equity",
        "current_ratio",
        "quick_ratio",
        "interest_coverage",
        "gross_margin",
        "operating_margin",
        "net_margin",
        mode="before",
    )
    @classmethod
    def validate_float_fields(cls, v: str) -> float | None:
        return parse_float_or_none(v)


class StockIncomeStatement(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )

    symbol: str
    annual_reports: list[IncomeStatementReport] = Field(default_factory=list)
    quarterly_reports: list[IncomeStatementReport] | None = None


class StockBalanceSheet(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )

    symbol: str
    annual_reports: list[BalanceSheetReport] = Field(default_factory=list)
    quarterly_reports: list[BalanceSheetReport] | None = None


class StockCashFlow(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )

    symbol: str
    annual_reports: list[CashFlowReport] = Field(default_factory=list)
    quarterly_reports: list[CashFlowReport] | None = None


class FundamentalData(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )

    symbol: str
    overview: StockMetaData | None = None
    balance_sheet: list[BalanceSheetReport] = Field(default_factory=list)
    cash_flow: list[CashFlowReport] = Field(default_factory=list)
    income_statement: list[IncomeStatementReport] = Field(default_factory=list)
    calculated_metrics: list[CalculatedMetrics] | None = None
    last_updated: str


class ProcessedFundamentalData(FinancialReport):
    revenue: float | None = None
    net_income: float | None = None
    gross_profit: float | None = None
    operating_income: float | None = None
    research_and_development: float | None = None
    ebitda: float | None = None
    shareholders_equity: float | None = None
    total_debt: float | None = None
    cash_and_equivalents: float | None = None
    outstanding_shares: float | None = None
    goodwill_and_intangible_assets: float | None = None
    operating_cashflow: float | None = None
    capital_expenditures: float | None = None
    free_cash_flow: float | None = None
    return_on_invested_capital: float | None = None
    return_on_equity: float | None = None
    debt_to_equity_ratio: float | None = None
    gross_margin: float | None = None
