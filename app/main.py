# main.py

import os
from dotenv import load_dotenv
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.base import BaseHTTPMiddleware
import uvicorn
import uuid
import logging
from app.routes import messages  # Modular route imports
from app.utils.logger import configure_logger

# Load environment
load_dotenv()

# Configure logging
logger = configure_logger()

# Validate critical env vars
if not os.getenv("OPENAI_API_KEY"):
    raise EnvironmentError("OPENAI_API_KEY not set")

# Metadata
API_VERSION = "v1"
APP_VERSION = "0.1.0"

docs_url = f"/api/{API_VERSION}/docs"
openapi_url = f"/api/{API_VERSION}/openapi.json"

app = FastAPI(
    title="Triage Agent API",
    description="Agent-based system for classifying, drafting, and triaging inbound messages.",
    version=APP_VERSION,
    openapi_url=openapi_url,
    docs_url=docs_url
)

# ---------------- CORS ------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------- Request ID Middleware ---------------
class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request.state.request_id = str(uuid.uuid4())
        logger.info(f"[RequestID] {request.method} {request.url} | ID: {request.state.request_id}")
        response = await call_next(request)
        response.headers["X-Request-ID"] = request.state.request_id
        return response

app.add_middleware(RequestIDMiddleware)

# ----------------- Routes -------------------
app.include_router(messages.router, prefix=f"/api/{API_VERSION}/messages", tags=["Messages"])

# ----------------- Root Endpoint -------------------
@app.get("/", summary="API Root", description="Root endpoint for Triage Agent API. Use /docs to explore full schema.")
async def root():
    return {
        "service": "Triage Agent API",
        "status": "running",
        "version": APP_VERSION,
        "docs": docs_url,
        "openapi": openapi_url
    }

# ----------------- Health Check -------------------
@app.get("/health", summary="Health Check", description="Verify application is alive and ready.")
async def health():
    return {"status": "ok"}

# --------------- Global Exception Handling ----------------
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    logger.warning(f"[HTTPException] {exc.detail}")
    return JSONResponse(status_code=exc.status_code, content={"error": exc.detail})

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.warning(f"[ValidationError] {exc.errors()}")
    return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, content={"error": exc.errors()})

@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.error(f"[UnhandledError] {str(exc)}", exc_info=True)
    return JSONResponse(status_code=500, content={"error": "Internal server error"})

# ----------------- Entry Point --------------------
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True, log_level="info")
