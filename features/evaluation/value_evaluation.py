from features.fundamental_data.model import FundamentalData
from ui.cli import get_cli
from langchain_core.prompts import ChatPromptTemplate
import json
from features.llm.llm import call_llm
from features.evaluation.model import EvaluationSignal
from features.fundamental_data.model import StockMetaData
from features.fundamental_data.model import ProcessedFundamentalData

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

    # Show additional metrics for valuation analysis
    if "intrinsic_value_range" in analysis_result:
        cli.show_info("\n💰 Valuation Metrics:")
        intrinsic_range = analysis_result["intrinsic_value_range"]
        cli.show_info(f"   Conservative Value: ${intrinsic_range['conservative']:,.0f}")
        cli.show_info(f"   Reasonable Value:   ${intrinsic_range['reasonable']:,.0f}")
        cli.show_info(f"   Optimistic Value:   ${intrinsic_range['optimistic']:,.0f}")

        fcf_yield = analysis_result.get("fcf_yield", 0)
        cli.show_info(f"   FCF Yield:          {fcf_yield:.1%}")

    cli.show_info("")


def evaluate(
    overview: StockMetaData,
    fundamental_data_time_series: list[ProcessedFundamentalData],
) -> str:
    # Perform analyses
    cli.show_progress_start("Business Model: Analyzing business predictability")
    # predictability_analysis = analyze_predictability(fundamental_data)

    cli.show_progress_start("MOAT: Analyzing moat strength")
    moat_analysis = analyze_moat_strength(fundamental_data_time_series)
    cli.show_progress_success("MOAT analysis completed")
    print_analysis_results("MOAT", moat_analysis)

    cli.show_progress_start("Management: Analyzing management quality")
    management_analysis = analyze_management_quality(fundamental_data_time_series)
    print_analysis_results("Management Quality", management_analysis)

    cli.show_progress_start("Margin of Safety: Calculating valuation")
    valuation_analysis = calculate_margin_of_safety(
        overview, fundamental_data_time_series
    )
    cli.show_progress_success("Valuation analysis completed")
    print_analysis_results("Margin of Safety", valuation_analysis)

    cli.show_progress_start("Generating final analysis...")
    output = generate_output(
        overview,
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
    - Consistent high returns on capital (ROIC)
    - Pricing power (stable/improving gross margins)
    - Low capital requirements
    - Network effects and intangible assets (R&D investments, goodwill)
    """
    score = 0
    details = []

    if not fundamental_data_time_series:
        return {"score": 0, "details": "Insufficient data to analyze moat strength"}

    # 1. Return on Invested Capital (ROIC) analysis - Munger's favorite metric
    roic_values = [
        item.return_on_invested_capital
        for item in fundamental_data_time_series
        if item.return_on_invested_capital is not None
    ]

    if roic_values:
        # Check if ROIC consistently above 15% (Munger's threshold)
        high_roic_count = sum(1 for r in roic_values if r > 0.15)
        if high_roic_count >= len(roic_values) * 0.8:  # 80% of periods show high ROIC
            score += 3
            details.append(
                f"Excellent ROIC: >15% in {high_roic_count}/{len(roic_values)} periods"
            )
        elif high_roic_count >= len(roic_values) * 0.5:  # 50% of periods
            score += 2
            details.append(
                f"Good ROIC: >15% in {high_roic_count}/{len(roic_values)} periods"
            )
        elif high_roic_count > 0:
            score += 1
            details.append(
                f"Mixed ROIC: >15% in only {high_roic_count}/{len(roic_values)} periods"
            )
        else:
            details.append("Poor ROIC: Never exceeds 15% threshold")
    else:
        details.append("No ROIC data available")

    # 2. Pricing power - check gross margin stability and trends
    gross_margins = [
        item.gross_margin
        for item in fundamental_data_time_series
        if item.gross_margin is not None
    ]

    if gross_margins and len(gross_margins) >= 3:
        # Munger likes stable or improving gross margins
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

    # 3. Capital intensity - Munger prefers low capex businesses
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

    # 4. Intangible assets - Munger values R&D and intellectual property
    r_and_d = [
        item.research_and_development
        for item in fundamental_data_time_series
        if item.research_and_development is not None
    ]

    goodwill_and_intangible_assets = [
        item.goodwill_and_intangible_assets
        for item in fundamental_data_time_series
        if item.goodwill_and_intangible_assets is not None
    ]

    if r_and_d and len(r_and_d) > 0:
        if sum(r_and_d) > 0:  # If company is investing in R&D
            score += 1
            details.append("Invests in R&D, building intellectual property")

    if goodwill_and_intangible_assets and len(goodwill_and_intangible_assets) > 0:
        score += 1
        details.append(
            "Significant goodwill/intangible assets, suggesting brand value or IP"
        )

    # Scale score to 0-10 range
    final_score = min(10, score * 10 / 9)  # Max possible raw score is 9

    return {"score": final_score, "details": "; ".join(details)}


def analyze_management_quality(
    fundamental_data_time_series: list[ProcessedFundamentalData],
) -> dict[str, any]:
    """
    Evaluate management quality using Munger's criteria:
    - Capital allocation wisdom
    - Insider ownership and transactions
    - Cash management efficiency
    - Candor and transparency
    - Long-term focus
    """
    score = 0
    details = []

    # Get financial time series data
    if not fundamental_data_time_series:
        return {
            "score": 0,
            "details": "Insufficient data to analyze management quality",
        }

    # 1. Capital allocation - Check FCF to net income ratio
    # Munger values companies that convert earnings to cash
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

    # 2. Debt management - Munger is cautious about debt
    debt_values = [
        item.total_debt
        for item in fundamental_data_time_series
        if item.total_debt is not None
    ]

    equity_values = [
        item.shareholders_equity
        for item in fundamental_data_time_series
        if item.shareholders_equity is not None
    ]

    if debt_values and equity_values and len(debt_values) == len(equity_values):
        # Calculate D/E ratio for most recent period
        recent_de_ratio = (
            debt_values[0] / equity_values[0] if equity_values[0] > 0 else float("inf")
        )

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
        else:
            details.append(f"High debt level: D/E ratio of {recent_de_ratio:.2f}")
    else:
        details.append("Missing debt or equity data")

    # 3. Cash management efficiency - Munger values appropriate cash levels
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

    # 4. Insider activity - Note: Not available in current data model
    # This would require additional data sources
    details.append("Insider trading data not available in current dataset")

    # 5. Consistency in share count - Munger prefers stable/decreasing shares
    share_counts = [
        item.outstanding_shares
        for item in fundamental_data_time_series
        if item.outstanding_shares is not None
    ]

    if share_counts and len(share_counts) >= 3:
        if share_counts[0] < share_counts[-1] * 0.95:  # 5%+ reduction in shares
            score += 2
            details.append("Shareholder-friendly: Reducing share count over time")
        elif share_counts[0] < share_counts[-1] * 1.05:  # Stable share count
            score += 1
            details.append("Stable share count: Limited dilution")
        elif share_counts[0] > share_counts[-1] * 1.2:  # >20% dilution
            score -= 1  # Penalty for excessive dilution
            details.append("Concerning dilution: Share count increased significantly")
        else:
            details.append("Moderate share count increase over time")
    else:
        details.append("Insufficient share count data")

    # Scale score to 0-10 range
    # Maximum possible raw score would be 10 (3+3+2+2) minus penalties
    final_score = max(0, min(10, score * 10 / 10))

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

    # Get FCF values (Munger's preferred "owner earnings" metric)
    fcf_values = [
        item.free_cash_flow
        for item in fundamental_data_time_series
        if item.free_cash_flow is not None
    ]

    if not fcf_values or len(fcf_values) < 3:
        return {"score": 0, "details": "Insufficient free cash flow data for valuation"}

    # 1. Normalize earnings by taking average of last 3-5 years
    # (Munger prefers to normalize earnings to avoid over/under-valuation based on cyclical factors)
    normalized_fcf = sum(fcf_values[: min(5, len(fcf_values))]) / min(
        5, len(fcf_values)
    )

    if normalized_fcf <= 0:
        return {
            "score": 0,
            "details": f"Negative or zero normalized FCF ({normalized_fcf}), cannot value",
            "intrinsic_value": None,
        }

    # 2. Calculate FCF yield (inverse of P/FCF multiple)
    if overview.market_capitalization <= 0:
        return {
            "score": 0,
            "details": f"Invalid market cap ({overview.market_capitalization}), cannot value",
        }

    fcf_yield = normalized_fcf / overview.market_capitalization

    # 3. Apply Munger's FCF multiple based on business quality
    # Munger would pay higher multiples for wonderful businesses
    # Let's use a sliding scale where higher FCF yields are more attractive
    if fcf_yield > 0.08:  # >8% FCF yield (P/FCF < 12.5x)
        score += 4
        details.append(f"Excellent value: {fcf_yield:.1%} FCF yield")
    elif fcf_yield > 0.05:  # >5% FCF yield (P/FCF < 20x)
        score += 3
        details.append(f"Good value: {fcf_yield:.1%} FCF yield")
    elif fcf_yield > 0.03:  # >3% FCF yield (P/FCF < 33x)
        score += 1
        details.append(f"Fair value: {fcf_yield:.1%} FCF yield")
    else:
        details.append(f"Expensive: Only {fcf_yield:.1%} FCF yield")

    # 4. Calculate simple intrinsic value range
    # Munger tends to use straightforward valuations, avoiding complex DCF models
    conservative_value = normalized_fcf * 10  # 10x FCF = 10% yield
    reasonable_value = normalized_fcf * 15  # 15x FCF ≈ 6.7% yield
    optimistic_value = normalized_fcf * 20  # 20x FCF = 5% yield

    # 5. Calculate margins of safety
    current_to_reasonable = (
        reasonable_value - overview.market_capitalization
    ) / overview.market_capitalization

    if current_to_reasonable > 0.3:  # >30% upside
        score += 3
        details.append(
            f"Large margin of safety: {current_to_reasonable:.1%} upside to reasonable value"
        )
    elif current_to_reasonable > 0.1:  # >10% upside
        score += 2
        details.append(
            f"Moderate margin of safety: {current_to_reasonable:.1%} upside to reasonable value"
        )
    elif current_to_reasonable > -0.1:  # Within 10% of reasonable value
        score += 1
        details.append(
            f"Fair price: Within 10% of reasonable value ({current_to_reasonable:.1%})"
        )
    else:
        details.append(
            f"Expensive: {-current_to_reasonable:.1%} premium to reasonable value"
        )

    # 6. Check earnings trajectory for additional context
    # Munger likes growing owner earnings
    if len(fcf_values) >= 3:
        recent_avg = sum(fcf_values[:3]) / 3
        older_avg = sum(fcf_values[-3:]) / 3 if len(fcf_values) >= 6 else fcf_values[-1]

        if recent_avg > older_avg * 1.2:  # >20% growth in FCF
            score += 3
            details.append("Growing FCF trend adds to intrinsic value")
        elif recent_avg > older_avg:
            score += 2
            details.append("Stable to growing FCF supports valuation")
        else:
            details.append("Declining FCF trend is concerning")

    # Scale score to 0-10 range
    # Maximum possible raw score would be 10 (4+3+3)
    final_score = min(10, score * 10 / 10)

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
    moat_analysis: dict[str, any],
    management_analysis: dict[str, any],
    valuation_analysis: dict[str, any],
):
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
                6. Prioritize businesses with high returns on invested capital.
                7. Pay a fair price for wonderful businesses.
                8. Never overpay, always demand a margin of safety.
                9. Avoid complexity and businesses you don't understand.
                10. "Invert, always invert" - focus on avoiding stupidity rather than seeking brilliance.
                
                Rules:
                - Praise businesses with predictable, consistent operations and cash flows.
                - Value businesses with high ROIC and pricing power.
                - Prefer simple businesses with understandable economics.
                - Admire management with skin in the game and shareholder-friendly capital allocation.
                - Focus on long-term economics rather than short-term metrics.
                - Be skeptical of businesses with rapidly changing dynamics or excessive share dilution.
                - Avoid excessive leverage or financial engineering.
                - Provide a rational, data-driven recommendation (bullish, bearish, or neutral).
                
                When providing your reasoning, be thorough and specific by:
                1. Explaining the key factors that influenced your decision the most (both positive and negative)
                2. Applying at least 2-3 specific mental models or disciplines to explain your thinking
                3. Providing quantitative evidence where relevant (e.g., specific ROIC values, margin trends)
                4. Citing what you would "avoid" in your analysis (invert the problem)
                5. Using Charlie Munger's direct, pithy conversational style in your explanation
                
                For example, if bullish: "The high ROIC of 22% demonstrates the company's moat. When applying basic microeconomics, we can see that competitors would struggle to..."
                For example, if bearish: "I see this business making a classic mistake in capital allocation. As I've often said about [relevant Mungerism], this company appears to be..."
                """,
            ),
            (
                "human",
                """Based on the following analysis, create a value investing style investment signal.

                Overview for {ticker}:
                {overview}

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
