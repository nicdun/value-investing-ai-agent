from pydantic import BaseModel
from typing import Any


class ValueEvaluation(BaseModel):
    business_model: dict[str, Any]
    moat: dict[str, Any]
    management: dict[str, Any]
    margin_of_safety: dict[str, Any]


class EvaluationSignal(BaseModel):
    report: str
