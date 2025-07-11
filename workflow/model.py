from langgraph.graph.message import BaseMessage
from pydantic import BaseModel
from features.fundamental_data.model import FundamentalData
from langgraph.graph.message import add_messages
from typing import Annotated, Optional, List
from datetime import datetime
from features.research.model import PDFDocument
from features.evaluation.model import ValueEvaluation


class Metrics(BaseModel):
    fcf_growth: float = 0.0


class ResearchState(BaseModel):
    messages: Annotated[list, add_messages] = []
    ticker_symbol: str = ""
    fundamental_data: FundamentalData = None
    evaluation: ValueEvaluation = None
    reports: list[PDFDocument] = []
    news: list[dict] = []
    investment_decision: str = ""
    report: str = ""
