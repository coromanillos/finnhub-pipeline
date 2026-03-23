# models/basic_financials_model.py
from pydantic import BaseModel, field_validator
from typing import Union, Optional

class SeriesEntry(BaseModel):
    period: str
    v:      Union[int, float, None]

class MetricBlock(BaseModel):
    tenDayAverageTradingVolume:    Optional[float] = None
    thirteenWeekPriceReturnDaily:  Optional[float] = None
    twentySixWeekPriceReturnDaily: Optional[float] = None
    fiftyTwoWeekHigh:              Optional[Union[int, float]] = None
    fiftyTwoWeekHighDate:          Optional[str]   = None
    fiftyTwoWeekLow:               Optional[Union[int, float]] = None
    fiftyTwoWeekLowDate:           Optional[str]   = None
    fiftyTwoWeekPriceReturnDaily:  Optional[float] = None
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
    roaAnnual:                     Optional[float] = None
    roeTTM:                        Optional[float] = None

    model_config = {"extra": "allow"}

class SeriesBlock(BaseModel):
    annual:    dict[str, list[SeriesEntry]]
    quarterly: dict[str, list[SeriesEntry]]

class BasicFinancialsModel(BaseModel):
    metric:     MetricBlock
    metricType: Optional[str] = None
    series:     SeriesBlock
    symbol:     str

    @field_validator("symbol")          # ← inside class body
    @classmethod
    def symbol_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("symbol must not be empty")
        return v