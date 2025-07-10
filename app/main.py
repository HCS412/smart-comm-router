from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from decouple import config, UndefinedValueError
from app.utils.logger import logger
from app.routes import messages, webhook
import uuid
import os

# Application metadata
APP_NAME = "Smart Comm Router"
APP_VERSION = "1.1.0"
APP_DESCRIPTION = """
Smart Comm Router is an AI-powered system for auto-triaging and drafting responses to incoming messages.
It classifies messages by category, intent, priority, and queue, and generates tailored draft responses.
Supports mock ingestion from Gmail and phone sources for demonstration purposes.
"""

# Initialize FastAPI app
app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    description=APP_DESCRIPTION
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[config("REACT_APP_API_BASE_URL", default="http://localhost:8000")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Request ID middleware for traceability
@app.middleware("http")
async def add_request_id(request: Request, call_next):
    """Add a unique request ID to each request for logging."""
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    logger.info(f"[Request] New request | ID: {request_id} | Path: {request.url.path} | IP: {request.client.host}")
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response

# Validate environment variables at startup
def validate_environment():
    """Validate required environment variables."""
    required_vars = ["OPENAI_API_KEY"]
    missing_vars = []
    
    for var in required_vars:
        try:
            config(var)
        except UndefinedValueError:
            missing_vars.append(var)
    
    if missing_vars:
        error_msg = f"Missing required environment variables: {', '.join(missing_vars)}"
        logger.error(f"[Startup] {error_msg}")
        raise EnvironmentError(error_msg)
    
    # Log optional variables
    react_api_url = config("REACT_APP_API_BASE_URL", default="http://localhost:8000")
    logger.info(f"[Startup] REACT_APP_API_BASE_URL: {react_api_url}")

# Include routers
app.include_router(messages.router)
app.include_router(webhook.router)

# Health check endpoint
@app.get("/health", response_model=dict, status_code=status.HTTP_200_OK)
async def health_check():
    """
    Health check endpoint to verify the application's status.
    
    Returns:
        dict: Status information including app version and environment details.
    """
    try:
        return {
            "status": "healthy",
            "app_name": APP_NAME,
            "app_version": APP_VERSION,
            "openai_key_configured": bool(config("OPENAI_API_KEY", default=None)),
            "react_api_url": config("REACT_APP_API_BASE_URL", default="http://localhost:8000"),
            "timestamp": os.environ.get("CURRENT_TIME", "2025-07-10T13:03:00-04:00")
        }
    except Exception as e:
        logger.error(f"[HealthCheck] Failed: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"status": "unhealthy", "error": str(e)}
        )

# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize the application and validate environment."""
    logger.info(f"[Startup] Starting {APP_NAME} v{APP_VERSION}")
    validate_environment()
    logger.info("[Startup] Application initialized successfully")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Clean up resources on shutdown."""
    logger.info(f"[Shutdown] Stopping {APP_NAME} v{APP_VERSION}")
