def calculate_average_growth_rate(
    values: list,
    metric_name: str,
    excellent_threshold: float = 0.1,
    good_threshold: float = 0.05,
    max_score: int = 3,
) -> tuple[int, list[str]]:
    """
    Analyze growth rate for a specific financial metric.

    Args:
        values: List of values to calculate the average growth rate for
        metric_name: Display name for the metric (e.g., "revenue", "equity")
        attribute_name: Attribute name in the data objects (e.g., "revenue", "shareholders_equity")
        excellent_threshold: Growth rate threshold for excellent score (default: 10%)
        good_threshold: Growth rate threshold for good score (default: 5%)
        max_score: Maximum score to award for excellent growth (default: 3)

    Returns:
        Tuple of (score, details) where score is int and details is list of strings
    """
    score = 0
    details = []

    if not values:
        details.append(f"No {metric_name} data available")
        return score, details

    # Calculate growth rates
    recent_values = values[:10]  # Use last 10 periods
    growth_rates = []

    for i in range(1, len(recent_values)):
        prev = recent_values[i]
        curr = recent_values[i - 1]
        if prev is not None and prev != 0 and curr is not None:
            growth = (curr - prev) / abs(prev)
            growth_rates.append(growth)

    if not growth_rates:
        details.append(f"No {metric_name} growth data available")
        return score, details

    # Calculate average growth rate
    avg_growth = sum(growth_rates) / len(growth_rates)

    # Score based on growth rate
    if avg_growth > excellent_threshold:
        score += max_score
        details.append(f"Excellent {metric_name} growth: {avg_growth:.1%}")
    elif avg_growth > good_threshold:
        score += max(1, max_score - 1)  # Award second-tier score
        details.append(f"Good {metric_name} growth: {avg_growth:.1%}")
    elif avg_growth > 0:
        score += max(1, max_score - 2)  # Award minimal score for positive growth
        details.append(f"Positive {metric_name} growth: {avg_growth:.1%}")
    else:
        score -= 1  # Deduct due to negative growth
        details.append(f"Poor {metric_name} growth: {avg_growth:.1%}")

    return score, details
