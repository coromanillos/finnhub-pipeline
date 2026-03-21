# models/basic_financials_model.py

from pydantic import BaseModel, field_validator
from typing import Union, Optional

# ─────────────────────────────────────────
# Series entry — shape of each time-series data point
# Used by both annual and quarterly series
# ─────────────────────────────────────────
class SeriesEntry(BaseModel):
    period: str
    v:      Union[int, float, None]  # scan showed int and float — None seen in practice

# ─────────────────────────────────────────
# Metric block — flat scalar financials
# All 60/60 present and never null from scan
# Only a representative set of fields validated —
# full metric block has 100+ fields, most unused downstream
# ─────────────────────────────────────────
class MetricBlock(BaseModel):
    tenDayAverageTradingVolume:    float = None  # 10DayAverageTradingVolume
    thirteenWeekPriceReturnDaily:  float = None  # 13WeekPriceReturnDaily
    twentySixWeekPriceReturnDaily: float = None  # 26WeekPriceReturnDaily
    fiftyTwoWeekHigh:              Union[int, float] = None  # 52WeekHigh
    fiftyTwoWeekHighDate:          str   = None  # 52WeekHighDate
    fiftyTwoWeekLow:               Union[int, float] = None  # 52WeekLow
    fiftyTwoWeekLowDate:           str   = None  # 52WeekLowDate
    fiftyTwoWeekPriceReturnDaily:  float = None  # 52WeekPriceReturnDaily
    assetTurnoverAnnual:           Optional[float] = None
    assetTurnoverTTM:              Optional[float] = None
    beta:                          Optional[float] = None
    epsAnnual:                     Optional[float] = None
    epsTTM:                        Optional[float] = None
    grossMarginAnnual:             Optional[float] = None
    grossMarginTTM:                Optional[float] = None
    marketCapitalization:          Optional[float] = None
    netProfitMarginAnnual:         Optional[float] = None
    netProfitMarginTTM:            Optional[float] = None
    peAnnual:                      Optional[float] = None
    peTTM:                         Optional[float] = None
    revenueGrowth3Y:               Optional[float] = None
    revenueGrowth5Y:               Optional[float] = None
    roaAnnual:                     Optional[float] = None  # roaRfy in response
    roeTTM:                        Optional[float] = None

    model_config = {"extra": "allow"}  # allows the 100+ other metric fields through

# ─────────────────────────────────────────
# Series block — time-series arrays
# annual and quarterly both 60/60 present
# ─────────────────────────────────────────
class SeriesBlock(BaseModel):
    annual:    dict[str, list[SeriesEntry]]
    quarterly: dict[str, list[SeriesEntry]]

# ─────────────────────────────────────────
# Top-level model
# ─────────────────────────────────────────
class BasicFinancialsModel(BaseModel):
    metric:     MetricBlock
    metricType: Optional[str] = None  # "all" — present but not analytically useful
    series:     SeriesBlock
    symbol:     str

    @field_validator("symbol")
    @classmethod
    def symbol_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("symbol must not be empty")
        return v