from fastapi import FastAPI
from src.lifespan import lifespan
from src.routes import users ,auth , tasks
from src.metrics import  configure_instrumentator
from src.middleware import UpdateLastActiveMiddleware

app = FastAPI(lifespan = lifespan)
app.add_middleware(UpdateLastActiveMiddleware)
instrumentator = configure_instrumentator()
instrumentator.instrument(app).expose(app)


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
