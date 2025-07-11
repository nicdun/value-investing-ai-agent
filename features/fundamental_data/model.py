from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime


def to_camel(string: str) -> str:
    """Convert snake_case to camelCase."""
    components = string.split("_")
    return components[0] + "".join(word.capitalize() for word in components[1:])


def to_camel_capitalize(string: str) -> str:
    """Convert snake_case to camelCase."""
    components = string.split("_")
    return "".join(word.capitalize() for word in components)


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
    market_capitalization: str | None = None
    ebitda: str | None = None
    pe_ratio: str | None = None
    peg_ratio: str | None = None
    book_value: str | None = None
    dividend_per_share: str | None = None
    dividend_yield: str | None = None
    eps: str | None = None
    revenue_per_share_ttm: str | None = None
    profit_margin: str | None = None
    operating_margin_ttm: str | None = None
    return_on_assets_ttm: str | None = None
    return_on_equity_ttm: str | None = None
    revenue_ttm: str | None = None
    gross_profit_ttm: str | None = None
    diluted_eps_ttm: str | None = None
    quarterly_earnings_growth_yoy: str | None = None
    quarterly_revenue_growth_yoy: str | None = None
    analyst_target_price: str | None = None
    analyst_rating_strong_buy: str | None = None
    analyst_rating_buy: str | None = None
    analyst_rating_hold: str | None = None
    analyst_rating_sell: str | None = None
    analyst_rating_strong_sell: str | None = None
    trailing_pe: str | None = None
    forward_pe: str | None = None
    price_to_sales_ratio_ttm: str | None = None
    price_to_book_ratio: str | None = None
    ev_to_revenue: str | None = None
    ev_to_ebitda: str | None = None
    beta: str | None = None
    week_52_high: str | None = Field(default=None, alias="52WeekHigh")
    week_52_low: str | None = Field(default=None, alias="52WeekLow")
    day_50_moving_average: str | None = Field(default=None, alias="50DayMovingAverage")
    day_200_moving_average: str | None = Field(
        default=None, alias="200DayMovingAverage"
    )
    shares_outstanding: str | None = None
    shares_float: str | None = None
    percent_insiders: str | None = None
    percent_institutions: str | None = None
    dividend_date: str | None = None
    ex_dividend_date: str | None = None


class FinancialReport(BaseModel):
    """Base class for financial reports."""

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,  # Allow both camelCase and snake_case during parsing
    )

    fiscal_date_ending: str
    reported_currency: str


class IncomeStatementReport(FinancialReport):
    gross_profit: str | None = None
    total_revenue: str | None = None
    cost_of_revenue: str | None = None
    cost_of_goods_and_services_sold: str | None = None
    operating_income: str | None = None
    selling_general_and_administrative: str | None = None
    research_and_development: str | None = None
    operating_expenses: str | None = None
    investment_income_net: str | None = None
    net_interest_income: str | None = None
    interest_income: str | None = None
    interest_expense: str | None = None
    non_interest_income: str | None = None
    other_non_operating_income: str | None = None
    depreciation: str | None = None
    depreciation_and_amortization: str | None = None
    income_before_tax: str | None = None
    income_tax_expense: str | None = None
    interest_and_debt_expense: str | None = None
    net_income_from_continuing_operations: str | None = None
    comprehensive_income_net_of_tax: str | None = None
    ebit: str | None = None
    ebitda: str | None = None
    net_income: str | None = None


class BalanceSheetReport(FinancialReport):
    total_assets: str | None = None
    total_current_assets: str | None = None
    cash_and_cash_equivalents_at_carrying_value: str | None = None
    cash_and_short_term_investments: str | None = None
    inventory: str | None = None
    current_net_receivables: str | None = None
    total_non_current_assets: str | None = None
    property_plant_equipment: str | None = None
    accumulated_depreciation_amortization_ppe: str | None = None
    intangible_assets: str | None = None
    intangible_assets_excluding_goodwill: str | None = None
    goodwill: str | None = None
    investments: str | None = None
    long_term_investments: str | None = None
    short_term_investments: str | None = None
    other_current_assets: str | None = None
    other_non_current_assets: str | None = None
    total_liabilities: str | None = None
    total_current_liabilities: str | None = None
    current_accounts_payable: str | None = None
    deferred_revenue: str | None = None
    current_debt: str | None = None
    short_term_debt: str | None = None
    total_non_current_liabilities: str | None = None
    capital_lease_obligations: str | None = None
    long_term_debt: str | None = None
    current_long_term_debt: str | None = None
    long_term_debt_noncurrent: str | None = None
    short_long_term_debt_total: str | None = None
    other_current_liabilities: str | None = None
    other_non_current_liabilities: str | None = None
    total_shareholder_equity: str | None = None
    treasury_stock: str | None = None
    retained_earnings: str | None = None
    common_stock: str | None = None
    common_stock_shares_outstanding: str | None = None


class CashFlowReport(FinancialReport):
    operating_cashflow: str | None = None
    payments_for_operating_activities: str | None = None
    proceeds_from_operating_activities: str | None = None
    change_in_operating_liabilities: str | None = None
    change_in_operating_assets: str | None = None
    depreciation_depletion_and_amortization: str | None = None
    capital_expenditures: str | None = None
    change_in_receivables: str | None = None
    change_in_inventory: str | None = None
    profit_loss: str | None = None
    cashflow_from_investment: str | None = None
    cashflow_from_financing: str | None = None
    proceeds_from_repayments_of_short_term_debt: str | None = None
    payments_for_repurchase_of_common_stock: str | None = None
    payments_for_repurchase_of_equity: str | None = None
    payments_for_repurchase_of_preferred_stock: str | None = None
    dividend_payout: str | None = None
    dividend_payout_common_stock: str | None = None
    dividend_payout_preferred_stock: str | None = None
    proceeds_from_issuance_of_common_stock: str | None = None
    proceeds_from_issuance_of_long_term_debt_and_capital_securities: str | None = None
    proceeds_from_issuance_of_preferred_stock: str | None = None
    proceeds_from_repurchase_of_equity: str | None = None
    proceeds_from_sale_of_treasury_stock: str | None = None
    change_in_cash_and_cash_equivalents: str | None = None
    change_in_exchange_rate: str | None = None
    net_income: str | None = None


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


class CalculatedMetrics(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )

    fiscal_date_ending: str
    quarter: int | None = None
    year: int
    pe_ratio: str | None = None
    fcf_yield: str | None = None
    ebitda_multiple: str | None = None
    roe: str | None = None
    roa: str | None = None
    debt_to_equity: str | None = None
    current_ratio: str | None = None
    quick_ratio: str | None = None
    interest_coverage: str | None = None
    gross_margin: str | None = None
    operating_margin: str | None = None
    net_margin: str | None = None


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
