from langchain_google_genai import ChatGoogleGenerativeAI
from config.env import GOOGLE_API_KEY
from langchain.prompts import PromptTemplate
from langchain_core.messages import HumanMessage, SystemMessage
from langchain.chat_models import init_chat_model
from langgraph.graph import StateGraph, END, START
from features.analysis.model import ResearchState
from features.fundamental_data.alphavantage_adapter import AlphaVantageAPI
from features.fundamental_data.model import FundamentalData
from features.research.firecrawl_adapter import FirecrawlAdapter
from datetime import datetime
from features.analysis.prompts import Prompts
class Workflow:
    def __init__(self):
        self.llm = init_chat_model("google_genai:gemini-2.0-flash")
        self.llm_chat = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=GOOGLE_API_KEY
        )
        self.workflow = self._build_workflow()
        self.prompts = Prompts()
    

    def _build_workflow(self):
        # 1. Extract the ticker symbol from the user input
        # 2. Analyze the fundamental data for the ticker symbol
        # 3. do a web research on the stock name (from the overview fundamental data) for last quarterly reports & news & market
        # 4. Generate a report on the ticker symbol
        # 5. provide an investment decision recommondation
        # 5. Return the report to the user
        graph_builder = StateGraph(ResearchState)
        
        graph_builder.add_edge(START, "retrieve_user_input")
        graph_builder.add_node("retrieve_user_input", self._retrieve_user_input)
        graph_builder.add_node("retrieve_ticker_data", self._retrieve_ticker_symbol)
        graph_builder.add_node("analyze_ticker_data", self._analyze_ticker_data)
        graph_builder.add_node("web_research", self._web_research)
        graph_builder.add_node("web_research", self._analyze_web_research)
        # graph_builder.add_node("generate_report", self.generate_report)
        # graph_builder.add_node("investment_decision", self.investment_decision)
        graph_builder.add_edge("retrieve_user_input", "retrieve_ticker_data")
        graph_builder.add_edge("retrieve_ticker_data", "analyze_ticker_data")
        graph_builder.add_edge("analyze_ticker_data", "web_research")
        graph_builder.add_edge("retrieve_ticker_data", END)

        return graph_builder.compile()


    def run(self) -> ResearchState:
        initial_state = ResearchState()
        final_state = self.workflow.invoke(initial_state)
        return ResearchState(**final_state)
    
    def _retrieve_user_input(self, state: ResearchState) -> ResearchState:
        user_input = input("Enter a stock name: ")
        return ResearchState(messages=[HumanMessage(content=user_input)])

    def _retrieve_ticker_symbol(self, state: ResearchState) -> str:
        print(f"Retrieving stock ticker for stock name {state.messages[-1].content}")
        # remove line after testing the whole process
        return ResearchState(ticker_symbol='AAPL')
        search_results = AlphaVantageAPI.get_ticker_symbol(state.messages[-1].content)

        # Extract the list of stocks from search_results and format each line as: symbol, name, region
        stock_lines = []
        for match in search_results:
            symbol = match.get('1. symbol', '')
            name = match.get('2. name', '')
            region = match.get('4. region', '')
            stock_lines.append(f"{symbol}, {name}, {region}")
        formatted_stock_list = "\n".join(stock_lines)
        print("Matching stocks:\n" + formatted_stock_list)

        user_input = input("Select a stock ticker you want to analyze: ")

        return ResearchState(ticker_symbol=user_input)
    
    def _analyze_ticker_data(self, state: ResearchState) -> str:
        print(f"Analyzing stock ticker {state.ticker_symbol}")
        fundamental_data = AlphaVantageAPI.get_ticker_overview(state.ticker_symbol)
        # balance_sheet = AlphaVantageAPI.get_balance_sheet(ticker_symbol)
        # income_statement = AlphaVantageAPI.get_income_statement(ticker_symbol)
        # cash_flow = AlphaVantageAPI.get_cash_flow(ticker_symbol)
        print(f"Overview: {fundamental_data}")

        return ResearchState(fundamental_data=FundamentalData(symbol=state.ticker_symbol, last_updated=datetime.now().isoformat(), overview=fundamental_data.overview))
    
    def _web_research(self, state: ResearchState) -> str:
        print("🔍 Starting web research...")
        
        # Get company information from fundamental data
        if not state.fundamental_data or not state.fundamental_data.overview:
            print("❌ No fundamental data available for web research")
            return state
        
        company_name = state.fundamental_data.overview.get('Name', '')
        ticker_symbol = state.ticker_symbol
        
        if not company_name:
            print("❌ No company name found in fundamental data")
            return state
        
        print(f"🏢 Researching: {company_name} ({ticker_symbol})")
        
        try:
            # Step 1: Find investor relations pages
            print("📋 Finding investor relations pages...")
            ir_pages = self.firecrawl.find_investor_relations_pages(company_name, ticker_symbol)
            print(f"Found {len(ir_pages)} investor relations pages")
            
            # Step 2: Crawl for quarterly reports
            print("📊 Crawling for quarterly reports...")
            quarterly_reports = self.firecrawl.crawl_quarterly_reports(ir_pages)
            print(f"Found {len(quarterly_reports)} quarterly reports")
            
            # Step 3: Search for recent news
            print("📰 Searching for recent news...")
            recent_news = self.firecrawl.search_recent_news(company_name, ticker_symbol)
            print(f"Found {len(recent_news)} recent news items")
            
            # Update state with research findings
            updated_state = ResearchState(
                messages=state.messages,
                ticker_symbol=state.ticker_symbol,
                fundamental_data=state.fundamental_data,
                calculated_metrics=state.calculated_metrics,
                quarterly_reports=quarterly_reports,
                news=recent_news,
                investment_decision=state.investment_decision,
            )
            
            print("✅ Web research completed")
            return updated_state
            
        except Exception as e:
            print(f"❌ Error during web research: {e}")
            # Return original state if research fails
            return state
    
    def _analyze_web_research(self, state: ResearchState) -> str:
        print("🔍 Analyzing web research...")

        prompt = PromptTemplate(
            template=self.prompts.analyze_ticker_user,
            input_variables=["company_name", "ticker", "reports_summary", "news_summary"]
        )

        try:
            formatted_prompt = prompt.format(
                company_name=state.fundamental_data.overview.get('Name', ''),
                ticker=state.ticker_symbol,
                reports_summary=state.quarterly_reports,
                news_summary=state.news
            )

            response = self.llm.invoke(formatted_prompt)
            print(f"🔍 Analysis: {response}")
            return ResearchState(report=response)
        except Exception as e:
            print(f"❌ Error during web research: {e}")
            return state