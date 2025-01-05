import json
import os

import pandas as pd
from celery import Celery

from app.core.config import settings
from app.core.db import redis_client
from celery_app.csv_ingestor import ingest_movies

TASK_TTL = 60 * 60 * 24  # 24 hours in seconds


celery_app = Celery('tasks', broker=settings.REDIS_URI)

def create_task_key(task_id: str) -> str:
    return f"upload_task:{task_id}"

def create_task_state(filename: str) -> dict:
    return {
        "filename": filename,
        "status": "pending",
        "total_rows": 0,
        "processed_rows": 0,
        "error_message": None,
        "created_at": pd.Timestamp.now().isoformat()
    }

def update_task_state(task_id: str, updates: dict):
    task_key = create_task_key(task_id)
    current_state = redis_client.get(task_key)
    
    if current_state:
        state = json.loads(current_state)
        state.update(updates)
        redis_client.set(task_key, json.dumps(state), ex=TASK_TTL)

@celery_app.task
def process_csv(task_id: str, file_path: str):

    
    try:

        ingest_movies(csv_path=file_path)
        
        update_task_state(task_id, {"status": "completed"})
        
    except Exception as e:
        update_task_state(task_id, {
            "status": "failed",
            "error_message": str(e)
        })
        raise
    
    finally:
        os.remove(file_path)