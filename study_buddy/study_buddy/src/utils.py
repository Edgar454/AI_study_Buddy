import os
import json
from study_buddy.crew import StudyBuddy
from pathlib import Path
from dotenv import load_dotenv
from redis.asyncio import Redis
import hashlib

# Load environment variables from .env file
load_dotenv()



async def process_study_material(file_path: Path):
    """
    Process the study material and return the results.
    Replace this placeholder with the actual logic for processing the file.
    """
    try:
        inputs = {
            'study_material_path': file_path
        }
        results = await StudyBuddy().crew().kickoff_async(inputs=inputs)
        results = dict(results)
        tasks = ['explanation', 'evaluation', 'flashcard_building', 'summary']
        tasks_output = results['tasks_output'][1:]
        final_result = {task: task_output.raw for task, task_output in zip(tasks, tasks_output)}
        return final_result, results['token_usage']
    
    except Exception as e:
        raise RuntimeError(f"Error processing material: {str(e)}")
    
# Redis configuration
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")

async def get_redis_client():
    client = Redis(host= REDIS_HOST, port=6379, db=0)
    return client


# hash the file content to check if it has already been processed
def get_file_hash(file_obj, chunk_size: int = 8192) -> str:
    sha256 = hashlib.sha256()
    while chunk := file_obj.read(chunk_size):
        sha256.update(chunk)
    file_obj.seek(0)  
    return sha256.hexdigest()

# celery task to process the file
async def process_file_main(file_path: Path, user_id: str, file_id: str):
    """
    Main function to process the file and return the results.
    """
    try:
        redis_client = await get_redis_client()
        result = await redis_client.hget(f"user_id:{user_id}", file_id)
        if result:
            print(f"File {file_id}  found in cache. Reeturning")
            # Deserialize the result
            deserialized_result = json.loads(result.decode())
            return {"filename": file_path, "result": deserialized_result , "user_id":user_id , "metadata": 0}
        else:
            print(f"File {file_id} not found in cache. Processing...")
            result, token_usage = await process_study_material(file_path)

            # Store the result in Redis cache
            await redis_client.hset(f"user_id:{user_id}", file_id, json.dumps(result))
            
            print(f"Processing completed")
            return {"filename": file_path, "result": result , "user_id":user_id ,"metadata":token_usage.total_tokens}
    except Exception as e:
        print(f"An error occurred: {e}")
        return {"error": str(e)}