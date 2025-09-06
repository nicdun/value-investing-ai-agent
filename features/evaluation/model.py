from pydantic import BaseModel
from typing import Any


class ValueEvaluation(BaseModel):
    growth_rates_analysis: dict[str, Any]
    moat_analysis: dict[str, Any]
    management_analysis: dict[str, Any]
    valuation_analysis: dict[str, Any]


class EvaluationSignal(BaseModel):
    report: str


class TranscriptSummary(BaseModel):
    summary: str
