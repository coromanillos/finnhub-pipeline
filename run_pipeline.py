# run_pipeline.py
from pipelines.company_profile_pipeline import CompanyProfilePipeline
from pipelines.basic_financials_pipeline import BasicFinancialsPipeline
from pipelines.earnings_pipeline import EarningsPipeline
from pipelines.lobbying_pipeline import LobbyingPipeline
from pipelines.usa_spending_pipeline import USASpendingPipeline

pipelines = [
    CompanyProfilePipeline(),
    BasicFinancialsPipeline(),
    EarningsPipeline(),
    LobbyingPipeline(),
    USASpendingPipeline()
]

for pipeline in pipelines:
    pipeline.run()