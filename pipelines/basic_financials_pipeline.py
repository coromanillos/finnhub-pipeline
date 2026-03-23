# pipelines/basic_financials_pipeline.py
from base_pipeline import BasePipeline
from models.basic_financials_model import BasicFinancialsModel

class BasicFinancialsPipeline(BasePipeline):
    ENDPOINT_NAME      = "basic_financials"
    RATE_LIMIT_SECONDS = 1
    pydantic_model     = BasicFinancialsModel

    def fetch(self, ticker: str) -> dict:      # ← inside class body
        return self.finnhub_client.company_basic_financials(
            symbol=ticker,
            metric="all"
        )

if __name__ == "__main__":
    BasicFinancialsPipeline().run()