from features.fundamental_data.model import FundamentalData, ProcessedFundamentalData


def get_fundamental_data_time_series(
    fundamental_data: FundamentalData, annual: bool
) -> list[ProcessedFundamentalData]:
    """Get time series of financial metrics for trend analysis."""
    time_series = []
    filtered_income_statements = [
        income_statement
        for income_statement in fundamental_data.income_statement
        if (annual and income_statement.annual_report)
        or (not annual and not income_statement.annual_report)
    ]
    filtered_balance_sheets = [
        balance_sheet
        for balance_sheet in fundamental_data.balance_sheet
        if (annual and balance_sheet.annual_report)
        or (not annual and not balance_sheet.annual_report)
    ]
    filtered_cash_flows = [
        cash_flow
        for cash_flow in fundamental_data.cash_flow
        if (annual and cash_flow.annual_report)
        or (not annual and not cash_flow.annual_report)
    ]

    # Get the number of periods available
    num_periods = min(
        len(filtered_income_statements),
        len(filtered_balance_sheets),
        len(filtered_cash_flows),
    )

    for i in range(num_periods):
        period_data = ProcessedFundamentalData(
            fiscal_date_ending=filtered_income_statements[i].fiscal_date_ending,
            reported_currency=filtered_income_statements[i].reported_currency,
            annual_report=annual,
            quarter_report=not annual,
        )
        # Income statement data
        if i < len(filtered_income_statements):
            income = filtered_income_statements[i]
            period_data.revenue = income.total_revenue
            period_data.net_income = income.net_income
            period_data.gross_profit = income.gross_profit
            period_data.research_and_development = income.research_and_development

            # Calculate gross margin
            if period_data.revenue and period_data.gross_profit:
                period_data.gross_margin = (
                    period_data.gross_profit / period_data.revenue
                )

        # Balance sheet data
        if i < len(filtered_balance_sheets):
            balance = filtered_balance_sheets[i]
            period_data.shareholders_equity = balance.total_shareholder_equity
            period_data.total_debt = balance.short_long_term_debt_total
            period_data.cash_and_equivalents = (
                balance.cash_and_cash_equivalents_at_carrying_value
            )
            period_data.outstanding_shares = balance.common_stock_shares_outstanding
            period_data.goodwill_and_intangible_assets = (balance.goodwill or 0) + (
                balance.intangible_assets or 0
            )

        # Cash flow data
        if i < len(filtered_cash_flows):
            cashflow = filtered_cash_flows[i]
            period_data.operating_cashflow = cashflow.operating_cashflow
            period_data.capital_expenditures = cashflow.capital_expenditures

            # Calculate free cash flow
            if (
                cashflow.operating_cashflow is not None
                and cashflow.capital_expenditures is not None
            ):
                period_data.free_cash_flow = (
                    cashflow.operating_cashflow - cashflow.capital_expenditures
                )

        # Calculate ROIC
        if (
            period_data.net_income
            and period_data.shareholders_equity
            and period_data.total_debt
        ):
            invested_capital = period_data.shareholders_equity + (
                period_data.total_debt or 0
            )
            if invested_capital > 0:
                period_data.return_on_invested_capital = (
                    period_data.net_income / invested_capital
                )

        # Caclulate ROE
        if period_data.net_income and period_data.shareholders_equity:
            period_data.return_on_equity = (
                period_data.net_income / period_data.shareholders_equity
            )

        # Caclulate D/E Ratio
        if period_data.total_debt and period_data.shareholders_equity:
            period_data.debt_to_equity_ratio = (
                period_data.total_debt / period_data.shareholders_equity
            )

        time_series.append(period_data)

    return time_series


def process_fundamental_data_to_usd(
    exchange_rate: float,
    fundamental_data_time_series: list[ProcessedFundamentalData],
) -> list[ProcessedFundamentalData]:
    """Process the fundamental data time series to USD."""
    for period_data in fundamental_data_time_series:
        period_data.revenue = period_data.revenue * exchange_rate
        period_data.net_income = period_data.net_income * exchange_rate
        period_data.gross_profit = period_data.gross_profit * exchange_rate
        period_data.research_and_development = (
            period_data.research_and_development * exchange_rate
        )
        period_data.operating_cashflow = period_data.operating_cashflow * exchange_rate
        period_data.capital_expenditures = (
            period_data.capital_expenditures * exchange_rate
        )
        period_data.free_cash_flow = period_data.free_cash_flow * exchange_rate
    return fundamental_data_time_series
