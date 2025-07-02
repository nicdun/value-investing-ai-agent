from pydantic import BaseModel, Field


class FundamentalData(BaseModel):
    symbol: str
    overview: dict = Field(default_factory=dict)
    balance_sheet: list[dict] = Field(default_factory=list)
    cash_flow: list[dict] = Field(default_factory=list)
    income_statement: list[dict] = Field(default_factory=list)
    last_updated: str
