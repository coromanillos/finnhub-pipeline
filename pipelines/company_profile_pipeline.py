# pipelines/company_profile_pipeline.py
from base_pipeline import BasePipeline
from models.company_profile_model import CompanyProfileModel

class CompanyProfilePipeline(BasePipeline):
    ENDPOINT_NAME      = "company_profile2"  # ← was "company_profile" — must match S3 path
    RATE_LIMIT_SECONDS = 1
    pydantic_model     = CompanyProfileModel

    def fetch(self, ticker: str) -> dict:    # ← inside class body
        return self.finnhub_client.company_profile2(symbol=ticker)

if __name__ == "__main__":
    CompanyProfilePipeline().run()