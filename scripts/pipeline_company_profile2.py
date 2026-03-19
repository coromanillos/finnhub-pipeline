
from base_pipeline import BasePipeline
from config import RATE_LIMIT

class CompanyProfile2Pipeline(BasePipeline):

    def endpoint_name(self) -> str:
        return "company_profile2"

    def rate_limit(self) -> int:
        return RATE_LIMIT["company_profile2"]

    def fetch(self, ticker: str) -> dict:
        return self.finnhub_client.company_profile2(symbol=ticker)

    def validate(self, ticker: str, data: dict) -> list:
        issues = []

        if not data:
            issues.append((ticker, "empty response — ticker may be delisted"))
            return issues

        none_fields = [k for k, v in data.items() if v is None or v == ""]
        if none_fields:
            issues.append((ticker, f"missing fields: {none_fields}"))

        return issues


if __name__ == "__main__":
    pipeline = CompanyProfile2Pipeline()
    pipeline.run()