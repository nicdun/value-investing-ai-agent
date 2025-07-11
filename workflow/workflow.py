from datetime import datetime

from langchain.chat_models import init_chat_model
from langchain.prompts import PromptTemplate
from langchain_core.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import END, START, StateGraph

from config.env import GOOGLE_API_KEY
from features.fundamental_data.alphavantage_adapter import AlphaVantageAPI
from features.fundamental_data.model import FundamentalData
from features.llm.google_genai import get_google_genai_llm
from features.evaluation.value_evaluation import evaluate
from features.research.firecrawl_adapter import FirecrawlAdapter
from features.research.pdf_agent import PdfAgent
from ui.cli import get_cli
from workflow.model import ResearchState
from workflow.prompts import GenericPrompts


class Workflow:
    def __init__(self):
        self.llm = get_google_genai_llm()
        self.firecrawl = FirecrawlAdapter()
        self.workflow = self._build_workflow()
        self.prompts = GenericPrompts()
        self.pdf_agent = PdfAgent()
        self.cli = get_cli()

    def _build_workflow(self):
        graph_builder = StateGraph(ResearchState)

        graph_builder.add_edge(START, "retrieve_user_input")
        graph_builder.add_node("retrieve_user_input", self._retrieve_user_input)
        graph_builder.add_node("retrieve_ticker_symbol", self._retrieve_ticker_symbol)
        graph_builder.add_node("retrieve_ticker_data", self._retrieve_ticker_data)
        graph_builder.add_node("analyze_ticker_data", self._analyze_ticker_data)
        # graph_builder.add_node("web_research", self._web_research)
        # graph_builder.add_node("analyze_web_research", self._analyze_web_research)
        # graph_builder.add_node("generate_report", self.generate_report)
        # graph_builder.add_node("investment_decision", self.investment_decision)
        graph_builder.add_edge("retrieve_user_input", "retrieve_ticker_symbol")
        graph_builder.add_edge("retrieve_ticker_symbol", "retrieve_ticker_data")
        graph_builder.add_edge("retrieve_ticker_data", "analyze_ticker_data")
        # graph_builder.add_edge("analyze_ticker_data", "web_research")
        # graph_builder.add_edge("web_research", "analyze_web_research")
        graph_builder.add_edge("analyze_ticker_data", END)

        return graph_builder.compile()

    def run(self) -> ResearchState:
        # Show welcome message
        self.cli.welcome()

        try:
            initial_state = ResearchState()
            final_state = self.workflow.invoke(initial_state)
            return ResearchState(**final_state)
        except KeyboardInterrupt:
            self.cli.display_info("Analysis cancelled by user.")
            return ResearchState()
        except Exception as e:
            self.cli.display_error(f"An error occurred during analysis: {str(e)}")
            raise e
            return ResearchState()

    def _retrieve_user_input(self, state: ResearchState) -> dict:
        """Get user input for stock name using questionary."""
        try:
            user_input = self.cli.get_stock_name()
            if not user_input:
                # User cancelled input
                return {}

            return {"messages": [HumanMessage(content=user_input)]}
        except KeyboardInterrupt:
            self.cli.display_info("Search cancelled.")
            return {}

    def _retrieve_ticker_symbol(self, state: ResearchState) -> dict:
        """Search for stock ticker and let user select from results."""
        if not state.messages:
            return {}

        search_query = state.messages[-1].content
        self.cli.show_progress_start(
            f"Searching for stocks matching '{search_query}'..."
        )

        try:
            # Get search results from Alpha Vantage
            search_result = AlphaVantageAPI.get_ticker_symbol(search_query)

            if not search_result.data:
                self.cli.show_progress_error("No matching stocks found.")
                # Ask if user wants to try again
                if self.cli.ask_yes_no(
                    "Would you like to search for a different company?"
                ):
                    return self._retrieve_user_input(state)
                else:
                    return {}

            # Show cache vs API source information
            if search_result.from_cache:
                cache_time = (
                    search_result.cache_timestamp[:19]
                    if search_result.cache_timestamp
                    else "unknown time"
                )
                self.cli.show_progress_success_cached(
                    f"Found {len(search_result.data)} matching stocks from cache"
                )
            else:
                self.cli.show_progress_success_api(
                    f"Found {len(search_result.data)} matching stocks from Alpha Vantage API"
                )

                # Let user select from results
            while True:
                selected_ticker = self.cli.select_stock_ticker(search_result.data)

                if not selected_ticker:
                    # User cancelled selection
                    return {}

                if selected_ticker == "__search_again__":
                    # User wants to search again
                    return self._retrieve_user_input(state)

                # Get company name for confirmation
                company_name = ""
                for match in search_result.data:
                    if match.get("1. symbol") == selected_ticker:
                        company_name = match.get("2. name", "")
                        break

                # Confirm with user
                if self.cli.confirm_analysis(selected_ticker, company_name):
                    return {"ticker_symbol": selected_ticker}
                else:
                    # User wants to select a different stock
                    continue

        except Exception as e:
            self.cli.show_progress_error(f"Error searching for stocks: {str(e)}")
            return {}

    def _retrieve_ticker_data(self, state: ResearchState) -> dict:
        """Retrieve fundamental data for the selected ticker."""
        if not state.ticker_symbol:
            return {}

        self.cli.show_progress_start(
            f"Analyzing fundamental data for {state.ticker_symbol}"
        )

        try:
            # Fetch all fundamental data
            self.cli.show_progress_start("Fetching company overview...")
            overview_result = AlphaVantageAPI.get_ticker_overview(state.ticker_symbol)
            if overview_result.data:
                if overview_result.from_cache:
                    cache_time = (
                        overview_result.cache_timestamp[:19]
                        if overview_result.cache_timestamp
                        else "unknown time"
                    )
                    self.cli.show_progress_success_cached(
                        f"Company overview retrieved from cache (saved at {cache_time})"
                    )
                else:
                    self.cli.show_progress_success_api(
                        "Company overview retrieved from Alpha Vantage API"
                    )
            else:
                self.cli.show_progress_warning("Company overview not available")

            self.cli.show_progress_start("Fetching balance sheet data...")
            balance_sheet_result = AlphaVantageAPI.get_balance_sheet(
                state.ticker_symbol
            )
            if balance_sheet_result.data and len(balance_sheet_result.data) > 0:
                periods_count = len(balance_sheet_result.data)
                if balance_sheet_result.from_cache:
                    cache_time = (
                        balance_sheet_result.cache_timestamp[:19]
                        if balance_sheet_result.cache_timestamp
                        else "unknown time"
                    )
                    self.cli.show_progress_success_cached(
                        f"Balance sheet retrieved ({periods_count} periods) from cache (saved at {cache_time})"
                    )
                else:
                    self.cli.show_progress_success_api(
                        f"Balance sheet retrieved ({periods_count} periods) from Alpha Vantage API"
                    )
            else:
                self.cli.show_progress_warning("Balance sheet data not available")

            self.cli.show_progress_start("Fetching income statement...")
            income_statement_result = AlphaVantageAPI.get_income_statement(
                state.ticker_symbol
            )
            if income_statement_result.data and len(income_statement_result.data) > 0:
                periods_count = len(income_statement_result.data)
                if income_statement_result.from_cache:
                    cache_time = (
                        income_statement_result.cache_timestamp[:19]
                        if income_statement_result.cache_timestamp
                        else "unknown time"
                    )
                    self.cli.show_progress_success_cached(
                        f"Income statement retrieved ({periods_count} periods) from cache (saved at {cache_time})"
                    )
                else:
                    self.cli.show_progress_success_api(
                        f"Income statement retrieved ({periods_count} periods) from Alpha Vantage API"
                    )
            else:
                self.cli.show_progress_warning("Income statement data not available")

            self.cli.show_progress_start("Fetching cash flow data...")
            cash_flow_result = AlphaVantageAPI.get_cash_flow(state.ticker_symbol)
            if cash_flow_result.data and len(cash_flow_result.data) > 0:
                periods_count = len(cash_flow_result.data)
                if cash_flow_result.from_cache:
                    cache_time = (
                        cash_flow_result.cache_timestamp[:19]
                        if cash_flow_result.cache_timestamp
                        else "unknown time"
                    )
                    self.cli.show_progress_success_cached(
                        f"Cash flow retrieved ({periods_count} periods) from cache (saved at {cache_time})"
                    )
                else:
                    self.cli.show_progress_success_api(
                        f"Cash flow retrieved ({periods_count} periods) from Alpha Vantage API"
                    )
            else:
                self.cli.show_progress_warning("Cash flow data not available")

            # Create fundamental data object using the actual data from results
            fundamental_data = FundamentalData(
                symbol=state.ticker_symbol,
                last_updated=datetime.now().isoformat(),
                overview=overview_result.data,
                balance_sheet=balance_sheet_result.data or [],
                income_statement=income_statement_result.data or [],
                cash_flow=cash_flow_result.data or [],
            )

            # Display summary
            summary_data = {
                "symbol": state.ticker_symbol,
                "company_name": overview_result.data.name
                if overview_result.data
                else "",
                "overview": overview_result.data,
                "data_counts": {
                    "balance_sheet_periods": len(balance_sheet_result.data)
                    if balance_sheet_result.data
                    else 0,
                    "income_statement_periods": len(income_statement_result.data)
                    if income_statement_result.data
                    else 0,
                    "cash_flow_periods": len(cash_flow_result.data)
                    if cash_flow_result.data
                    else 0,
                },
            }
            self.cli.display_analysis_summary(summary_data)

            return {"fundamental_data": fundamental_data}

        except Exception as e:
            self.cli.show_progress_error(f"Error analyzing fundamental data: {str(e)}")
            return {}

    def _analyze_ticker_data(self, state: ResearchState) -> dict:
        """Analyze fundamental data for the selected ticker."""
        if not state.ticker_symbol or not state.fundamental_data:
            return {}

        self.cli.show_progress_start("Analyzing fundamental data...")

        calculated_metrics = evaluate(state.fundamental_data)

        self.cli.show_progress_success("Fundamental data analysis completed")

        return {"calculated_metrics": calculated_metrics}

    def _web_research(self, state: ResearchState) -> dict:
        """Perform web research for the company."""
        self.cli.show_progress_start("Starting web research...")

        # Get company information from fundamental data
        if not state.fundamental_data or not state.fundamental_data.overview:
            self.cli.show_progress_error(
                "No fundamental data available for web research"
            )
            return {}

        company_name = (
            state.fundamental_data.overview.name
            if hasattr(state.fundamental_data.overview, "name")
            else ""
        )
        ticker_symbol = state.ticker_symbol

        if not company_name:
            self.cli.show_progress_error("No company name found in fundamental data")
            return {}

        self.cli.show_progress_start(f"Researching: {company_name} ({ticker_symbol})")

        try:
            self.cli.show_progress_start("Finding investor relations pages...")
            # ir_pages = self.firecrawl.find_investor_relations_pages(
            #     company_name, ticker_symbol
            # )
            ir_pages = [
                {
                    "title": "Investor Relations",
                    "url": "https://www.apple.com/investor-relations/",
                }
            ]
            self.cli.show_progress_success(
                f"Found {len(ir_pages)} investor relations pages"
            )
            for page in ir_pages:
                title = page.get("title", "No Title")
                url = page.get("url", "")
                self.cli.display_info(f"IR Page: {title} - {url}")

            pdf_links = self.pdf_agent.extract_pdf_links_with_llm(
                ir_pages, company_name
            )

            self.cli.show_progress_start("Crawling for quarterly reports...")
            reports = self.firecrawl.crawl_quarterly_reports(pdf_links)
            self.cli.show_progress_success(f"Found {len(reports)} quarterly reports")

            self.cli.show_progress_start("Searching for recent news...")
            # recent_news = self.firecrawl.search_recent_news(company_name, ticker_symbol)
            # self.cli.show_progress_success(f"Found {len(recent_news)} recent news items")

            self.cli.show_progress_success("Web research completed")
            return {"reports": reports}

        except Exception as e:
            self.cli.show_progress_error(f"Error during web research: {str(e)}")
            # Return empty dict if research fails
            return {}

    def _analyze_web_research(self, state: ResearchState) -> dict:
        """Analyze the collected web research data."""
        self.cli.show_progress_start("Analyzing web research data...")

        prompt = PromptTemplate(
            template=self.prompts.analyze_ticker_user,
            input_variables=[
                "company_name",
                "ticker",
                "reports_summary",
                "news_summary",
            ],
        )

        try:
            company_name = ""
            if state.fundamental_data and state.fundamental_data.overview:
                company_name = (
                    state.fundamental_data.overview.name
                    if hasattr(state.fundamental_data.overview, "name")
                    else ""
                )

            formatted_prompt = prompt.format(
                company_name=company_name,
                ticker=state.ticker_symbol,
                reports_summary=state.reports,
                news_summary=state.news,
            )

            self.cli.show_progress_start("Generating AI analysis...")
            response = self.llm.invoke(formatted_prompt)
            self.cli.show_progress_success("Analysis completed")

            # Display the analysis result
            self.cli.display_info("Analysis Report Generated")

            return {
                "report": response.content
                if hasattr(response, "content")
                else str(response)
            }

        except Exception as e:
            self.cli.show_progress_error(f"Error during analysis: {str(e)}")
            return {}
