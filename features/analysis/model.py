from langgraph.graph.message import BaseMessage
from pydantic import BaseModel
from features.fundamental_data.model import FundamentalData
from langgraph.graph.message import add_messages
from typing import Annotated

class ResearchState(BaseModel):
    messages: Annotated[list, add_messages] = []
    ticker_symbol: str = ""
    fundamental_data: FundamentalData = None
    calculated_metrics: Metrics = None
    quarterly_reports: list[dict] = []
    news: list[dict] = []
    investment_decision: str = ""
    report: str = ""

class Metrics(BaseModel):
    