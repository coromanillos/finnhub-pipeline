# models/usa_spending_model.py
from pydantic import BaseModel, field_validator
from typing import Optional, Union

# ─────────────────────────────────────────
# Individual spending activity record
# Evaluated across 40,465 records, 45 tickers
# ─────────────────────────────────────────
class SpendingActivity(BaseModel):
    actionDate:                       str
    awardDescription:                 Optional[str]       = None  # null in 28/40465
    awardingAgencyName:               str
    awardingOfficeName:               str                         # required — overrides prior assumption
    awardingSubAgencyName:            str
    country:                          str
    lastModifiedDate:                 str
    naicsCode:                        Optional[str]       = None  # null in 5/40465
    obligatedAmount:                  Union[int, float]
    outlayedAmount:                   Union[int, float]
    performanceCity:                  Optional[str]       = None  # null in 3986/40465
    performanceCongressionalDistrict: Optional[str]       = None  # null in 1328/40465
    performanceCountry:               Optional[str]       = None  # null in 2697/40465
    performanceCounty:                Optional[str]       = None  # null in 3986/40465
    performanceEndDate:               Optional[str]       = None  # null in 2697/40465
    performanceStartDate:             str
    performanceState:                 Optional[str]       = None  # null in 3978/40465
    performanceZipCode:               Optional[str]       = None  # null in 3849/40465
    permalink:                        str
    potentialAmount:                  Union[int, float]
    recipientName:                    str
    recipientParentName:              Optional[str]       = None  # null in 4/40465
    symbol:                           str
    totalValue:                       Union[int, float]

    @field_validator("totalValue", "potentialAmount", "obligatedAmount")  # ← inside SpendingActivity
    @classmethod
    def amount_must_be_non_negative(cls, v):
        if v < 0:
            raise ValueError(f"amount field must be non-negative, got {v}")
        return v

    @field_validator("actionDate", "performanceStartDate", "lastModifiedDate")  # ← inside SpendingActivity
    @classmethod
    def date_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("date field must not be empty")
        return v

    @field_validator("permalink")     # ← inside SpendingActivity
    @classmethod
    def permalink_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("permalink must not be empty")
        return v

# ─────────────────────────────────────────
# Top-level wrapper
# symbol always present — data can be empty
# list for 15 tickers with no spending activity
# ─────────────────────────────────────────
class USASpendingModel(BaseModel):
    symbol: str
    data:   list[SpendingActivity] = []

    @field_validator("symbol")        # ← inside USASpendingModel
    @classmethod
    def symbol_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("symbol must not be empty")
        return v