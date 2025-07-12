from workflow.workflow import Workflow
from workflow.model import ResearchState
from ui.cli import get_cli, StockResearchCLI
import json
import sys


def main():
    cli = get_cli()

    try:
        while True:
            workflow = Workflow()
            final_state = workflow.run()

            # Check if analysis was completed successfully
            if not final_state.ticker_symbol:
                # User cancelled or analysis failed
                if cli.ask_yes_no("Would you like to try analyzing a different stock?"):
                    continue
                else:
                    break

            # Show analysis completion and options
            if final_state.report:
                cli.display_info("Analysis completed successfully!")

                # Show post-analysis options
                while True:
                    option = cli.show_analysis_options()

                    if option == "view_report":
                        display_detailed_report(final_state, cli)

                    elif option == "analyze_another":
                        break  # Break inner loop to start new analysis

                    elif option == "exit":
                        return

                    else:
                        break  # Break if no valid option

                # Continue with new analysis if "analyze_another" was selected
                if option == "analyze_another":
                    continue
                else:
                    break
            else:
                cli.display_warning("Analysis completed but no report was generated.")
                if cli.ask_yes_no("Would you like to try analyzing a different stock?"):
                    continue
                else:
                    break

    except KeyboardInterrupt:
        cli.display_info("\nExiting...")
    except Exception as e:
        cli.display_error(f"An unexpected error occurred: {str(e)}")
        raise e
    finally:
        cli.goodbye()


def display_detailed_report(state: ResearchState, cli: StockResearchCLI):
    """Display the detailed analysis report."""
    if not state.report:
        cli.display_error("No report available to display.")
        return

    cli.display_info("📊 DETAILED ANALYSIS REPORT")
    cli.display_info("=" * 60)

    # Display basic info
    if state.ticker_symbol:
        cli.display_info(f"Symbol: {state.ticker_symbol}")

    if state.fundamental_data and state.fundamental_data.overview:
        overview = state.fundamental_data.overview
        if hasattr(overview, "name") and overview.name:
            cli.display_info(f"Company: {overview.name}")

    cli.display_info("=" * 60)

    # Display the main report content
    print("\n" + state.report.report + "\n")

    cli.display_info("=" * 60)
    input("Press Enter to continue...")


if __name__ == "__main__":
    main()
