# run_piepline.py

from pipeline_company_profile2 import CompanyProfile2Pipeline
from pipeline_basic_financials import BasicFinancialsPipeline
from pipeline_eps_surprises import EpsSurprisesPipeline
from pipeline_senate_lobbying import SenateLobbyingPipeline
from pipeline_usa_spending import UsaSpendingPipeline

pipelines = [
    CompanyProfile2Pipeline(),
    BasicFinancialsPipeline(),
    EpsSurprisesPipeline(),
    SenateLobbyingPipeline(),
    UsaSpendingPipeline()
]

for pipeline in pipelines:
    pipeline.run()
    print()