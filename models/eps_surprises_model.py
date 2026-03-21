import finnhub
import os
import time
from collections import defaultdict
from dotenv import load_dotenv
load_dotenv()

finnhub_client = finnhub.Client(api_key=os.getenv("FINNHUB_API_KEY"))

tickers = [
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

duplicates = [t for t in tickers if tickers.count(t) > 1]
assert not duplicates, f"Duplicate tickers found: {duplicates}"

results = {}
errors  = []

# ── field-level tracking across all quarters of all tickers ───────────────
field_present = defaultdict(int)  # field → count of non-null occurrences
field_null    = defaultdict(int)  # field → count of null/empty occurrences
field_types   = defaultdict(set)  # field → set of Python types seen
total_quarters = 0                # total quarters seen across all tickers

# ── quarter count tracking ─────────────────────────────────────────────────
quarter_counts = []  # one entry per ticker — how many quarters returned

total = len(tickers)

for i, ticker in enumerate(tickers):
    try:
        data = finnhub_client.company_earnings(symbol=ticker)

        if not data:
            errors.append((ticker, "empty response"))
            results[ticker] = []
        else:
            results[ticker] = data
            quarter_counts.append(len(data))
            total_quarters += len(data)

            for quarter in data:
                for field, value in quarter.items():
                    if value is None or value == "":
                        field_null[field] += 1
                    else:
                        field_present[field] += 1
                        field_types[field].add(type(value).__name__)

    except Exception as e:
        errors.append((ticker, f"API error: {str(e)}"))
        results[ticker] = []

    if i < len(tickers) - 1:
        time.sleep(1)

# ─────────────────────────────────────────
# SUMMARY
# ─────────────────────────────────────────
successful    = len([r for r in results.values() if r])
empty_tickers = [t for t, r in results.items() if not r]

print(f"✅ Successfully pulled: {successful} / {total}")
print(f"❌ Errors:              {len(errors)}")
print(f"📭 Empty responses:     {empty_tickers if empty_tickers else 'None'}\n")

if errors:
    print("─── Errors ───")
    for ticker, msg in errors:
        print(f"   {ticker}: {msg}")
    print()

# ─────────────────────────────────────────
# SECTION 1 — QUARTER COUNT DISTRIBUTION
# ─────────────────────────────────────────
if quarter_counts:
    print("─── Quarter Count Distribution ───")
    print(f"  Total quarters across all tickers: {total_quarters}")
    print(f"  Min quarters returned:             {min(quarter_counts)}")
    print(f"  Max quarters returned:             {max(quarter_counts)}")
    print(f"  Avg quarters returned:             {sum(quarter_counts) / len(quarter_counts):.1f}")
    under_4 = [(t, len(r)) for t, r in results.items() if r and len(r) < 4]
    if under_4:
        print("  ⚠️  Tickers with fewer than 4 quarters: {under_4}")
    else:
        print("  ✅ All tickers returned 4+ quarters")
    print()

# ─────────────────────────────────────────
# SECTION 2 — FIELD DECISION TABLE
# Evaluated across all quarters, all tickers
# ─────────────────────────────────────────
print("─── Field Decision Table (per quarter record) ───")
print(f"{'Field':<20} {'Present':>12} {'Null':>8} {'Types':<20} Recommendation")
print("─" * 85)

all_fields = set(field_present.keys()) | set(field_null.keys())

for field in sorted(all_fields):
    present    = field_present.get(field, 0)
    null_count = field_null.get(field, 0)
    types      = ", ".join(field_types.get(field, {"unknown"}))
    ever_null  = null_count > 0

    if ever_null:
        rec = "Optional  ← null in some quarters"
    else:
        rec = "Required  ← never null across all quarters"

    print(f"{field:<20} {present:>9} seen  {null_count:>5} null   {types:<20} {rec}")