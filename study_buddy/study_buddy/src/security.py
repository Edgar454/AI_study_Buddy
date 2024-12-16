import os
from jose import JWTError, jwt
from passlib.hash import bcrypt
from datetime import datetime, timedelta
from fastapi import Depends , HTTPException , status
from fastapi.security import OAuth2PasswordBearer


# JWT configuration
SECRET_KEY = os.getenv("SECRET_KEY", "default-secret-key")  
ALGORITHM = "HS256"



# OAuth2PasswordBearer instance
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


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


async def get_current_user(token: str = Depends(oauth2_scheme), db_pool=Depends()):
    """
    Get the currently authenticated user from the token.
    """
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
