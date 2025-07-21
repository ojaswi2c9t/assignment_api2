import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError

from core.config import settings
from core.database import connect_to_mongo, close_mongo_connection
from core.logging import setup_logging
from routes import api_router
from utils.errors import (
    APIError,
    api_error_handler,
    http_exception_handler,
    validation_exception_handler,
    general_exception_handler,
)

# Setup logging
setup_logging()
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
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register exception handlers
app.add_exception_handler(APIError, api_error_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(ValidationError, validation_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# Mount versioned routes
app.include_router(api_router, prefix=settings.API_PREFIX)

# Database connection
@app.on_event("startup")
async def startup_db_client():
    logger.info("💚 Starting up application")
    await connect_to_mongo()

@app.on_event("shutdown")
async def shutdown_db_client():
    logger.info("💔 Shutting down application")
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
