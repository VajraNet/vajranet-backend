import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from app.core.config import settings
from app.core.response import error_response
from app.api.router import api_router
from app.db.session import engine
from app.models.base import Base

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.ENVIRONMENT.upper() == "DEVELOPMENT" and "DEBUG" or "INFO"),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Ensure database schema tables exist gracefully
    logger.info("Connecting to database and verifying VajraNet schema...")
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("VajraNet database schema verified and ready for emergency coordination.")
    except Exception as exc:
        logger.warning(
            f"Database connection warning at boot: {exc}. "
            "If using Supabase on Render/IPv4 hosts, ensure you use the Supabase Pooler URL "
            "(port 6543 / pooler.supabase.com) instead of the direct IPv6 database host."
        )
    yield
    # Shutdown
    logger.info("VajraNet backend shutting down gracefully.")


app = FastAPI(
    title="VAJRANET Disaster Communication & Emergency Response API",
    description=(
        "Production-grade backend for VajraNet. Connects Citizens, Government Authorities, "
        "and Volunteers during disasters via online REST APIs and offline mesh gateway synchronization."
    ),
    version=settings.VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Configure CORS for All Local and Deployed Frontends
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"https?://.*|capacitor://.*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global Exception Handlers for Predictable REST Responses
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return error_response(
        message=exc.detail if isinstance(exc.detail, str) else "HTTP error occurred",
        status_code=exc.status_code,
        data=exc.detail if not isinstance(exc.detail, str) else None
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    msg = "Validation error in request payload"
    if errors:
        msg = f"Invalid field: {errors[0].get('loc', ['field'])[-1]} - {errors[0].get('msg', 'invalid')}"
    return error_response(
        message=msg,
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        data=errors
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled system error: {exc}", exc_info=True)
    return error_response(
        message="An internal server error occurred while processing the request",
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
    )


# Root Endpoint (For UptimeRobot, Render Health Pings & Root Browsing)
@app.get("/", summary="Root Health Endpoint", tags=["System Health"])
@app.head("/", summary="Root Health Endpoint", tags=["System Health"])
def root():
    """
    Root status endpoint returning 200 OK for UptimeRobot, Render, and uptime monitors.
    """
    return {
        "status": "online",
        "service": "VAJRANET Disaster Communication & Emergency Response API",
        "version": settings.VERSION,
        "docs": "/docs",
        "health": "/health"
    }


# Health Check Endpoint
@app.get("/health", summary="Health Check", tags=["System Health"])
@app.head("/health", summary="Health Check", tags=["System Health"])
def health_check():
    """
    Production health check endpoint for Render and uptime monitoring.
    """
    return {"status": "ok"}


@app.get("/system/status", summary="System Status & Feature Flags", tags=["System Health"])
def system_status():
    """
    Returns deployment environment status and feature flag toggles.
    """
    return {
        "status": "operational",
        "environment": settings.ENVIRONMENT,
        "ai_enabled": settings.ENABLE_AI,
        "ai_url": settings.VAJRA_AI_URL,
        "cloudinary_enabled": settings.ENABLE_CLOUDINARY
    }


# Mount API v1
app.include_router(api_router)
