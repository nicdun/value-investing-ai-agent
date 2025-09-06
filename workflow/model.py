from langgraph.graph.message import BaseMessage
from pydantic import BaseModel
from features.data.model import FundamentalData
from langgraph.graph.message import add_messages
from typing import Annotated, Optional, List
from datetime import datetime
from features.data.model import TranscriptEntry
from features.research.model import PDFDocument
from features.evaluation.model import ValueEvaluation, EvaluationSignal


class Metrics(BaseModel):
    fcf_growth: float = 0.0


class ResearchState(BaseModel):
    messages: Annotated[list, add_messages] = []
    ticker_symbol: str = ""
    analysis_years: int = 10  # Default to 10 years
    fundamental_data: FundamentalData = None
    value_evaluation: ValueEvaluation = None
    transcript: list[TranscriptEntry] = []
    reports: list[PDFDocument] = []
    news: list[dict] = []
    report: EvaluationSignal = None
