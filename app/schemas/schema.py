from pydantic import BaseModel, Field
from typing import List, Optional


class PollRequest(BaseModel):
    symbols: List[str] = Field(..., min_length=1)
    interval: int
    provider: Optional[str] = "yfinance"


class PollResponse(BaseModel):
    job_id: str
    status: str
    config: PollRequest


class PriceResponse(BaseModel):
    symbol: str
    price: float
    timestamp: str
    provider: str = "yfinance"


class MovingAverageResponse(BaseModel):
    symbol: str
    moving_average: float
    timestamp: str


class PriceHistoryItem(BaseModel):
    symbol: str
    price: float
    timestamp: str
    source: str
