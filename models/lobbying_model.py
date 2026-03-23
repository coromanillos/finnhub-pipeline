# models/lobbying_model.py
from pydantic import BaseModel, field_validator
from typing import Optional

# ─────────────────────────────────────────
# Individual lobbying activity record
# Evaluated across 3012 records, 46 tickers
# ─────────────────────────────────────────
class LobbyingActivity(BaseModel):
    clientId:           str
    country:            Optional[str] = None  # null in 12/3012
    date:               Optional[str] = None  # always null — never use downstream
    description:        Optional[str] = None  # null in 582/3012
    documentUrl:        str
    expenses:           Optional[int] = None  # null in 2589/3012 — mutually exclusive with income
    houseRegistrantId:  Optional[str] = None  # null in 174/3012
    income:             Optional[int] = None  # null in 423/3012 — mutually exclusive with expenses
    name:               str
    period:             str
    postedName:         Optional[str] = None  # always null — never use downstream
    registrantId:       str
    senateId:           str
    symbol:             str
    year:               int

    @field_validator("year")                          # ← inside LobbyingActivity
    @classmethod
    def year_must_be_valid(cls, v):
        if v < 2000 or v > 2100:
            raise ValueError(f"year out of expected range, got {v}")
        return v

    @field_validator("clientId", "registrantId", "senateId")  # ← inside LobbyingActivity
    @classmethod
    def id_fields_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("ID field must not be empty")
        return v

    @field_validator("documentUrl")                   # ← inside LobbyingActivity
    @classmethod
    def document_url_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("documentUrl must not be empty")
        return v

# ─────────────────────────────────────────
# Top-level wrapper
# symbol always present — data can be empty
# list for 14 tickers with no lobbying activity
# ─────────────────────────────────────────
class LobbyingModel(BaseModel):
    symbol: str
    data:   list[LobbyingActivity] = []

    @field_validator("symbol")                        # ← inside LobbyingModel
    @classmethod
    def symbol_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("symbol must not be empty")
        return v