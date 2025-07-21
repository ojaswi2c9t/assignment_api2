import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.config import settings
from core.database import connect_to_mongo, close_mongo_connection
from routes import api_router

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    description="E-Commerce API with FastAPI and MongoDB",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount versioned routes
app.include_router(api_router, prefix=settings.API_PREFIX)

# Database connection
@app.on_event("startup")
async def startup_db_client():
    logger.info("Starting up application")
    await connect_to_mongo()

@app.on_event("shutdown")
async def shutdown_db_client():
    logger.info("Shutting down application")
    await close_mongo_connection()

# Root endpoint
@app.get("/", include_in_schema=False)
async def root():
    return {
        "message": f"Welcome to {settings.PROJECT_NAME}!",
        "version": settings.PROJECT_VERSION,
        "docs_url": "/api/docs",
        "health_endpoint": "/health"
    }

# Health check
@app.get("/health", include_in_schema=False)
async def health():
    return {"status": "healthy"} 