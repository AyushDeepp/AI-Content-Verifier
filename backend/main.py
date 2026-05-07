from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from fastapi.staticfiles import StaticFiles
import os
import logging

from core.config import settings
from core.database import connect_to_mongo, close_mongo_connection
from core.key_rotator import init_rotators
from routers import auth, detect, results, contact

os.makedirs("uploads", exist_ok=True)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    # Startup
    await connect_to_mongo()
    init_rotators(settings.GEMINI_API_KEY or "", settings.GROQ_API_KEY or "")
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
default_origins = [
    "http://localhost:3000", 
    "http://127.0.0.1:3000", 
    "http://localhost:5173", 
    "https://ai-content-verifier.netlify.app",
    "https://credence-ai.netlify.app"
]
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

from starlette.middleware.base import BaseHTTPMiddleware

class UploadsCORPMiddleware(BaseHTTPMiddleware):
    """Add Cross-Origin-Resource-Policy header to /uploads static files
       so browsers allow cross-origin video/image playback."""
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        if request.url.path.startswith("/uploads"):
            response.headers["Cross-Origin-Resource-Policy"] = "cross-origin"
            response.headers["Access-Control-Allow-Origin"] = "*"
        return response

app.add_middleware(UploadsCORPMiddleware)

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


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


