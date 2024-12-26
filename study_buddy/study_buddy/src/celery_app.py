from celery import Celery
from celery.signals import task_success, task_failure
import requests
import asyncio
from utils import process_study_material
import os
from cachetools import TTLCache
import time
import agentops
agentops.init()


from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()



# FastAPI Backend URL from environment variable
FASTAPI_BACKEND_URL = os.getenv("FASTAPI_BACKEND_URL", "http://localhost:8000/update-task-result")

celery_app = Celery(
    "tasks",
    broker= "redis://localhost:6379/0",
    backend= "redis://localhost:6379/0",
)

@celery_app.task(autoretry_for=(Exception,) , max_retries=5)
def process_file_task(file_path , user_id):
    """
    Background task for processing a file asynchronously using asyncio.
    """
    try:
        result, token_usage = asyncio.run(process_study_material(file_path))
        print(f"Processing completed")
        return {"filename": file_path, "result": result , "user_id":user_id ,"metadata":token_usage.total_tokens}
    except Exception as e:
        print(f"An error occurred: {e}")
        return {"error": str(e)}
    

# Cache for storing the token and its expiration time
token_cache = TTLCache(maxsize=1, ttl=1800)  # Default TTL of 30 minutes

def get_auth_token():
    """
    Retrieve and cache the authentication token from the backend.
    Validates token expiration based on stored metadata.
    """
    # Check if the token is in cache and still valid
    if "token_data" in token_cache:
        token_data = token_cache["token_data"]
        if time.time() < token_data["expires_at"]:  # Token is still valid
            return token_data["access_token"]

    # Otherwise, request a new token
    token_endpoint = "http://127.0.0.1:8000/token"
    payload = {
        "username": "celery_service",
        "password": os.getenv("CELERY_SERVICE_ACCESS_PASSWORD")
    }
    try:
        response = requests.post(token_endpoint, data=payload, timeout=5)
        response.raise_for_status()
        data = response.json()
        token = data.get("access_token")
        expires_in = data.get("expires_in", 1800)  # Default to 30 minutes if not provided

        if not token:
            raise ValueError("No token received from the backend.")

        # Store token and expiration in the cache
        token_cache["token_data"] = {
            "access_token": token,
            "expires_at": time.time() + expires_in - 60  # Adjust to refresh 1 minute before expiration
        }

        return token
    except requests.RequestException as e:
        print(f"Failed to retrieve token: {e}")
        return None

def notify_backend(url, payload):
    """
    Notify the FastAPI backend with retries, including service authentication.
    """
    max_retries = 3
    headers = {
        "Authorization": f"Bearer {get_auth_token()}"
    }
    for attempt in range(max_retries):
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=5)
            response.raise_for_status()
            print(f"Notification sent successfully: {response.status_code}")
            return
        except requests.RequestException as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if attempt == max_retries - 1:
                print("Max retries reached. Notification failed.")


@task_success.connect
def on_task_success(sender=None, result=None, **kwargs):
    """
    Send the task result to the FastAPI backend upon successful completion.
    """
    task_id = sender.request.id
    url = f"{FASTAPI_BACKEND_URL}/{task_id}"
    payload = {"result": result}
    notify_backend(url, payload)

@task_failure.connect
def on_task_failure(sender=None, exception=None, **kwargs):
    """
    Notify the FastAPI backend of task failure.
    """
    task_id = sender.request.id
    url = f"{FASTAPI_BACKEND_URL}/{task_id}"
    payload = {"result": str(exception)}
    notify_backend(url, payload)
