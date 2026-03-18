import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from scripts.config import TICKERS, SECTOR, LOBBY_GROUP, RATE_LIMIT, OPTIONAL_FIELDS

# ─────────────────────────────────────────────
# TICKER TESTS
# ─────────────────────────────────────────────

def test_ticker_count():
    assert len(TICKERS) == 60, f"Expected 60 tickers, found {len(TICKERS)}"

def test_no_duplicate_tickers():
    assert len(TICKERS) == len(set(TICKERS)), "Duplicate tickers found"

# ─────────────────────────────────────────────
# SECTOR MAPPING TESTS
# ─────────────────────────────────────────────

def test_all_tickers_have_sector():
    missing = [t for t in TICKERS if t not in SECTOR]
    assert not missing, f"Tickers missing sector mapping: {missing}"

def test_sector_values_are_valid():
    valid_sectors = {"defense", "energy", "tech"}
    invalid = [t for t, s in SECTOR.items() if s not in valid_sectors]
    assert not invalid, f"Invalid sector values: {invalid}"

def test_sector_count_per_group():
    defense = [t for t, s in SECTOR.items() if s == "defense"]
    energy = [t for t, s in SECTOR.items() if s == "energy"]
    tech = [t for t, s in SECTOR.items() if s == "tech"]
    assert len(defense) == 20, f"Expected 20 defense tickers, found {len(defense)}"
    assert len(energy) == 20, f"Expected 20 energy tickers, found {len(energy)}"
    assert len(tech) == 20, f"Expected 20 tech tickers, found {len(tech)}"

# ─────────────────────────────────────────────
# LOBBY GROUP MAPPING TESTS
# ─────────────────────────────────────────────

def test_all_tickers_have_lobby_group():
    missing = [t for t in TICKERS if t not in LOBBY_GROUP]
    assert not missing, f"Tickers missing lobby group mapping: {missing}"

def test_lobby_group_values_are_valid():
    valid_groups = {"high", "low"}
    invalid = [t for t, g in LOBBY_GROUP.items() if g not in valid_groups]
    assert not invalid, f"Invalid lobby group values: {invalid}"

def test_lobby_group_count_per_group():
    high = [t for t, g in LOBBY_GROUP.items() if g == "high"]
    low = [t for t, g in LOBBY_GROUP.items() if g == "low"]
    assert len(high) == 30, f"Expected 30 high lobby tickers, found {len(high)}"
    assert len(low) == 30, f"Expected 30 low lobby tickers, found {len(low)}"

# ─────────────────────────────────────────────
# RATE LIMIT TESTS
# ─────────────────────────────────────────────

def test_rate_limit_keys_exist():
    expected_endpoints = {
        "company_profile2", "basic_financials",
        "eps_surprises", "senate_lobbying", "usa_spending"
    }
    assert set(RATE_LIMIT.keys()) == expected_endpoints

def test_rate_limit_values_are_positive():
    invalid = [k for k, v in RATE_LIMIT.items() if v <= 0]
    assert not invalid, f"Invalid rate limit values: {invalid}"

# ─────────────────────────────────────────────
# OPTIONAL FIELDS TESTS
# ─────────────────────────────────────────────

def test_optional_fields_keys_exist():
    expected = {"senate_lobbying", "usa_spending"}
    assert set(OPTIONAL_FIELDS.keys()) == expected

def test_optional_fields_are_sets():
    for endpoint, fields in OPTIONAL_FIELDS.items():
        assert isinstance(fields, set), f"{endpoint} optional fields should be a set"