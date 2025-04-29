import os 
import json
import asyncpg
import asyncio
from contextlib import asynccontextmanager 
from fastapi import FastAPI
from dotenv import load_dotenv
from config import  UPLOAD_DIR 
from src.metrics import  run_periodic_tasks , shutdown_event  
from src.utils import get_redis_client



# Load environment variables from .env file
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

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
            hashed_password TEXT NOT NULL ,
            last_active TIMESTAMP DEFAULT NOW(), 
            role VARCHAR(50) DEFAULT 'user'
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
        await conn.execute(""" 
        CREATE TABLE IF NOT EXISTS user_activity (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL,
            tokens_used INTEGER NOT NULL,
            timestamp TIMESTAMP DEFAULT NOW(),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
        """)

    app.state.db_pool = db_pool
    redis_client = await get_redis_client()
    # scrapping metrics periodicaly
    asyncio.create_task(run_periodic_tasks())

    # Load recent results from the database into the cache
    async with db_pool.acquire() as conn:
        rows = await conn.fetch("""
        SELECT user_id, filename, result FROM events
        """)
        for row in rows:
            await redis_client.hset(row["user_id"] , row["filename"] ,row["result"])

    
    yield
    shutdown_event.set()
    user_ids = await redis_client.keys("user_id:*")

    async with db_pool.acquire() as conn:
        for user_id in user_ids:
            raw_events = await redis_client.hgetall(user_id)
            events = []
            for file_id, result_bytes in raw_events.items():
                result = json.loads(result_bytes.decode())
                id = int(user_id.decode().split(":")[1])
                events.append({"filename": file_id, "result": result, "user_id": id})

            for event in events:
                result_json = json.dumps(event["result"])
                await conn.execute("""
                    INSERT INTO events (filename, result, user_id)
                    VALUES ($1, $2, $3)
                    ON CONFLICT (id) DO NOTHING
                """, event["filename"].decode(), result_json, event["user_id"] )

            await conn.execute("""
                DELETE FROM events
                WHERE user_id = $1 AND id NOT IN (
                    SELECT id FROM events
                    WHERE user_id = $1
                    ORDER BY id DESC
                    LIMIT 5
                )
            """, event["user_id"])

    await db_pool.close()
    UPLOAD_DIR.cleanup()