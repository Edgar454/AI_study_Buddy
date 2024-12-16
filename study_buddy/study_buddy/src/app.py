import os
import shutil
import tempfile
import json
from pathlib import Path
from datetime import datetime, timedelta
from collections import deque
from contextlib import asynccontextmanager

import asyncpg
from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, status , Header
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.hash import bcrypt

from celery.result import AsyncResult
from celery_app import process_file_task , celery_app

from security import create_access_token ,get_user ,authenticate_user



# Temporary directory for uploaded files
UPLOAD_DIR = tempfile.TemporaryDirectory()

# Cache size for storing recent results
CACHE_SIZE = 5
processed_cache = {}

# PostgreSQL connection details
DATABASE_URL = os.getenv("DATABASE_URL")

# JWT configuration
SECRET_KEY = os.getenv("SECRET_KEY", "default-secret-key")  # Use a fallback for testing
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# OAuth2PasswordBearer instance
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app = FastAPI()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan context manager for initializing and cleaning up resources.
    """
    db_pool = await asyncpg.create_pool(DATABASE_URL)
    async with db_pool.acquire() as conn:
        # Create necessary tables
        await conn.execute(""" 
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            hashed_password TEXT NOT NULL
        )
        """)
        await conn.execute(""" 
        CREATE TABLE IF NOT EXISTS events (
            id SERIAL PRIMARY KEY,
            filename TEXT NOT NULL,
            result JSONB NOT NULL,
            user_id INTEGER NOT NULL REFERENCES users(id)
        )
        """)

    app.state.db_pool = db_pool

    # Load recent results from the database into the cache
    async with db_pool.acquire() as conn:
        rows = await conn.fetch("""
        SELECT user_id, filename, result FROM events
        """)
        for row in rows:
            processed_cache.setdefault(row["user_id"], deque(maxlen=CACHE_SIZE)).append({
                "filename": row["filename"],
                "result": row["result"]
            })

    yield

    # Save recent results to the database on shutdown
    async with db_pool.acquire() as conn:
        for user_id, events in processed_cache.items():
            for event in events:
                await conn.execute("""
                INSERT INTO events (filename, result, user_id)
                VALUES ($1, $2, $3)
                ON CONFLICT (id) DO NOTHING
                """, event["filename"], json.dumps(event["result"]), user_id)

            # Retain only the last 5 results for each user in the database
            await conn.execute("""
            DELETE FROM events
            WHERE user_id = $1 AND id NOT IN (
                SELECT id FROM events
                WHERE user_id = $1
                ORDER BY id DESC
                LIMIT 5
            )
            """, user_id)

    await db_pool.close()
    UPLOAD_DIR.cleanup()


app = FastAPI(lifespan=lifespan)



# Helper function to authenticate a user , this function decide which routes the user get access to
async def get_current_user(token: str = Depends(oauth2_scheme), db_pool=Depends(lambda: app.state.db_pool)):
    """
    Get the currently authenticated user from the token. This works for both users and services.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        role = payload.get("role")  # Check the role from the token
        if not username:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
        
        # Retrieve user from the database (if needed)
        user = await get_user(db_pool, username)
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
        
        return user
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    
# Helper function to authenticate a service , this function decide which routes the service get access to
async def get_current_service(token: str = Depends(oauth2_scheme)):
    """
    Custom dependency to ensure only the Celery service can update the cache.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        role = payload.get("role")  # Check the role from the token
        if not username:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
        
        # Ensure that the role is 'service' and check if the service name matches the expected service (e.g., Celery)
        if role != "service":
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied: You are not a service user")
        
        if username != "celery_service":  # Ensure the request is coming from the Celery service
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied: Invalid service")
        
        return {"username": username, "role": role}
    
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")





# Routes
@app.get("/")
async def root():
    """
    Root endpoint.
    """
    return {"message": "Welcome Buddy, I'm here to help!"}


@app.post("/register/")
async def register_user(username: str, password: str, db_pool=Depends(lambda: app.state.db_pool)):
    """
    Register a new user.
    """
    hashed_password = bcrypt.hash(password)
    async with db_pool.acquire() as conn:
        try:
            await conn.execute("INSERT INTO users (username, hashed_password) VALUES ($1, $2)", username, hashed_password)
            return {"message": "User registered successfully!"}
        except asyncpg.UniqueViolationError:
            raise HTTPException(status_code=400, detail="Username already taken")


@app.post("/token/")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db_pool=Depends(lambda: app.state.db_pool)):
    """
    Login and get an access token.
    """
    user = await authenticate_user(db_pool, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    access_token = create_access_token(data={"sub": user['username'] ,
                                              "role":user['role']}, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/recent-results/")
async def recent_results(current_user=Depends(get_current_user)):
    """
    Get recent processed results for the current user.
    """
    user_id = current_user["id"]
    return list(processed_cache.get(user_id, []))


@app.post("/process-material/")
async def process_material(file: UploadFile = File(...), current_user=Depends(get_current_user)):
    """
    Process the uploaded study material file.
    """
    user_id = current_user["id"]
    
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


@app.get("/task-status/{task_id}")
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

@app.post("/update-task-result/{task_id}")
async def update_task_result(task_id: str,
                            payload: dict,
                            current_service =Depends(get_current_service)):
    """
    Update the task result in the cache.
    """
    
    result = payload.get("result")
    user_id = result['user_id']
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

    return {"message": "Task result updated successfully!"}

