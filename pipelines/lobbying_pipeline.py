# pipelines/lobbying_pipeline.py
from base_pipeline import BasePipeline
from models.lobbying_model import LobbyingModel
from config import FROM_DATE, TO_DATE

class LobbyingPipeline(BasePipeline):
    ENDPOINT_NAME      = "senate_lobbying"   # ← was "lobbying" — must match S3 path
    RATE_LIMIT_SECONDS = 2                   # ← was 1 — lobbying needs 2s per scan findings
    pydantic_model     = LobbyingModel

    def fetch(self, ticker: str) -> dict:    # ← inside class body
        return self.finnhub_client.stock_lobbying(
            symbol=ticker,                   # ← use keyword argument
            _from=FROM_DATE,                 # ← date range missing entirely
            to=TO_DATE
        )

if __name__ == "__main__":
    LobbyingPipeline().run()