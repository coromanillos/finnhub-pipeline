import finnhub
import boto3
import json
import time
import os
import logging
import tempfile
from datetime import date
from abc import ABC, abstractmethod
from typing import Type
from dotenv import load_dotenv
from pydantic import BaseModel, ValidationError
from config import (
    API_KEY,
    TICKERS,
    S3_BUCKET,
    BRONZE_PREFIX,
    AWS_REGION,
    AWS_ACCESS_KEY_ID,
    AWS_SECRET_ACCESS_KEY
)

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s — %(levelname)s — %(message)s"
)
logger = logging.getLogger(__name__)

class BasePipeline(ABC):
    """
    Abstract base class for all Finnhub endpoint ingestion pipelines.

    Each subclass must define:
        ENDPOINT_NAME: str              e.g. "company_profile2"
        RATE_LIMIT_SECONDS: int         e.g. 1
        pydantic_model: Type[BaseModel] e.g. CompanyProfileModel

    Each subclass must implement:
        fetch(ticker)    → raw API response dict/list

    Shared pipeline flow: extract() → load() → summary()
    Validation now happens inline inside fetch_with_retry(), immediately
    after each API call. Invalid records are routed to dead_letter,
    never written to S3 as clean data.
    """

    ENDPOINT_NAME: str = NotImplemented
    RATE_LIMIT_SECONDS: int = NotImplemented
    pydantic_model: Type[BaseModel] = NotImplemented

    def __init__(self):
        self.finnhub_client = finnhub.Client(api_key=API_KEY)
        self.s3_client = boto3.client(
            "s3",
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            region_name=AWS_REGION
        )
        self.today = str(date.today())
        self.results = {}       # ticker → validated data (clean records only)
        self.dead_letter = {}   # ticker → {"raw": ..., "errors": [...]}

    # ─────────────────────────────────────────
    # ABSTRACT METHODS — subclasses must implement
    # ─────────────────────────────────────────

    @abstractmethod
    def fetch(self, ticker: str) -> dict | list:
        """Makes the Finnhub API call for one ticker. Returns raw response."""
        pass

    # ─────────────────────────────────────────
    # SHARED METHODS — inherited by all subclasses
    # ─────────────────────────────────────────

    def extract(self) -> None:
        logger.info(f"Starting {self.ENDPOINT_NAME} ingest for {len(TICKERS)} tickers...")

        for i, ticker in enumerate(TICKERS):
            tick = time.time()  # start timer before the call

            try:
                validated_data = self.fetch_with_retry(ticker)
                self.results[ticker] = validated_data

            except ValidationError as e:
                errors = e.errors()
                logger.warning(f"{ticker}: validation failed — {len(errors)} issue(s)")
                for err in errors:
                    logger.warning(f"   field={err['loc']} | {err['msg']}")
                self.dead_letter[ticker] = {
                    "raw": getattr(e, "_raw", {}),
                    "errors": errors
                }

            except Exception as e:
                logger.error(f"{ticker}: API error — {str(e)}")
                self.dead_letter[ticker] = {
                    "raw": {},
                    "errors": [{"msg": f"API error: {str(e)}"}]
                }

            # Sleep only the remaining time to fill 1 full second
            if i < len(TICKERS) - 1:
                elapsed = time.time() - tick
                sleep_time = max(0, self.RATE_LIMIT_SECONDS - elapsed)
                time.sleep(sleep_time)

        logger.info(
            f"Extract complete — "
            f"{len(self.results)} clean / "
            f"{len(self.dead_letter)} dead-lettered / "
            f"{len(TICKERS)} total"
        )

    def fetch_with_retry(self, ticker: str, retries: int = 3) -> dict:
        """
        Fetches data for one ticker with exponential backoff retry.
        Validates the response through Pydantic immediately after fetch.
        Returns the validated record as a dict (via model_dump).
        Raises ValidationError if the record is invalid (no retry on bad data).
        Raises Exception if all API attempts fail.
        """
        raw = None
        for attempt in range(retries):
            try:
                raw = self.fetch(ticker)
                break  # API call succeeded — exit retry loop
            except Exception as e:
                if attempt < retries - 1:
                    wait = 2 ** attempt  # 1s, 2s, 4s
                    logger.warning(
                        f"{ticker}: attempt {attempt + 1} failed — "
                        f"retrying in {wait}s. Error: {str(e)}"
                    )
                    time.sleep(wait)
                else:
                    raise  # All retries exhausted — propagate to extract()

        # Validate immediately after a successful fetch
        # ValidationError is intentionally NOT caught here — it bubbles up
        # to extract() so the record is dead-lettered, not retried
        if not raw:
            raise ValueError(f"Empty response for {ticker}")
        try:
            validated = self.pydantic_model(**raw)
        except ValidationError as e:
            e._raw = raw  # Attach raw data so dead_letter can log it
            raise

        return validated.model_dump()

    def load(self) -> str:
        """
        Writes two NDJSON files to S3:
          1. Clean records  → BRONZE_PREFIX/<endpoint>/<endpoint>_raw_<date>.ndjson
          2. Dead-lettered  → BRONZE_PREFIX/<endpoint>/dead_letter/<endpoint>_dead_letter_<date>.ndjson
        """
        clean_key = self._upload_ndjson(
            records=self.results,
            filename=f"{self.ENDPOINT_NAME}_raw_{self.today}.ndjson",
            s3_prefix=f"{BRONZE_PREFIX}/{self.ENDPOINT_NAME}"
        )

        if self.dead_letter:
            self._upload_ndjson(
                records=self.dead_letter,
                filename=f"{self.ENDPOINT_NAME}_dead_letter_{self.today}.ndjson",
                s3_prefix=f"{BRONZE_PREFIX}/{self.ENDPOINT_NAME}/dead_letter"
            )

        return clean_key

    def _upload_ndjson(self, records: dict, filename: str, s3_prefix: str) -> str:
        """Writes a dict of records to a local NDJSON file then uploads to S3."""
        filepath = os.path.join(tempfile.gettempdir(), filename)

        with open(filepath, "w") as f:
            for ticker, data in records.items():
                f.write(json.dumps({
                    "ticker": ticker,
                    "pulled_at": self.today,
                    "data": data
                }) + "\n")

        logger.info(f"Saved locally: {filepath}")

        s3_key = f"{s3_prefix}/{filename}"

        try:
            self.s3_client.upload_file(
                Filename=filepath,
                Bucket=S3_BUCKET,
                Key=s3_key
            )
            logger.info(f"Uploaded to s3://{S3_BUCKET}/{s3_key}")
        except Exception as e:
            logger.error(f"S3 upload failed for {s3_key}: {str(e)}")
            raise

        os.remove(filepath)
        logger.info(f"Cleaned up temp file: {filepath}")

        return s3_key

    def summary(self, s3_key: str) -> None:
        """Logs run summary including dead-lettered tickers."""
        logger.info(f"\n{'='*50}")
        logger.info(f"SUMMARY — {self.ENDPOINT_NAME} — {self.today}")
        logger.info(f"{'='*50}")
        logger.info(f"✅ Clean records:     {len(self.results)} / {len(TICKERS)}")
        logger.warning(f"⚠️  Dead-lettered:    {len(self.dead_letter)} / {len(TICKERS)}")

        if self.dead_letter:
            for ticker, info in self.dead_letter.items():
                for err in info["errors"]:
                    logger.warning(f"   {ticker}: {err.get('msg', err)}")

        logger.info(f"📦 Clean data:  s3://{S3_BUCKET}/{s3_key}")
        if self.dead_letter:
            dl_key = s3_key.replace(
                f"{self.ENDPOINT_NAME}_raw",
                f"dead_letter/{self.ENDPOINT_NAME}_dead_letter"
            )
            logger.info(f"🪣 Dead letter: s3://{S3_BUCKET}/{dl_key}")

    def run(self) -> None:
        """Runs the full pipeline: extract (+ inline validation) → load → summary"""
        self.extract()
        s3_key = self.load()
        self.summary(s3_key)