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
    # Startup: Ensure database schema tables exist
    logger.info("Initializing VajraNet database schema...")
    Base.metadata.create_all(bind=engine)
    logger.info("VajraNet backend ready for emergency coordination.")
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


# Health Check Endpoint
@app.get("/health", summary="Health Check", tags=["System Health"])
def health_check():
    """
    Production health check endpoint for Render and uptime monitoring.
    """
    return {"status": "ok"}


# Mount API v1
app.include_router(api_router)
