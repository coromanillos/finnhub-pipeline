# pipelines/earnings_pipeline.py
from base_pipeline import BasePipeline
from models.earnings_model import EPSSurprisesModel

class EPSSurprisesPipeline(BasePipeline):
    ENDPOINT_NAME      = "earnings"
    RATE_LIMIT_SECONDS = 1
    pydantic_model     = EPSSurprisesModel

    def fetch(self, ticker: str) -> dict:
        # API returns a bare list — wrap into dict so base class
        # and Pydantic model always receive a consistent shape
        response = self.finnhub_client.company_earnings(symbol=ticker)
        return {
            "symbol": ticker,
            "data": response if response else []
        }

if __name__ == "__main__":
    EPSSurprisesPipeline().run()