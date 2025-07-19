#!/usr/bin/env python3
"""
Interactive CLI utilities using questionary for better user experience.
"""

import questionary
from questionary import Style
from typing import List, Dict, Optional
import sys
from features.fundamental_data.model import ProcessedFundamentalData, StockMetaData


# Custom style for the CLI
custom_style = Style(
    [
        ("question", "bold"),
        ("answer", "fg:#ff9500 bold"),
        ("pointer", "fg:#ff9500 bold"),
        ("highlighted", "fg:#ff9500 bold"),
        ("selected", "fg:#cc5454"),
        ("separator", "fg:#cc5454"),
        ("instruction", ""),
        ("text", ""),
        ("disabled", "fg:#858585 italic"),
    ]
)


class StockResearchCLI:
    """Interactive CLI for stock research application."""

    def __init__(self):
        self.style = custom_style

    def welcome(self) -> None:
        """Display welcome message."""
        questionary.print("=" * 60, style="fg:#ff9500 bold")
        questionary.print("🔎  STOCK RESEARCH AGENT", style="fg:#ff9500 bold")
        questionary.print("=" * 60, style="fg:#ff9500 bold")
        questionary.print(
            "Analyze stocks with AI-powered fundamental research\n", style="fg:#858585"
        )

    def get_stock_name(self) -> str:
        """Get stock name input from user."""
        return questionary.text(
            "🏢 Enter a company name or stock symbol to research:",
            style=self.style,
            validate=lambda text: len(text.strip()) >= 2
            or "Please enter at least 2 characters",
        ).ask()

    def get_analysis_years(self) -> int:
        """Get number of years for fundamental data analysis from user."""
        years_str = questionary.text(
            "📅 Enter number of years for analysis (5-20, default: 10):",
            style=self.style,
            default="10",
            validate=lambda text: self._validate_years(text),
        ).ask()
        return int(years_str.strip())

    def _validate_years(self, text: str) -> str | bool:
        """Validate years input."""
        try:
            years = int(text.strip())
            if 5 <= years <= 20:
                return True
            else:
                return "Please enter a number between 5 and 20"
        except ValueError:
            return "Please enter a valid number"

    def select_stock_ticker(self, search_results: List[Dict]) -> Optional[str]:
        """
        Display search results and let user select a stock ticker.

        Args:
            search_results: List of stock search results from Alpha Vantage API

        Returns:
            Selected ticker symbol or None if cancelled
        """
        if not search_results:
            questionary.print("❌ No matching stocks found.", style="fg:#cc5454")
            return None

        # Format choices for questionary
        choices = []
        for match in search_results:
            symbol = match.get("1. symbol", "")
            name = match.get("2. name", "")
            region = match.get("4. region", "")
            market_type = match.get("3. type", "")

            # Create a formatted display string
            display_text = f"{symbol} - {name} ({region})"
            if market_type:
                display_text += f" [{market_type}]"

            choices.append(questionary.Choice(title=display_text, value=symbol))

        # Add option to search again
        choices.append(
            questionary.Choice(
                title="🔍 Search for a different company", value="__search_again__"
            )
        )

        questionary.print(
            f"\n📊 Found {len(search_results)} matching stocks:", style="fg:#ff9500"
        )

        selected = questionary.select(
            "Select a stock to analyze:",
            choices=choices,
            style=self.style,
        ).ask()

        return selected

    def confirm_analysis(self, symbol: str, company_name: str = "") -> bool:
        """
        Confirm user wants to proceed with analysis.

        Args:
            symbol: Stock ticker symbol
            company_name: Company name (optional)

        Returns:
            True if user confirms, False otherwise
        """
        display_name = f"{symbol}"
        if company_name:
            display_name = f"{company_name} ({symbol})"

        return questionary.confirm(
            f"🎯 Proceed with comprehensive analysis of {display_name}?",
            style=self.style,
            default=True,
        ).ask()

    def show_progress_start(self, message: str) -> None:
        """Show start of a progress step."""
        questionary.print(f"\n🔄 {message}", style="fg:#ff9500")

    def show_progress_success(self, message: str) -> None:
        """Show successful completion of a step."""
        questionary.print(f"✅ {message}", style="fg:#00aa00")

    def show_progress_success_cached(self, message: str) -> None:
        """Show successful completion of a step from cache."""
        questionary.print(f"💾 {message}", style="fg:#0099cc")

    def show_progress_success_api(self, message: str) -> None:
        """Show successful completion of a step from API."""
        questionary.print(f"🌐 {message}", style="fg:#00aa00")

    def show_progress_error(self, message: str) -> None:
        """Show error in a step."""
        questionary.print(f"❌ {message}", style="fg:#cc5454")

    def show_progress_warning(self, message: str) -> None:
        """Show warning for a step."""
        questionary.print(f"⚠️  {message}", style="fg:#ffaa00")

    def display_analysis_summary(self, data: StockMetaData) -> None:
        """
        Display analysis summary in a nicely formatted way.

        Args:
            data: Dictionary containing analysis data
        """
        questionary.print("\n" + "=" * 60, style="fg:#ff9500 bold")
        questionary.print("📊  ANALYSIS SUMMARY", style="fg:#ff9500 bold")
        questionary.print("=" * 60, style="fg:#ff9500 bold")

        questionary.print(f"Symbol: {data.symbol}", style="bold")
        questionary.print(f"Company: {data.name}", style="bold")

        # Display key metrics if available
        questionary.print("\n📈 Key Metrics:", style="fg:#ff9500 bold")

        if data.market_capitalization:
            questionary.print(f"  Market Cap: ${data.market_capitalization}")
        if data.pe_ratio:
            questionary.print(f"  P/E Ratio: {data.pe_ratio}")
        if data.sector:
            questionary.print(f"  Sector: {data.sector}")
        if data.dividend_yield:
            questionary.print(f"  Industry: {data.industry}")
        if data.dividend_per_share:
            questionary.print(f"  Dividend Per Share: {data.dividend_per_share}")
        if data.dividend_yield:
            questionary.print(f"  Dividend Yield: {data.dividend_yield}")
        if data.eps:
            questionary.print(f"  EPS: {data.eps}")

    def show_analysis_options(self) -> str:
        """
        Show post-analysis options menu.

        Returns:
            Selected option
        """
        choices = [
            questionary.Choice("📊 View detailed report", value="view_report"),
            questionary.Choice("🔍 Analyze another stock", value="analyze_another"),
            questionary.Choice("🚪 Exit", value="exit"),
        ]

        return questionary.select(
            "\nWhat would you like to do next?", choices=choices, style=self.style
        ).ask()

    def display_error(self, error_message: str) -> None:
        """Display error message."""
        questionary.print(f"\n❌ Error: {error_message}", style="fg:#cc5454 bold")

    def display_warning(self, warning_message: str) -> None:
        """Display warning message."""
        questionary.print(f"\n⚠️  Warning: {warning_message}", style="fg:#ffaa00 bold")

    def display_info(self, info_message: str) -> None:
        """Display info message."""
        questionary.print(f"\nℹ️  {info_message}", style="fg:#85c5f7")

    def show_info(self, message: str) -> None:
        """Show info message without extra formatting."""
        questionary.print(message, style="fg:#85c5f7")

    def show_warning(self, message: str) -> None:
        """Show warning message."""
        questionary.print(f"⚠️  {message}", style="fg:#ffaa00")

    def ask_yes_no(self, question: str, default: bool = True) -> bool:
        """
        Ask a yes/no question.

        Args:
            question: Question to ask
            default: Default answer

        Returns:
            True for yes, False for no
        """
        return questionary.confirm(question, style=self.style, default=default).ask()

    def goodbye(self) -> None:
        """Display goodbye message."""
        questionary.print("\n" + "=" * 60, style="fg:#ff9500 bold")
        questionary.print(
            "👋 Thank you for using Stock Research Agent!", style="fg:#ff9500 bold"
        )
        questionary.print("Happy investing! 📈", style="fg:#85c5f7")
        questionary.print("=" * 60, style="fg:#ff9500 bold")

    def print_fundamental_data_time_series(
        self, symbol: str, time_series: list[ProcessedFundamentalData]
    ):
        """Print the calculated financial time series data as a table."""

        if not time_series:
            self.show_warning("No financial time series data available")
            return

        self.show_info(f"\nFinancial Time Series for {symbol}")
        self.show_info("=" * 130)

        # Headers
        headers = [
            "Year",
            "Revenue (M)",
            "Rev%",
            "Net Income (M)",
            "NI%",
            "Operating CF (M)",
            "OCF%",
            "Free CF (M)",
            "FCF%",
            "Gross Margin",
            "ROIC",
            "ROE",
            "D/E",
            "Shares (M)",
        ]

        # Prepare all data rows first to calculate column widths
        data_rows = []
        colored_rows = []  # Store colored versions for display

        for i, period in enumerate(time_series):
            year = period.fiscal_date_ending[:4] if period.fiscal_date_ending else "N/A"

            revenue = period.revenue
            revenue_str = f"{revenue / 1_000_000:.1f}" if revenue else "N/A"

            net_income = period.net_income
            net_income_str = f"{net_income / 1_000_000:.1f}" if net_income else "N/A"

            operating_cashflow = period.operating_cashflow
            operating_cashflow_str = (
                f"{operating_cashflow / 1_000_000:.1f}" if operating_cashflow else "N/A"
            )
            fcf = period.free_cash_flow
            fcf_str = f"{fcf / 1_000_000:.1f}" if fcf else "N/A"

            # Calculate growth rates compared to previous year
            revenue_growth_str = "N/A"
            net_income_growth_str = "N/A"
            operating_cf_growth_str = "N/A"
            fcf_growth_str = "N/A"

            if i < len(time_series) - 1:  # Not the oldest year
                prev_period = time_series[i + 1]

                # Revenue growth
                if revenue and prev_period.revenue:
                    revenue_growth = (
                        (revenue - prev_period.revenue) / prev_period.revenue
                    ) * 100
                    revenue_growth_str = f"{revenue_growth:+.1f}%"

                # Net income growth
                if net_income and prev_period.net_income:
                    net_income_growth = (
                        (net_income - prev_period.net_income) / prev_period.net_income
                    ) * 100
                    net_income_growth_str = f"{net_income_growth:+.1f}%"

                # Operating cashflow growth
                if operating_cashflow and prev_period.operating_cashflow:
                    operating_cf_growth = (
                        (operating_cashflow - prev_period.operating_cashflow)
                        / prev_period.operating_cashflow
                    ) * 100
                    operating_cf_growth_str = f"{operating_cf_growth:+.1f}%"

                # FCF growth
                if fcf and prev_period.free_cash_flow:
                    fcf_growth = (
                        (fcf - prev_period.free_cash_flow) / prev_period.free_cash_flow
                    ) * 100
                    fcf_growth_str = f"{fcf_growth:+.1f}%"

            gross_margin = period.gross_margin
            gross_margin_str = f"{gross_margin:.1%}" if gross_margin else "N/A"

            roic = period.return_on_invested_capital
            roic_str = f"{roic:.1%}" if roic else "N/A"

            roe = period.return_on_equity
            roe_str = f"{roe:.1%}" if roe else "N/A"

            debt_to_equity = period.debt_to_equity_ratio
            debt_to_equity_str = f"{debt_to_equity:.2f}" if debt_to_equity else "N/A"

            shares = period.outstanding_shares
            shares_str = f"{shares / 1_000_000:.1f}" if shares else "N/A"

            row_data = [
                year,
                revenue_str,
                revenue_growth_str,
                net_income_str,
                net_income_growth_str,
                operating_cashflow_str,
                operating_cf_growth_str,
                fcf_str,
                fcf_growth_str,
                gross_margin_str,
                roic_str,
                roe_str,
                debt_to_equity_str,
                shares_str,
            ]
            data_rows.append(row_data)

        # Calculate column widths (more compact)
        column_widths = []
        for i, header in enumerate(headers):
            # Start with header width
            max_width = len(header)

            # Check all data rows for this column
            for row in data_rows:
                if i < len(row):
                    max_width = max(max_width, len(str(row[i])))

            # Add minimal padding, extra space for growth columns to fit emoji
            if i in [2, 4, 6, 8]:  # Growth columns
                column_widths.append(max_width + 3)  # Extra space for emoji
            else:
                column_widths.append(max_width + 1)

        # Format and print header
        header_line = " | ".join(f"{h:>{w}}" for h, w in zip(headers, column_widths))
        self.show_info(header_line)

        # Print separator line
        separator_line = "-+-".join("-" * w for w in column_widths)
        self.show_info(separator_line)

        # Print data rows with colored growth values
        for row in data_rows:
            # Build the row line piece by piece to handle coloring
            output_line = ""

            for i, (data, width) in enumerate(zip(row, column_widths)):
                # Add separator except for first column
                if i > 0:
                    output_line += " | "

                # Apply colors to growth columns (indices 2, 4, 6, 8)
                if i in [2, 4, 6, 8] and data != "N/A":
                    if data.startswith("+"):
                        # Green for positive growth - format with emoji within width
                        formatted_data = f"🟢{data:>{width - 2}}"
                    elif data.startswith("-"):
                        # Red for negative growth - format with emoji within width
                        formatted_data = f"🔴{data:>{width - 2}}"
                    else:
                        formatted_data = f"{data:>{width}}"
                    output_line += formatted_data
                else:
                    formatted_data = f"{data:>{width}}"
                    output_line += formatted_data

            self.show_info(output_line)

        self.show_info("")


# Global CLI instance
_cli = StockResearchCLI()


def get_cli() -> StockResearchCLI:
    """Get the global CLI instance."""
    return _cli
