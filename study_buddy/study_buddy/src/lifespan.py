import os 
import json
import asyncpg
from collections import deque
from contextlib import asynccontextmanager
from fastapi import FastAPI
from dotenv import load_dotenv
from config import processed_cache , UPLOAD_DIR , CACHE_SIZE

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

    app.state.db_pool = db_pool
    app.state.processed_cache = {}

    # Load recent results from the database into the cache
    async with db_pool.acquire() as conn:
        rows = await conn.fetch("""
        SELECT user_id, filename, result FROM events
        """)
        for row in rows:
            deserialized_result = json.loads(row["result"]) if isinstance(row["result"], str) else row["result"]
            app.state.processed_cache.setdefault(row["user_id"], deque(maxlen=CACHE_SIZE)).append({
                "filename": row["filename"],
                "result": deserialized_result
            })

    yield
    # Save recent results to the database on shutdown
    async with db_pool.acquire() as conn:
        for user_id, events in app.state.processed_cache.items():
            for event in events:
                result_json = json.dumps(event["result"])
                await conn.execute("""
                INSERT INTO events (filename, result, user_id)
                VALUES ($1, $2, $3)
                ON CONFLICT (id) DO NOTHING
                """, event["filename"], result_json, user_id)

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