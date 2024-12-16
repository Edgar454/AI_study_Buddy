from celery import Celery
from celery.signals import task_success, task_failure
import requests
import asyncio
from utils import process_study_material
import os

# FastAPI Backend URL from environment variable
FASTAPI_BACKEND_URL = os.getenv("FASTAPI_BACKEND_URL", "http://localhost:8000/update-task-result")

celery_app = Celery(
    "tasks",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0",
)

@celery_app.task
def process_file_task(file_path):
    """
    Background task for processing a file asynchronously using asyncio.
    """
    try:
        result, _ = asyncio.run(process_study_material(file_path))
        print(f"Processing completed")
        return {"filename": file_path, "result": result}
    except Exception as e:
        print(f"An error occurred: {e}")
        return {"error": str(e)}

def notify_backend(url, payload):
    """
    Notify the FastAPI backend with retries, including service authentication.
    """
    max_retries = 3
    headers = {
        "Authorization": f"Bearer {os.getenv('CELERY_SERVICE_TOKEN')}"
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
    payload = {"error": str(exception)}
    notify_backend(url, payload)
