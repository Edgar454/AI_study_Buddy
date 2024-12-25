from fastapi import FastAPI
from src.lifespan import lifespan
from src.routes import users ,auth , tasks

app = FastAPI(lifespan = lifespan)

# Routes
@app.get("/")
async def root():
    """
    Root endpoint.
    """
    return {"message": "Welcome Buddy, I'm here to help!"}

app.include_router(users.router)
app.include_router(auth.router)
app.include_router(tasks.router)
