from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.config.database import init_db
from app.api.student_routes import router as student_router
from app.api.department_routes import router as dept_router
from app.api.auth_routes import router as auth_router

@asynccontextmanager
async def lifeSpan(app: FastAPI):
    print("Server starting up with modular routers...")
    init_db()
    yield
    print("Server shutting down cleanly...")

app = FastAPI(
    title="Student Profile tracker",
    lifespan=lifeSpan
)

# Connect all your modular route clusters back to the core instance
app.include_router(student_router)
app.include_router(dept_router)
app.include_router(auth_router)

@app.get("/")
def Welcome():
    return {"Message": "Welcome to structurally modular Student Profile API"}