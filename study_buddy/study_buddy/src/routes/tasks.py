import shutil
from collections import deque
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException , UploadFile, File , Request
from src.security import get_current_service , get_current_user , get_db_pool

from celery.result import AsyncResult
from src.celery_app import process_file_task , celery_app
from src.config import UPLOAD_DIR  , CACHE_SIZE


router = APIRouter()

@router.post("/process-material/")
async def process_material(request: Request,file: UploadFile = File(...), current_user=Depends(get_current_user)):
    """
    Process the uploaded study material file.
    """
    user_id = current_user["id"]
    processed_cache = request.app.state.processed_cache
    
    try:
        # Get the user's cache and build a lookup dictionary
        user_cache = processed_cache.get(user_id, [])
        cache_index = {entry["filename"]: entry["result"] for entry in user_cache}

        # Check if the file is already processed
        if file.filename in cache_index:
            result = cache_index[file.filename]
            return {"message": "File processed successfully (from cache)!", "result": result}
        
        file_path = Path(UPLOAD_DIR.name) / file.filename
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Call the Celery task
        task = process_file_task.delay(file_path = str(file_path),
                                        user_id = user_id)

        # Store task ID in the cache to track progress
        processed_cache.setdefault(user_id, deque(maxlen=CACHE_SIZE)).append({
            "filename": file.filename,
            "task_id": task.id
        })

        return {"message": "Processing started", "task_id": task.id}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

@router.get("/task-status/{task_id}")
def get_task_status(task_id: str, current_user=Depends(get_current_user)):
    # Get the task status from Celery
    task = AsyncResult(task_id , app = celery_app)

    if task.state == "PENDING":
        return {"status": "Pending"}
    
    elif task.state == "SUCCESS":
        return {"status": "Success"}
    
    elif task.state == "FAILURE":
        return {"status": "Failure", "error": str(task.result)}
    else:
        return {"status": task.state}
    
@router.post("/update-task-result/{task_id}")
async def update_task_result(task_id: str,
                            payload: dict,
                            request: Request ,
                            current_service=Depends(get_current_service)):
    """
    Update the task result in the cache.
    """
    processed_cache = request.app.state.processed_cache
    result = payload.get("result")
    user_id = result['user_id']
    total_tokens = result['metadata']
    error = payload.get("error")

    # Update the cache for the user
    user_cache = processed_cache.setdefault(user_id, deque(maxlen=CACHE_SIZE))
    for entry in user_cache:
        if entry.get("task_id") == task_id:
            # Update the entry with the final result or error
            if result:
                entry.update({"result": result['result']})
                entry.pop("task_id", None)  # Remove task_id once completed
            elif error:
                print(error)
                entry.update({"result": None})
                entry.pop("task_id", None)
            break
    
    # add the activity related metrics to the databases
    db_pool = await get_db_pool()
    async with db_pool.acquire() as conn:              
        await conn.execute(
                        """
                        INSERT INTO user_activity (user_id, tokens_used) 
                        VALUES ($1, $2);
                        """,user_id, total_tokens
                        )

    return {"message": "Task result updated successfully!"}