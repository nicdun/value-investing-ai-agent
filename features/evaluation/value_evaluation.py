from features.fundamental_data.model import FundamentalData
from ui.cli import get_cli
from langchain_core.prompts import ChatPromptTemplate
import json
from features.llm.llm import call_llm
from features.evaluation.model import EvaluationSignal
from features.fundamental_data.model import StockMetaData
from features.fundamental_data.model import ProcessedFundamentalData
from features.evaluation.kpi_calculation import calculate_average_growth_rate

cli = get_cli()


def print_analysis_results(analysis_name: str, analysis_result: dict):
    """Print analysis results in a formatted way."""
    cli.show_info(f"\n📊 {analysis_name} Analysis Results")
    cli.show_info("=" * 50)

    # Show score with visual indicator
    score = analysis_result.get("score", 0)
    if score >= 8:
        score_emoji = "🟢"
        score_label = "Excellent"
    elif score >= 6:
        score_emoji = "🟡"
        score_label = "Good"
    elif score >= 4:
        score_emoji = "🟠"
        score_label = "Fair"
    else:
        score_emoji = "🔴"
        score_label = "Poor"

    cli.show_info(f"{score_emoji} Score: {score:.1f}/10 ({score_label})")

    # Show details
    details = analysis_result.get("details", "")
    if details:
        cli.show_info(f"📝 Details: {details}")

    cli.show_info("")


def print_valuation_metrics(analysis_result: dict, market_capitalization: float):
    # Show additional metrics for valuation analysis
    cli.show_info("\n💰 Valuation Metrics:")
    intrinsic_range = analysis_result["intrinsic_value_range"]
    cli.show_info(f"   Conservative Value: ${intrinsic_range['conservative']:,.0f}")
    cli.show_info(f"   Reasonable Value:   ${intrinsic_range['reasonable']:,.0f}")
    cli.show_info(f"   Optimistic Value:   ${intrinsic_range['optimistic']:,.0f}")
    cli.show_info(f"   Actual Value (MCap): ${market_capitalization:,.0f}")

    fcf_yield = analysis_result.get("fcf_yield", 0)
    cli.show_info(f"   FCF Yield:          {fcf_yield:.1%}")


def evaluate(
    overview: StockMetaData,
    fundamental_data_time_series: list[ProcessedFundamentalData],
) -> str:
    """
    Perform comprehensive value investing analysis on the given stock data.

    Args:
        overview: Stock metadata and overview information
        fundamental_data_time_series: Time series of processed fundamental data
        analysis_years: Number of years of data to use for analysis (5-20, default 10)

    Returns:
        EvaluationSignal with the complete investment analysis
    """
    # Show analysis scope
    cli.show_info(
        f"\n🔍 Performing analysis using {len(fundamental_data_time_series)} years of data"
    )

    # Perform analyses
    cli.show_progress_start("Business Model: Analyzing business predictability")
    # predictability_analysis = analyze_predictability(fundamental_data)

    cli.show_progress_start("Growth Rates: Analyzing growth rates")
    growth_rates_analysis = analyze_growth_rates(fundamental_data_time_series)
    cli.show_progress_success("Growth rates analysis completed")
    print_analysis_results("Growth Rates", growth_rates_analysis)

    cli.show_progress_start("MOAT: Analyzing moat strength")
    moat_analysis = analyze_moat_strength(fundamental_data_time_series)
    cli.show_progress_success("MOAT analysis completed")
    print_analysis_results("MOAT", moat_analysis)

    cli.show_progress_start("Management: Analyzing management quality")
    management_analysis = analyze_management_quality(fundamental_data_time_series)
    cli.show_progress_success("Management quality analysis completed")
    print_analysis_results("Management Quality", management_analysis)

    cli.show_progress_start("Margin of Safety: Calculating valuation")
    valuation_analysis = calculate_margin_of_safety(
        overview, fundamental_data_time_series
    )
    cli.show_progress_success("Valuation analysis completed")
    print_analysis_results("Margin of Safety", valuation_analysis)
    print_valuation_metrics(valuation_analysis, overview.market_capitalization)

    cli.show_progress_start("Generating final analysis...")
    output = generate_output(
        overview,
        growth_rates_analysis,
        moat_analysis,
        management_analysis,
        valuation_analysis,
    )
    cli.show_progress_success("Investment analysis completed")

    # Print final summary
    cli.show_info("\n🎯 Final Investment Analysis")
    cli.show_info("=" * 60)
    cli.show_info(output.report)

    return output


def analyze_predictability(
    fundamental_data_time_series: list[ProcessedFundamentalData],
) -> dict[str, any]:
    pass


def analyze_moat_strength(
    fundamental_data_time_series: list[ProcessedFundamentalData],
) -> dict[str, any]:
    """
    Analyze the business's competitive advantage using value investing approach:
    - Pricing power (stable/improving gross margins)
    - Low capital requirements
    - Network effects and intangible assets (R&D investments, goodwill)
    """
    score = 0
    details = []

    if not fundamental_data_time_series:
        return {"score": 0, "details": "Insufficient data to analyze moat strength"}

    # Pricing power - check gross margin stability and trends
    gross_margins = [
        item.gross_margin
        for item in fundamental_data_time_series
        if item.gross_margin is not None
    ]

    if gross_margins and len(gross_margins) >= 3:
        # Stable or improving gross margins
        margin_trend = sum(
            1
            for i in range(1, len(gross_margins))
            if gross_margins[i] >= gross_margins[i - 1]
        )
        if margin_trend >= len(gross_margins) * 0.7:  # Improving in 70% of periods
            score += 2
            details.append("Strong pricing power: Gross margins consistently improving")
        elif sum(gross_margins) / len(gross_margins) > 0.3:  # Average margin > 30%
            score += 1
            details.append(
                f"Good pricing power: Average gross margin {sum(gross_margins) / len(gross_margins):.1%}"
            )
        else:
            details.append("Limited pricing power: Low or declining gross margins")
    else:
        details.append("Insufficient gross margin data")

    # Capital intensity
    if len(fundamental_data_time_series) >= 3:
        capex_to_revenue = []
        for item in fundamental_data_time_series:
            if (
                item.capital_expenditures is not None
                and item.revenue is not None
                and item.revenue > 0
            ):
                # Note: capital_expenditure is typically negative in financial statements
                capex_ratio = abs(item.capital_expenditures) / item.revenue
                capex_to_revenue.append(capex_ratio)

        if capex_to_revenue:
            avg_capex_ratio = sum(capex_to_revenue) / len(capex_to_revenue)
            if avg_capex_ratio < 0.05:  # Less than 5% of revenue
                score += 2
                details.append(
                    f"Low capital requirements: Avg capex {avg_capex_ratio:.1%} of revenue"
                )
            elif avg_capex_ratio < 0.10:  # Less than 10% of revenue
                score += 1
                details.append(
                    f"Moderate capital requirements: Avg capex {avg_capex_ratio:.1%} of revenue"
                )
            else:
                details.append(
                    f"High capital requirements: Avg capex {avg_capex_ratio:.1%} of revenue"
                )
        else:
            details.append("No capital expenditure data available")
    else:
        details.append("Insufficient data for capital intensity analysis")

    # Intangible assets
    research_and_development = [
        item.research_and_development
        for item in fundamental_data_time_series
        if item.research_and_development is not None
    ]

    goodwill_and_intangible_assets = [
        item.goodwill_and_intangible_assets
        for item in fundamental_data_time_series
        if item.goodwill_and_intangible_assets is not None
    ]

    if research_and_development and len(research_and_development) > 0:
        if sum(research_and_development) > 0:  # If company is investing in R&D
            score += 1
            details.append("Invests in R&D, building intellectual property")

    if goodwill_and_intangible_assets and len(goodwill_and_intangible_assets) > 0:
        score += 1
        details.append(
            "Significant goodwill/intangible assets, suggesting brand value or IP"
        )

    # Scale score to 0-10 range
    final_score = min(10, score * 10 / 6)  # Max possible raw score is 6

    return {"score": final_score, "details": "; ".join(details)}


def analyze_growth_rates(
    fundamental_data_time_series: list[ProcessedFundamentalData],
) -> dict[str, any]:
    """
    Analyze the business's growth rates using value investing approach:
    - Revenue growth
    - Equity growth
    - Net income growth
    - operating cashflow growth
    """
    score = 0
    details = []

    # Define metrics to analyze with their specific scoring parameters
    metrics = [
        ("revenue", "revenue", 0.1, 0.05),
        ("equity", "shareholders_equity", 0.1, 0.05),
        ("net income", "net_income", 0.1, 0.05),
        ("operating cashflow", "operating_cashflow", 0.1, 0.05),
        ("free cashflow", "free_cash_flow", 0.1, 0.10),
    ]

    for (
        metric_name,
        attribute_name,
        excellent_threshold,
        good_threshold,
    ) in metrics:
        # Extract values for the metric
        values = [
            getattr(item, attribute_name)
            for item in fundamental_data_time_series
            if getattr(item, attribute_name) is not None
        ]
        metric_score, metric_details = calculate_average_growth_rate(
            values=values,
            metric_name=metric_name,
            excellent_threshold=excellent_threshold,
            good_threshold=good_threshold,
        )
        score += metric_score
        details.extend(metric_details)

    final_score = max(0, min(10, score * 10 / (len(metrics) * 2)))

    return {"score": final_score, "details": "; ".join(details)}


def analyze_management_quality(
    fundamental_data_time_series: list[ProcessedFundamentalData],
) -> dict[str, any]:
    """
    Evaluate management quality using rule1 criteria:
    - ROIC > 10%
    - ROE > 15%
    - Capital allocation wisdom
    - Cash management efficiency
    """
    score = 0
    details = []

    # Get financial time series data
    if not fundamental_data_time_series:
        return {
            "score": 0,
            "details": "Insufficient data to analyze management quality",
        }

    # 1. Return on Invested Capital (ROIC) analysis
    roic_values = [
        item.return_on_invested_capital
        for item in fundamental_data_time_series
        if item.return_on_invested_capital is not None
    ]

    if roic_values:
        # Check if ROIC consistently above 10%
        high_roic_count = sum(1 for r in roic_values if r > 0.10)
        if high_roic_count >= len(roic_values) * 0.8:  # 80% of periods show high ROIC
            score += 3
            details.append(
                f"Excellent ROIC: >10% in {high_roic_count}/{len(roic_values)} periods"
            )
        elif high_roic_count >= len(roic_values) * 0.5:  # 50% of periods
            score += 2
            details.append(
                f"Good ROIC: >10% in {high_roic_count}/{len(roic_values)} periods"
            )
        elif high_roic_count > 0:
            score += 1
            details.append(
                f"Mixed ROIC: >10% in only {high_roic_count}/{len(roic_values)} periods"
            )
        else:
            details.append("Poor ROIC: Never exceeds 10% threshold")
    else:
        details.append("No ROIC data available")

    roe_values = [
        item.return_on_equity
        for item in fundamental_data_time_series
        if item.return_on_equity is not None
    ]
    if roe_values:
        # Check if ROE consistently above 15%
        high_roe_count = sum(1 for r in roe_values if r > 0.15)
        if high_roe_count >= len(roe_values) * 0.8:  # 80% of periods show high ROIC
            score += 3
            details.append(
                f"Excellent ROE: >15% in {high_roe_count}/{len(roe_values)} periods"
            )
        elif high_roe_count >= len(roe_values) * 0.5:  # 50% of periods
            score += 2
            details.append(
                f"Good ROE: >15% in {high_roe_count}/{len(roe_values)} periods"
            )
        elif high_roe_count > 0:
            score += 1
            details.append(
                f"Mixed ROE: >15% in only {high_roe_count}/{len(roe_values)} periods"
            )
        else:
            details.append("Poor ROE: Never exceeds 15% threshold")
    else:
        details.append("No ROE data available")

    # Capital allocation - Check FCF to net income ratio
    # Companies that convert earnings to cash
    fcf_values = [
        item.free_cash_flow
        for item in fundamental_data_time_series
        if item.free_cash_flow is not None
    ]

    net_income_values = [
        item.net_income
        for item in fundamental_data_time_series
        if item.net_income is not None
    ]

    if fcf_values and net_income_values and len(fcf_values) == len(net_income_values):
        # Calculate FCF to Net Income ratio for each period
        fcf_to_ni_ratios = []
        for i in range(len(fcf_values)):
            if net_income_values[i] and net_income_values[i] > 0:
                fcf_to_ni_ratios.append(fcf_values[i] / net_income_values[i])

        if fcf_to_ni_ratios:
            avg_ratio = sum(fcf_to_ni_ratios) / len(fcf_to_ni_ratios)
            if avg_ratio > 1.1:  # FCF > net income suggests good accounting
                score += 3
                details.append(
                    f"Excellent cash conversion: FCF/NI ratio of {avg_ratio:.2f}"
                )
            elif avg_ratio > 0.9:  # FCF roughly equals net income
                score += 2
                details.append(f"Good cash conversion: FCF/NI ratio of {avg_ratio:.2f}")
            elif avg_ratio > 0.7:  # FCF somewhat lower than net income
                score += 1
                details.append(
                    f"Moderate cash conversion: FCF/NI ratio of {avg_ratio:.2f}"
                )
            else:
                details.append(
                    f"Poor cash conversion: FCF/NI ratio of only {avg_ratio:.2f}"
                )
        else:
            details.append("Could not calculate FCF to Net Income ratios")
    else:
        details.append("Missing FCF or Net Income data")

    # Debt management
    debt_to_equity_values = [
        item.debt_to_equity_ratio
        for item in fundamental_data_time_series
        if item.debt_to_equity_ratio is not None
    ]

    if debt_to_equity_values and len(debt_to_equity_values) > 0:
        recent_de_ratio = debt_to_equity_values[0]

        if recent_de_ratio < 0.3:  # Very low debt
            score += 3
            details.append(
                f"Conservative debt management: D/E ratio of {recent_de_ratio:.2f}"
            )
        elif recent_de_ratio < 0.7:  # Moderate debt
            score += 2
            details.append(
                f"Prudent debt management: D/E ratio of {recent_de_ratio:.2f}"
            )
        elif recent_de_ratio < 1.5:  # Higher but still reasonable debt
            score += 1
            details.append(f"Moderate debt level: D/E ratio of {recent_de_ratio:.2f}")
        elif recent_de_ratio < 2.0:
            score += 0
            details.append(f"High debt level: D/E ratio of {recent_de_ratio:.2f}")
        elif recent_de_ratio < 3.0:
            score -= 1
            details.append(f"Very high debt level: D/E ratio of {recent_de_ratio:.2f}")
        else:
            score -= 3
            details.append(
                f"Unacceptable debt level: D/E ratio of {recent_de_ratio:.2f}"
            )
    else:
        details.append("Missing debt or equity data")

    # debt to earnings
    # TODO

    # Cash management efficiency
    cash_values = [
        item.cash_and_equivalents
        for item in fundamental_data_time_series
        if item.cash_and_equivalents is not None
    ]
    revenue_values = [
        item.revenue
        for item in fundamental_data_time_series
        if item.revenue is not None
    ]

    if (
        cash_values
        and revenue_values
        and len(cash_values) > 0
        and len(revenue_values) > 0
    ):
        # Calculate cash to revenue ratio (Munger likes 10-20% for most businesses)
        cash_to_revenue = (
            cash_values[0] / revenue_values[0] if revenue_values[0] > 0 else 0
        )

        if 0.1 <= cash_to_revenue <= 0.25:
            # Goldilocks zone - not too much, not too little
            score += 2
            details.append(
                f"Prudent cash management: Cash/Revenue ratio of {cash_to_revenue:.2f}"
            )
        elif 0.05 <= cash_to_revenue < 0.1 or 0.25 < cash_to_revenue <= 0.4:
            # Reasonable but not ideal
            score += 1
            details.append(
                f"Acceptable cash position: Cash/Revenue ratio of {cash_to_revenue:.2f}"
            )
        elif cash_to_revenue > 0.4:
            # Too much cash - potentially inefficient capital allocation
            details.append(
                f"Excess cash reserves: Cash/Revenue ratio of {cash_to_revenue:.2f}"
            )
        else:
            # Too little cash - potentially risky
            details.append(
                f"Low cash reserves: Cash/Revenue ratio of {cash_to_revenue:.2f}"
            )
    else:
        details.append("Insufficient cash or revenue data")

    # Consistency in share count
    share_counts = [
        item.outstanding_shares
        for item in fundamental_data_time_series
        if item.outstanding_shares is not None
    ]

    if share_counts and len(share_counts) >= 3:
        if share_counts[0] < share_counts[5] * 0.95:  # 5%+ reduction in shares
            score += 2
            details.append("Shareholder-friendly: Reducing share count over time")
        elif share_counts[0] < share_counts[5] * 1.05:  # Stable share count
            score += 1
            details.append("Stable share count: Limited dilution")
        elif share_counts[0] > share_counts[5] * 1.2:  # >20% dilution
            score -= 1  # Penalty for excessive dilution
            details.append("Concerning dilution: Share count increased significantly")
        else:
            details.append("Moderate share count increase over time")
    else:
        details.append("Insufficient share count data")

    # Scale score to 0-10 range
    # Maximum possible raw score would be 10 (3+3+3+3+2+2) minus penalties
    final_score = max(0, min(10, score * 10 / 16))

    return {"score": final_score, "details": "; ".join(details)}


def calculate_margin_of_safety(
    overview: StockMetaData,
    fundamental_data_time_series: list[ProcessedFundamentalData],
) -> dict[str, any]:
    """
    Calculate intrinsic value using Munger's approach:
    - Focus on owner earnings (approximated by FCF)
    - Simple multiple on normalized earnings
    - Prefer paying a fair price for a wonderful business
    """
    score = 0
    details = []

    if not fundamental_data_time_series or overview.market_capitalization is None:
        return {"score": 0, "details": "Insufficient data to perform valuation"}

    # Get FCF values ("owner earnings")
    fcf_values = [
        item.free_cash_flow
        for item in fundamental_data_time_series
        if item.free_cash_flow is not None
    ]

    if not fcf_values or len(fcf_values) < 3:
        return {"score": 0, "details": "Insufficient free cash flow data for valuation"}

    # Normalize fcf by taking average of last 3-5 years
    normalized_fcf = sum(fcf_values[: min(5, len(fcf_values))]) / min(
        5, len(fcf_values)
    )

    if normalized_fcf <= 0:
        return {
            "score": 0,
            "details": f"Negative or zero normalized FCF ({normalized_fcf}), cannot value",
            "intrinsic_value": None,
        }

    # Calculate FCF yield (inverse of P/FCF multiple)
    if overview.market_capitalization <= 0:
        return {
            "score": 0,
            "details": f"Invalid market cap ({overview.market_capitalization}), cannot value",
        }

    fcf_yield = normalized_fcf / overview.market_capitalization

    # FCF multiple based on business quality
    # Let's use a sliding scale where higher FCF yields are more attractive
    # 10 Cap
    if fcf_yield > 0.1:
        score += 4
        details.append(f"Perfect value: {fcf_yield:.1%} FCF yield")
    elif fcf_yield > 0.08:
        score += 3
        details.append(f"Excellent value: {fcf_yield:.1%} FCF yield")
    elif fcf_yield > 0.05:
        score += 2
        details.append(f"Good value: {fcf_yield:.1%} FCF yield")
    elif fcf_yield > 0.03:
        score += 1
        details.append(f"Fair value: {fcf_yield:.1%} FCF yield")
    else:
        details.append(f"Expensive: Only {fcf_yield:.1%} FCF yield")

    # Calculate simple intrinsic value range
    # we use 10 cap as base line evaluation
    conservative_value = normalized_fcf * 10  # 10x FCF = 10% yield
    reasonable_value = normalized_fcf * 15  # 15x FCF ≈ 6.7% yield
    optimistic_value = normalized_fcf * 20  # 20x FCF = 5% yield

    # Calculate margins of safety
    current_to_conservative = (
        conservative_value - overview.market_capitalization
    ) / overview.market_capitalization

    if current_to_conservative > 0.5:  # >50% MOS
        score += 4
        details.append(
            f"Large margin of safety: {current_to_conservative:.1%} upside to conservative value"
        )
    elif current_to_conservative > 0.3:  # >30% MOS
        score += 3
        details.append(
            f"Moderate margin of safety: {current_to_conservative:.1%} upside to conservative value"
        )
    elif current_to_conservative > 0.2:  # >20% MOS
        score += 2
        details.append(
            f"Moderate margin of safety: {current_to_conservative:.1%} upside to conservative value"
        )
    elif current_to_conservative > -0.1:  # value is fair but not MOS
        score += 0
        details.append(
            f"Fair price: Within 10% of conservative value ({current_to_conservative:.1%})"
        )
    else:
        details.append(
            f"Expensive: {-current_to_conservative:.1%} premium to conservative value"
        )

    # Scale score to 0-10 range
    final_score = min(10, score * 10 / (4 + 4))

    return {
        "score": final_score,
        "details": "; ".join(details),
        "intrinsic_value_range": {
            "conservative": conservative_value,
            "reasonable": reasonable_value,
            "optimistic": optimistic_value,
        },
        "fcf_yield": fcf_yield,
        "normalized_fcf": normalized_fcf,
    }


def generate_output(
    overview: StockMetaData,
    growth_rates_analysis: dict[str, any],
    moat_analysis: dict[str, any],
    management_analysis: dict[str, any],
    valuation_analysis: dict[str, any],
) -> EvaluationSignal:
    """
    Generates investment decisions in value investing style
    """
    template = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """You are a Value Investing AI agent, making investment decisions using his principles:

                1. Focus on the quality and predictability of the business.
                2. Rely on mental models from multiple disciplines to analyze investments.
                3. Look for strong, durable competitive advantages (moats).
                4. Emphasize long-term thinking and patience.
                5. Value management integrity and competence.
                6. Prioritize businesses with high returns on invested capital and return on equity.
                7. Pay a fair price for wonderful businesses.
                8. Never overpay, always demand a margin of safety.
                9. Avoid complexity and businesses you don't understand.
                10. "Invert, always invert" - focus on avoiding stupidity rather than seeking brilliance.
                
                Rules:
                - Praise businesses with growing key growth rates revenue, income, operating cash flow and shareholder equity.
                - Praise businesses with predictable, consistent operations and cash flows.
                - Value businesses with high ROIC, ROE and pricing power.
                - Prefer simple businesses with understandable economics.
                - Admire management with skin in the game and shareholder-friendly capital allocation.
                - Focus on long-term economics rather than short-term metrics.
                - Be skeptical of businesses with rapidly changing dynamics or excessive share dilution.
                - Avoid excessive leverage or financial engineering.
                - Provide a rational, data-driven recommendation (bullish, bearish, or neutral).
                
                When providing your reasoning, be thorough and specific by:
                1. Explaining the key factors that influenced your decision the most (both positive and negative)
                2. Applying at least 2-3 specific mental models or disciplines to explain your thinking
                3. Providing quantitative evidence where relevant (e.g., specific ROIC/ROE values, margin trends, growth rates)
                4. Citing what you would "avoid" in your analysis (invert the problem)
                5. Using direct, clear conversational style in your explanation
                
                For example, if bullish: "The high ROIC of 22% demonstrates the company's moat. When applying basic microeconomics, we can see that competitors would struggle to..."
                For example, if bearish: "I see this business making a classic mistake in capital allocation. As I've often said about [relevant Mungerism], this company appears to be..."
                """,
            ),
            (
                "human",
                """Based on the following analysis, create a value investing style investment signal.

                Overview for {ticker}:
                {overview}

                Growth rates analysis for {ticker}:
                {growth_rates_analysis}

                Moat analysis for {ticker}:
                {moat_analysis}

                Management analysis for {ticker}:
                {management_analysis}

                Valuation analysis for {ticker}: 
                {valuation_analysis}
                """,
            ),
        ]
    )

    prompt = template.invoke(
        {
            "ticker": overview.symbol,
            "overview": json.dumps(overview.model_dump(), indent=2),
            "growth_rates_analysis": json.dumps(growth_rates_analysis, indent=2),
            "moat_analysis": json.dumps(moat_analysis, indent=2),
            "management_analysis": json.dumps(management_analysis, indent=2),
            "valuation_analysis": json.dumps(valuation_analysis, indent=2),
        }
    )

    return call_llm(
        prompt=prompt,
        pydantic_model=EvaluationSignal,
    )


def extract_financial_metrics(fundamental_data: FundamentalData) -> dict:
    # Implementation of extract_financial_metrics function
    pass
