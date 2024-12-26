from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from datetime import datetime
from jose import JWTError, jwt
from src.security import get_db_pool, ALGORITHM, SECRET_KEY

class UpdateLastActiveMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        token = request.headers.get("Authorization")
        
        if token and token.startswith("Bearer "):  # Check if the token is present and correctly formatted
            token = token.split()[-1]  # Extract the actual token
            try:
                # Decode the token
                payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
                username = payload.get("sub")
                
                if username:
                    db_pool = await get_db_pool()
                    # Get a connection from the asyncpg pool
                    async with db_pool.acquire() as conn:
                        # Update last_active field in the database
                        await conn.execute(
                            """
                            UPDATE users
                            SET last_active = $1
                            WHERE username = $2
                            """,
                            datetime.utcnow(),
                            username,
                        )
            except JWTError:
                # Handle invalid token cases
                print("Invalid or expired JWT token")
            except Exception as e:
                # Handle other unexpected errors
                print(f"Error processing token: {e}")
        
        # Proceed with the request
        response = await call_next(request)
        return response
