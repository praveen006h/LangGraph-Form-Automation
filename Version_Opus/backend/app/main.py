from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.database import engine, Base
from app.seed import seed_database
from app.routers import chat, data


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create tables and seed data on startup."""
    Base.metadata.create_all(bind=engine)
    seed_database()
    yield


app = FastAPI(
    title="HCP CRM AI Assistant",
    description="AI-First CRM for Healthcare Professional Interaction Logging",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:5174", "http://127.0.0.1:5174"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router)
app.include_router(data.router)


@app.get("/api/health")
async def health_check():
    return {"status": "ok", "message": "HCP CRM AI Assistant is running"}
