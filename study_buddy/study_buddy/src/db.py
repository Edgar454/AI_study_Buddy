from collections import deque
import json


async def init_app(db_pool , processed_cache,CACHE_SIZE = 5 ):
    """ Function to execute when the server start up ,
    it creates the database if necessary and load the last 5 processed documents"""

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


async def shutdown_app(db_pool , processed_cache):
    """ Function to execute when the server shutdown ,
    it save the last 5 results into the database and remove past entries"""

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