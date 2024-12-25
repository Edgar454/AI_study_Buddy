import os
from jose import JWTError, jwt
from passlib.hash import bcrypt
from datetime import datetime, timedelta
from fastapi import Depends , HTTPException , status
from fastapi.security import OAuth2PasswordBearer
import asyncpg


# JWT configuration
SECRET_KEY = os.getenv("SECRET_KEY", "default-secret-key")  
ALGORITHM = "HS256"


# OAuth2PasswordBearer instance
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# PostgreSQL connection details
DATABASE_URL = os.getenv("DATABASE_URL")

db_pool = None

async def get_db_pool():
    global db_pool
    if db_pool is None:
        db_pool = await asyncpg.create_pool(DATABASE_URL)
    return db_pool



# Helper Functions
def create_access_token(data: dict, expires_delta: timedelta = None):
    """
    Generate a JWT access token.
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_user(db_pool, username: str):
    """
    Retrieve a user from the database by username.
    """
    async with db_pool.acquire() as conn:
        return await conn.fetchrow("SELECT * FROM users WHERE username = $1", username)


async def authenticate_user(db_pool, username: str, password: str):
    """
    Authenticate user by username and password.
    """
    user = await get_user(db_pool, username)
    if user and bcrypt.verify(password, user['hashed_password']):
        return user
    return None


async def get_current_user(token: str = Depends(oauth2_scheme), db_pool= None):
    """
    Get the currently authenticated user from the token.
    """
    if db_pool is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="DB Pool not available")
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if not username:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
        user = await get_user(db_pool, username)
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
        return user
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")


# Helper function to authenticate a user , this function decide which routes the user get access to
async def get_current_user(token: str = Depends(oauth2_scheme), db_pool=Depends(get_db_pool)):
    """
    Get the currently authenticated user from the token. This works for both users and services.
    """
    if db_pool is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="DB Pool not available")
    
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
async def get_current_service(token: str = Depends(oauth2_scheme) , db_pool=Depends(get_db_pool) ):
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