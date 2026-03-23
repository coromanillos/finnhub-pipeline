# config.py
# Central configuration for finnhub-pipeline
# All shared constants and settings live here
# All validation logic lives in tests/test_config.py

# ─────────────────────────────────────────────
# API AUTHENTICATION
# ─────────────────────────────────────────────

import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("FINNHUB_API_KEY")

assert API_KEY, "FINNHUB_API_KEY not found — check your .env file"

# ─────────────────────────────────────────────
# TICKERS
# ─────────────────────────────────────────────

TICKERS = [
    # DEFENSE - High Lobby
    "LMT", "RTX", "NOC", "GD", "BA", "LHX", "LDOS", "HII", "BAESY", "SAIC",
    # DEFENSE - Low Lobby
    "TXT", "TDG", "HEI", "DRS", "KTOS", "AVAV", "MRCY", "CW", "MOG.A", "DCO",
    # ENERGY - High Lobby
    "XOM", "CVX", "COP", "OXY", "BP", "NEE", "D", "DUK", "HAL", "BKR",
    # ENERGY - Low Lobby
    "SLB", "VLO", "PSX", "EOG", "FANG", "DVN", "CTRA", "AR", "CHRD", "MTDR",
    # TECH - High Lobby
    "MSFT", "AMZN", "GOOGL", "IBM", "ORCL", "PLTR", "BAH", "CACI", "PSN", "CRM",
    # TECH - Low Lobby
    "AAPL", "META", "NVDA", "CSCO", "PANW", "CRWD", "SNOW", "DDOG", "NET", "TWLO"
]

# ─────────────────────────────────────────────
# SECTOR MAPPING
# ─────────────────────────────────────────────

SECTOR = {
    # Defense
    "LMT": "defense", "RTX": "defense", "NOC": "defense", "GD": "defense",
    "BA": "defense", "LHX": "defense", "LDOS": "defense", "HII": "defense",
    "BAESY": "defense", "SAIC": "defense", "TXT": "defense", "TDG": "defense",
    "HEI": "defense", "DRS": "defense", "KTOS": "defense", "AVAV": "defense",
    "MRCY": "defense", "CW": "defense", "MOG.A": "defense", "DCO": "defense",
    # Energy
    "XOM": "energy", "CVX": "energy", "COP": "energy", "OXY": "energy",
    "BP": "energy", "NEE": "energy", "D": "energy", "DUK": "energy",
    "HAL": "energy", "BKR": "energy", "SLB": "energy", "VLO": "energy",
    "PSX": "energy", "EOG": "energy", "FANG": "energy", "DVN": "energy",
    "CTRA": "energy", "AR": "energy", "CHRD": "energy", "MTDR": "energy",
    # Tech
    "MSFT": "tech", "AMZN": "tech", "GOOGL": "tech", "IBM": "tech",
    "ORCL": "tech", "PLTR": "tech", "BAH": "tech", "CACI": "tech",
    "PSN": "tech", "CRM": "tech", "AAPL": "tech", "META": "tech",
    "NVDA": "tech", "CSCO": "tech", "PANW": "tech", "CRWD": "tech",
    "SNOW": "tech", "DDOG": "tech", "NET": "tech", "TWLO": "tech"
}

# ─────────────────────────────────────────────
# LOBBY GROUP MAPPING
# ─────────────────────────────────────────────

LOBBY_GROUP = {
    # Defense - High Lobby
    "LMT": "high", "RTX": "high", "NOC": "high", "GD": "high",
    "BA": "high", "LHX": "high", "LDOS": "high", "HII": "high",
    "BAESY": "high", "SAIC": "high",
    # Defense - Low Lobby
    "TXT": "low", "TDG": "low", "HEI": "low", "DRS": "low",
    "KTOS": "low", "AVAV": "low", "MRCY": "low", "CW": "low",
    "MOG.A": "low", "DCO": "low",
    # Energy - High Lobby
    "XOM": "high", "CVX": "high", "COP": "high", "OXY": "high",
    "BP": "high", "NEE": "high", "D": "high", "DUK": "high",
    "HAL": "high", "BKR": "high",
    # Energy - Low Lobby
    "SLB": "low", "VLO": "low", "PSX": "low", "EOG": "low",
    "FANG": "low", "DVN": "low", "CTRA": "low", "AR": "low",
    "CHRD": "low", "MTDR": "low",
    # Tech - High Lobby
    "MSFT": "high", "AMZN": "high", "GOOGL": "high", "IBM": "high",
    "ORCL": "high", "PLTR": "high", "BAH": "high", "CACI": "high",
    "PSN": "high", "CRM": "high",
    # Tech - Low Lobby
    "AAPL": "low", "META": "low", "NVDA": "low", "CSCO": "low",
    "PANW": "low", "CRWD": "low", "SNOW": "low", "DDOG": "low",
    "NET": "low", "TWLO": "low"
}

# ─────────────────────────────────────────────
# DATE RANGES
# ─────────────────────────────────────────────

FROM_DATE = "2023-01-01"
TO_DATE = "2025-12-31"

# ─────────────────────────────────────────────
# S3 CONFIGURATION
# ─────────────────────────────────────────────

S3_BUCKET = "finnhub-pipeline-288831154476-us-east-1-an"
BRONZE_PREFIX = "bronze"