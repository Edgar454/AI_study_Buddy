from fastapi import APIRouter, Depends, HTTPException , status
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from src.security import get_db_pool , authenticate_user , create_access_token

# JWT configuration
ACCESS_TOKEN_EXPIRE_MINUTES = 30

router = APIRouter()

@router.post("/token/")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db_pool=Depends(get_db_pool)):
    """
    Login and get an access token.
    """
    user = await authenticate_user(db_pool, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    access_token = create_access_token(data={"sub": user['username'] ,
                                              "role":user['role']}, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    return {"access_token": access_token, "token_type": "bearer"}