import asyncpg
from fastapi import APIRouter, Depends, HTTPException , Request
from passlib.hash import bcrypt
from src.security import get_db_pool , get_current_user
from src.utils import get_redis_client 

router = APIRouter()

@router.post("/register/")
async def register_user(username: str, password: str, db_pool=Depends(get_db_pool)):
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

@router.get("/recent-results/")
async def recent_results(request: Request ,current_user=Depends(get_current_user) ):
    """
    Get recent processed results for the current user.
    """
    user_id = current_user["id"]
    redis_client = await get_redis_client()
    processed_cache =  await redis_client.hgetall(f"user_id:{user_id}")
    return processed_cache

