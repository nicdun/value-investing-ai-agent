from langchain_google_genai import ChatGoogleGenerativeAI
from config.env import GOOGLE_API_KEY
from langchain.prompts import PromptTemplate
from langchain_core.messages import HumanMessage, SystemMessage
from langchain.chat_models import init_chat_model
from langgraph.graph import StateGraph, END, START
from features.analysis.model import ResearchState
from features.fundamental_data.alphavantage_adapter import AlphaVantageAPI
from features.fundamental_data.model import FundamentalData

class Workflow:
    def __init__(self):
        self.llm = init_chat_model("google_genai:gemini-2.0-flash")
        self.llm_chat = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=GOOGLE_API_KEY
        )
        self.workflow = self._build_workflow()
    

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
        # graph_builder.add_node("web_research", self.web_research)
        # graph_builder.add_node("generate_report", self.generate_report)
        # graph_builder.add_node("investment_decision", self.investment_decision)
        graph_builder.add_edge("retrieve_user_input", "retrieve_ticker_data")
        graph_builder.add_edge("retrieve_ticker_data", "analyze_ticker_data")
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
        overview = AlphaVantageAPI.get_ticker_overview(state.ticker_symbol)
        # balance_sheet = AlphaVantageAPI.get_balance_sheet(ticker_symbol)
        # income_statement = AlphaVantageAPI.get_income_statement(ticker_symbol)
        # cash_flow = AlphaVantageAPI.get_cash_flow(ticker_symbol)
        print(f"Overview: {overview}")

        return ResearchState(fundamental_data=FundamentalData(overview=overview))