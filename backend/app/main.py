"""Digital Ophthalmology Assistant - FastAPI Application.

Main application entry point with middleware, routes, and startup/shutdown events.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.database.db import get_db, init_db
from app.routes.content import router as content_router
from app.routes.library import router as library_router
from app.routes.predict import router as predict_router
from app.routes.questions import router as questions_router
from app.routes.results import router as results_router
from app.services.seed_service import seed_content

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Load settings
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup and shutdown events."""
    # Startup
    logger.info("Starting up Digital Ophthalmology Assistant...")

    # Initialize database
    init_db()
    logger.info("Database initialized")

    # Seed initial content
    db = next(get_db())
    try:
        seed_content(db)
        logger.info("Database seeded with initial content")
    except Exception as e:
        logger.warning(f"Failed to seed database: {e}")
    finally:
        db.close()

    # Preload DL model
    try:
        from app.services.ai_service import get_model  # noqa: PLC0415

        get_model(settings.resolved_model_path)
        logger.info(f"DL model loaded from {settings.resolved_model_path}")
    except FileNotFoundError:
        logger.warning("DL model not found. Prediction endpoint will fail until model is added.")
    except Exception as e:
        logger.warning(f"Failed to preload DL model: {e}")

    logger.info(f"Server ready at http://{settings.host}:{settings.port}")

    yield

    # Shutdown
    logger.info("Shutting down...")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="AI-powered ophthalmology assistant for anterior eye disease classification",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=settings.cors_allow_methods,
    allow_headers=settings.cors_allow_headers,
)


# Health check endpoint
@app.get("/health", tags=["health"])
async def health_check():
    """Health check endpoint for monitoring and load balancers."""
    return {"status": "healthy", "version": settings.app_version}


# Root endpoint
@app.get("/", tags=["root"])
async def root():
    """Root endpoint with API information."""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "docs": "/docs",
        "health": "/health",
    }


# Custom exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(_: Request, exc: HTTPException):
    """Handle HTTP exceptions with consistent format."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "status_code": exc.status_code},
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    """Handle unhandled exceptions with logging."""
    logger.error(f"Unhandled exception in {request.method} {request.url}: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "status_code": 500},
    )


# Include routers
app.include_router(predict_router)
app.include_router(results_router)
app.include_router(questions_router)
app.include_router(content_router)
app.include_router(library_router)