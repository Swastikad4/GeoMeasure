from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import init_db
from app.routes.health import router as health_router
from app.routes.files import router as files_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize SQLite database
    init_db()
    yield

app = FastAPI(
    title="Geospatial File Measurement API",
    description="Production-grade API to upload, parse, project, and calculate measurements on geospatial datasets (.kml and Shapefile .zip).",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(health_router, prefix="/api")
app.include_router(files_router, prefix="/api")

@app.get("/")
def root():
    return {
        "name": "Geospatial File Measurement API",
        "docs_url": "/docs",
        "health_check": "/api/health"
    }
