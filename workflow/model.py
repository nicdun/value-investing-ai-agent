from langgraph.graph.message import BaseMessage
from pydantic import BaseModel
from features.fundamental_data.model import FundamentalData
from langgraph.graph.message import add_messages
from typing import Annotated, Optional, List
from datetime import datetime


class Metrics(BaseModel):
    fcf_growth: float = 0.0


class PDFDocument(BaseModel):
    """
    Represents a PDF document found on investor relations pages.
    """

    url: str
    title: str
    document_type: str  # e.g., "10-K Annual Report", "10-Q Quarterly Report"
    period: str  # e.g., "FY 2024", "FY 2024 Q3"
    filing_date: Optional[str] = None
    filename: str

    def __str__(self) -> str:
        return f"{self.document_type} - {self.period}: {self.title}"


class PDFDocumentList(BaseModel):
    """
    Wrapper for a list of PDF documents for structured output.
    """

    documents: List[PDFDocument]

    def __len__(self) -> int:
        return len(self.documents)

    def __iter__(self):
        return iter(self.documents)

    def __getitem__(self, index):
        return self.documents[index]


class ResearchState(BaseModel):
    messages: Annotated[list, add_messages] = []
    ticker_symbol: str = ""
    fundamental_data: FundamentalData = None
    calculated_metrics: Metrics = None
    reports: list[PDFDocument] = []
    news: list[dict] = []
    investment_decision: str = ""
    report: str = ""
