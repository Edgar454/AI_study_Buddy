import os 
from passlib.hash import bcrypt
import asyncio
import asyncpg
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# PostgreSQL connection details
DATABASE_URL = os.getenv("DATABASE_URL")
password = os.getenv("CELERY_SERVICE_ACCESS_PASSWORD")


async def setup_services():
    db_pool = await asyncpg.create_pool(DATABASE_URL)
    hashed_password = bcrypt.hash(password)
    async with db_pool.acquire() as conn:
        await conn.execute(""" INSERT INTO users (username, hashed_password,role)
                            VALUES ($1, $2,$3)
                           ON CONFLICT (username) DO NOTHING ;""", 'celery_service', hashed_password,"service")
        
    print('Services Added Successfully')

if __name__ == '__main__' :
    asyncio.run(setup_services())