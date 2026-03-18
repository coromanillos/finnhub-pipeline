import finnhub
import boto3
import json
import time
import os
import logging
import tempfile
from datetime import date
from abc import ABC, abstractmethod
from dotenv import load_dotenv

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s — %(levelname)s — %(message)s"
)
logger = logging.getLogger(__name__)

load_dotenv()

from config import (
    API_KEY,
    TICKERS,
    S3_BUCKET,
    BRONZE_PREFIX,
    AWS_REGION,
    AWS_ACCESS_KEY_ID,
    AWS_SECRET_ACCESS_KEY
)

class BasePipeline(ABC):
    """
    Abstract base class for all Finnhub endpoint ingestion pipelines.

    Each subclass must define:
        ENDPOINT_NAME: str        e.g. "company_profile2"
        RATE_LIMIT_SECONDS: int   e.g. 1

    Each subclass must implement:
        fetch(ticker)             → raw API response
        validate_record(ticker, data) → list of issue strings

    Shared pipeline flow: extract() → validate() → load() → summary()
    """

    ENDPOINT_NAME: str = NotImplemented
    RATE_LIMIT_SECONDS: int = NotImplemented

    def __init__(self):
        self.finnhub_client = finnhub.Client(api_key=API_KEY)
        self.s3_client = boto3.client(
            "s3",
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            region_name=AWS_REGION
        )
        self.today = str(date.today())
        self.results = {}
        self.issues = []

    # ─────────────────────────────────────────
    # ABSTRACT METHODS — subclasses must implement
    # ─────────────────────────────────────────

    @abstractmethod
    def fetch(self, ticker: str) -> dict | list:
        """Makes the Finnhub API call for one ticker"""
        pass

    @abstractmethod
    def validate_record(self, ticker: str, data: dict | list) -> list:
        """Validates one ticker's response — implemented by each subclass"""
        pass

    def validate(self) -> None:
        """Iterates all results and calls validate_record per ticker"""
        for ticker, data in self.results.items():
            ticker_issues = self.validate_record(ticker, data)
            self.issues.extend(ticker_issues)

    # ─────────────────────────────────────────
    # SHARED METHODS — inherited by all subclasses
    # ─────────────────────────────────────────

    def extract(self) -> None:
        """Pulls data for all 60 tickers from Finnhub"""
        logger.info(f"Starting {self.ENDPOINT_NAME} ingest for {len(TICKERS)} tickers...")

        for i, ticker in enumerate(TICKERS):
            try:
                data = self.fetch_with_retry(ticker)
                self.results[ticker] = data

            except Exception as e:
                logger.error(f"API error for {ticker}: {str(e)}")
                self.issues.append((ticker, f"API error: {str(e)}"))
                self.results[ticker] = {}

            if i < len(TICKERS) - 1:
                time.sleep(self.RATE_LIMIT_SECONDS)

        logger.info(f"Extract complete — {len([r for r in self.results.values() if r])}/{len(TICKERS)} successful")

    def fetch_with_retry(self, ticker: str, retries: int = 3) -> dict | list:
        """Fetches data for one ticker with exponential backoff retry"""
        for attempt in range(retries):
            try:
                return self.fetch(ticker)
            except Exception as e:
                if attempt < retries - 1:
                    wait = 2 ** attempt  # 1s, 2s, 4s
                    logger.warning(f"{ticker}: attempt {attempt + 1} failed — retrying in {wait}s. Error: {str(e)}")
                    time.sleep(wait)
                else:
                    raise

    def load(self) -> str:
        """Saves NDJSON locally then uploads to S3"""
        filename = f"{self.ENDPOINT_NAME}_raw_{self.today}.ndjson"
        filepath = os.path.join(tempfile.gettempdir(), filename) 

        # Save locally
        with open(filepath, "w") as f:
            for ticker, record in self.results.items():
                f.write(json.dumps({
                    "ticker": ticker,
                    "pulled_at": self.today,
                    "data": record
                }) + "\n")

        logger.info(f"Saved locally: {filepath}")

        # Upload to S3
        s3_key = f"{BRONZE_PREFIX}/{self.ENDPOINT_NAME}/{filename}"
        self.s3_client.upload_file(
            Filename=filepath,
            Bucket=S3_BUCKET,
            Key=s3_key
        )
        logger.info(f"Uploaded to s3://{S3_BUCKET}/{s3_key}")
    
        # Clean up temp file
        os.remove(filepath)
        logger.info(f"Cleaned up local temp file: {filepath}")
        
        return s3_key

    def summary(self, s3_key: str) -> None:
        """Logs run summary"""
        logger.info(f"\n{'='*50}")
        logger.info(f"SUMMARY — {self.ENDPOINT_NAME} — {self.today}")
        logger.info(f"{'='*50}")
        logger.info(f"✅ Successfully pulled: {len([r for r in self.results.values() if r])} / {len(TICKERS)}")
        logger.warning(f"⚠️  Issues found:       {len(self.issues)}")
        for ticker, issue in self.issues:
            logger.warning(f"   {ticker}: {issue}")
        logger.info(f"📦 S3 location: s3://{S3_BUCKET}/{s3_key}")

    def run(self) -> None:
        """Runs the full pipeline: extract → validate → load → summary"""
        self.extract()
        self.validate()
        s3_key = self.load()
        self.summary(s3_key)