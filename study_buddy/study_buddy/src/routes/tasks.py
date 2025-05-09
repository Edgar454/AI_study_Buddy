import shutil
import json
import datetime
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException , UploadFile, File , Request
from src.security import get_current_service , get_current_user , get_db_pool

from celery.result import AsyncResult
from src.celery_app import process_file_task , celery_app
from src.config import UPLOAD_DIR  , CACHE_SIZE
from src.utils import get_file_hash , get_redis_client



router = APIRouter()

@router.post("/process-material/")
async def process_material(request: Request,file: UploadFile = File(...), current_user=Depends(get_current_user)):
    """
    Process the uploaded study material file.
    """
    user_id = current_user["id"]
    
    try:
        
        file_path = Path(UPLOAD_DIR.name) / file.filename
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        file_hash = get_file_hash(file_path)
        print(f"File hash: {file_hash}")
        print(f"Processing file : {file.filename}")

        # Call the Celery task
        task = process_file_task.delay(file_path = str(file_path),
                                        user_id = user_id,
                                        file_id = file_hash)

        return {"message": "Processing started", "task_id": task.id , "file_id": file_hash}
        
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
    
@router.get("/get-task-result/")
async def get_task_result(file_id: str, current_user=Depends(get_current_user)):
    redis_client = await get_redis_client()
    user_id = current_user["id"]

    # Check if the file is in the cache
    result = await redis_client.hget(user_id, file_id)
    if result:
        # Deserialize the result
        deserialized_result = json.loads(result.decode())
        return {"result": deserialized_result}
    else:
        raise HTTPException(status_code=404, detail="File not found in cache")
    
@router.post("/update-task-result/{task_id}")
async def update_task_result(task_id: str,
                            payload: dict,
                            current_service=Depends(get_current_service)):
    """
    Update the task result in the cache.
    """
    result = payload.get("result")
    if result.get('user_id'):
        user_id = result['user_id']
        total_tokens = result['metadata']
        
        # add the activity related metrics to the databases
        db_pool = await get_db_pool()
        async with db_pool.acquire() as conn:              
            await conn.execute(
                            """
                            INSERT INTO user_activity (user_id, tokens_used, timestamp) 
                            VALUES ($1, $2 , $3);
                            """,user_id, total_tokens,datetime.datetime.now()
                            )

        return {"message": "Task result updated successfully!"}
    else:
         return {"message": f"Task failed. {result['error']}"}
   