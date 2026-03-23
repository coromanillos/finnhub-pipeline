# models/earnings_model.py
from pydantic import BaseModel, field_validator
from typing import Union

# ─────────────────────────────────────────
# Individual EPS surprise record — one per quarter
# Evaluated across 240 records, 60 tickers
# All fields required — zero nulls observed
# ─────────────────────────────────────────
class EPSSurpriseEntry(BaseModel):
    actual:          Union[int, float]
    estimate:        float
    period:          str
    quarter:         int
    surprise:        float
    surprisePercent: float
    symbol:          str
    year:            int

    @field_validator("year")                  # ← inside EPSSurpriseEntry
    @classmethod
    def year_must_be_valid(cls, v):
        if v < 2000 or v > 2100:
            raise ValueError(f"year out of expected range, got {v}")
        return v

    @field_validator("quarter")               # ← inside EPSSurpriseEntry
    @classmethod
    def quarter_must_be_valid(cls, v):
        if v not in (1, 2, 3, 4):
            raise ValueError(f"quarter must be 1–4, got {v}")
        return v

    @field_validator("symbol", "period")      # ← inside EPSSurpriseEntry
    @classmethod
    def string_fields_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("field must not be empty")
        return v

# ─────────────────────────────────────────
# Top-level wrapper
# API returns a bare list — wrapped in fetch()
# for consistency with base pipeline expectations
# ─────────────────────────────────────────
class EPSSurprisesModel(BaseModel):
    symbol: str
    data:   list[EPSSurpriseEntry] = []

    @field_validator("symbol")                # ← inside EPSSurprisesModel
    @classmethod
    def symbol_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("symbol must not be empty")
        return v