import ast
import logging
import os
from contextlib import contextmanager
from typing import Dict

import pandas as pd
from sqlalchemy.dialects.postgresql import insert

from app.core.db import SessionLocal
from app.models import (
    Movie,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@contextmanager
def get_db_session():
    """Context manager for database sessions"""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()


def parse_array(array_str: str) -> list:
    """Parse string array representation to list"""
    try:
        if pd.isna(array_str):
            return []
        return ast.literal_eval(array_str)
    except (ValueError, SyntaxError):
        logger.warning(f"Failed to parse array: {array_str}")
        return []


def process_row(row) -> Dict:
    """Process a single movie row from CSV"""
    release_date = (
        pd.to_datetime(row["release_date"]).date()
        if pd.notna(row["release_date"])
        else None
    )
    homepage = None if pd.isna(row["homepage"]) else row["homepage"]

    return {
        "title": row["title"],
        "original_title": row["original_title"],
        "original_language": row["original_language"],
        "overview": row["overview"],
        "release_date": release_date,
        "budget": row["budget"],
        "revenue": row["revenue"],
        "runtime": row["runtime"],
        "status": row["status"],
        "vote_average": row["vote_average"],
        "vote_count": row["vote_count"],
        "languages": parse_array(row["languages"]),
        "homepage": homepage,
        "genre_id": row["genre_id"],
        "production_company_id": row["production_company_id"],
    }


def ingest_movies(csv_path: str, batch_size: int = 1000):
    """Ingest movies from CSV in batches using lazy loading"""
    logger.info(f"Starting ingestion from {csv_path}")

    TEMP_DIR = "/temp"
    absolute_path = (
        csv_path if csv_path.startswith("/") else os.path.join(TEMP_DIR, csv_path)
    )

    chunk_iterator = pd.read_csv(
        absolute_path,
        chunksize=batch_size,
        dtype={"genre_id": "Int64", "production_company_id": "Int64"},
    )

    processed_chunks = 0
    for chunk in chunk_iterator:
        with get_db_session() as db:
            try:
                movies_data = (process_row(row) for _, row in chunk.iterrows())

                for batch in batch_generator(movies_data, size=1000):
                    db.execute(insert(Movie).values(batch).on_conflict_do_nothing())

                processed_chunks += 1
                logger.info(f"Processed chunk {processed_chunks}: {len(chunk)} rows")
            except Exception as e:
                logger.error(f"Error processing chunk {processed_chunks}: {e}")
                raise

    logger.info("CSV ingestion completed successfully")


def batch_generator(iterable, size=1000):
    """Generate batches from an iterable"""
    batch = []
    for item in iterable:
        batch.append(item)
        if len(batch) >= size:
            yield batch
            batch = []
    if batch:
        yield batch
