# run_pipeline.py
import logging
import time
from pipelines.company_profile_pipeline import CompanyProfilePipeline
from pipelines.basic_financials_pipeline import BasicFinancialsPipeline
from pipelines.earnings_pipeline import EarningsPipeline
from pipelines.lobbying_pipeline import LobbyingPipeline
from pipelines.usa_spending_pipeline import USASpendingPipeline

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s — %(levelname)s — %(message)s"
)
logger = logging.getLogger(__name__)

PIPELINES = [
    CompanyProfilePipeline(),
    BasicFinancialsPipeline(),
    EarningsPipeline(),
    LobbyingPipeline(),
    USASpendingPipeline(),
]

if __name__ == "__main__":
    start = time.time()
    logger.info(f"Starting full pipeline run — {len(PIPELINES)} endpoints")
    logger.info("=" * 50)

    failed = []

    for pipeline in PIPELINES:
        try:
            logger.info(f"Running {pipeline.ENDPOINT_NAME}...")
            pipeline.run()
        except Exception as e:
            logger.error(f"{pipeline.ENDPOINT_NAME} failed — {str(e)}")
            failed.append(pipeline.ENDPOINT_NAME)

    duration = round(time.time() - start, 2)

    logger.info("=" * 50)
    logger.info(f"Full pipeline run complete — {duration}s")
    logger.info(f"✅ Succeeded: {len(PIPELINES) - len(failed)} / {len(PIPELINES)}")

    if failed:
        logger.error(f"❌ Failed:    {len(failed)} / {len(PIPELINES)}")
        for name in failed:
            logger.error(f"   {name}")
    else:
        logger.info(f"✅ All pipelines completed successfully")