import os
import uuid
from typing import Optional

from fastapi import APIRouter, BackgroundTasks, File, HTTPException, UploadFile, Query
from fastapi.responses import JSONResponse

from celery_app.tasks import process_csv

router = APIRouter(tags=["CSV Upload"])


@router.post("/upload/")
async def upload_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    use_celery: Optional[bool] = Query(
        default=False,
        description="If true, uses Celery for processing. If false, uses FastAPI background tasks."
    )
):
    MAX_SIZE = 1000 * 1024 * 1024  # 1000 MB
    file_size = 0

    TEMP_DIR = "/temp" 
    task_id = str(uuid.uuid4())
    temp_file_path = os.path.join(TEMP_DIR, f"{task_id}_{file.filename}")
    
    try:
        with open(temp_file_path, "wb") as buffer:
            while chunk := await file.read(8192):
                file_size += len(chunk)
                if file_size > MAX_SIZE:
                    raise HTTPException(
                        status_code=413,
                        detail="File too large"
                    )
                buffer.write(chunk)

        if not file.filename.endswith(".csv"):
            raise HTTPException(
                status_code=400,
                detail="Invalid file type"
            )

        if use_celery:
            # Use Celery task
            celery_task = process_csv.delay(task_id, temp_file_path)
            response_data = {
                "upload_id": task_id,
                "status": "pending",
                "celery_task_id": celery_task.id
            }
        else:
            background_tasks.add_task(
                process_csv,
                task_id,
                temp_file_path
            )
            response_data = {
                "upload_id": task_id,
                "status": "pending"
            }
        
        return JSONResponse(
            content=response_data,
            status_code=202
        )
    
    except HTTPException as http_ex:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
        raise http_ex
    
    except Exception as e:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )
