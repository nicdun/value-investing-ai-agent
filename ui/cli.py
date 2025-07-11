#!/usr/bin/env python3
"""
Interactive CLI utilities using questionary for better user experience.
"""

import questionary
from questionary import Style
from typing import List, Dict, Optional
import sys


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

    def display_analysis_summary(self, data: Dict) -> None:
        """
        Display analysis summary in a nicely formatted way.

        Args:
            data: Dictionary containing analysis data
        """
        questionary.print("\n" + "=" * 60, style="fg:#ff9500 bold")
        questionary.print("📊  ANALYSIS SUMMARY", style="fg:#ff9500 bold")
        questionary.print("=" * 60, style="fg:#ff9500 bold")

        # Display basic info
        if "symbol" in data:
            questionary.print(f"Symbol: {data['symbol']}", style="bold")
        if "company_name" in data:
            questionary.print(f"Company: {data['company_name']}", style="bold")

        # Display key metrics if available
        if "overview" in data and data["overview"]:
            overview = data["overview"]
            questionary.print("\n📈 Key Metrics:", style="fg:#ff9500 bold")

            if (
                hasattr(overview, "market_capitalization")
                and overview.market_capitalization
            ):
                questionary.print(f"  Market Cap: ${overview.market_capitalization:,}")
            if hasattr(overview, "pe_ratio") and overview.pe_ratio:
                questionary.print(f"  P/E Ratio: {overview.pe_ratio}")
            if hasattr(overview, "sector") and overview.sector:
                questionary.print(f"  Sector: {overview.sector}")

        # Display data counts
        counts = data.get("data_counts", {})
        if counts:
            questionary.print("\n📋 Data Retrieved:", style="fg:#ff9500 bold")
            for data_type, count in counts.items():
                if count > 0:
                    questionary.print(
                        f"  {data_type.replace('_', ' ').title()}: {count}"
                    )

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


# Global CLI instance
_cli = StockResearchCLI()


def get_cli() -> StockResearchCLI:
    """Get the global CLI instance."""
    return _cli
