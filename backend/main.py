from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from core.config import settings
from core.database import connect_to_mongo, close_mongo_connection
from routers import auth, detect, results, contact

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    # Startup
    await connect_to_mongo()
    yield
    # Shutdown
    await close_mongo_connection()


app = FastAPI(
    title="AI Content Verifier API",
    description="Backend API for AI content detection",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware - must be added before routers
# Combine default origins with environment variable origins
default_origins = ["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:5173"]
cors_origins = default_origins + (settings.CORS_ORIGINS if isinstance(settings.CORS_ORIGINS, list) else [])
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(detect.router)
app.include_router(results.router)
app.include_router(contact.router)


@app.get("/")
async def root():
    return {
        "message": "AI Content Verifier API",
        "status": "running",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


