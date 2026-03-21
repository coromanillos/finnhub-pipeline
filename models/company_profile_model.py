from pydantic import BaseModel, field_validator
from typing import Union

class CompanyProfileModel(BaseModel):
    country:              str
    currency:             str
    estimateCurrency:     str
    exchange:             str
    finnhubIndustry:      str
    ipo:                  str           # "1980-12-12" — cast to date in dbt
    logo:                 str
    marketCapitalization: float
    name:                 str
    phone:                str           # numeric string — keep as str
    shareOutstanding:     Union[int, float]  # scan showed both types
    ticker:               str
    weburl:               str

    @field_validator("marketCapitalization")
    @classmethod
    def market_cap_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError(f"marketCapitalization must be positive, got {v}")
        return v

    @field_validator("shareOutstanding")
    @classmethod
    def shares_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError(f"shareOutstanding must be positive, got {v}")
        return v