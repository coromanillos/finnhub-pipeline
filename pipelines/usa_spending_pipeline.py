# pipelines/usa_spending_pipeline.py
from base_pipeline import BasePipeline
from models.usa_spending_model import USASpendingModel
from config import FROM_DATE, TO_DATE

class USASpendingPipeline(BasePipeline):
    ENDPOINT_NAME      = "usa_spending"
    RATE_LIMIT_SECONDS = 2                  # ← was 1 — spending needs 2s per scan findings
    pydantic_model     = USASpendingModel

    def fetch(self, ticker: str) -> dict:   # ← inside class body
        return self.finnhub_client.stock_usa_spending(
            symbol=ticker,                  # ← use keyword argument
            _from=FROM_DATE,                # ← date range missing entirely
            to=TO_DATE
        )

if __name__ == "__main__":
    USASpendingPipeline().run()