"""
sage_live.api package.

Application factory that creates and configures the FastAPI application
instance, registers all routers, and installs global exception handlers.

Usage::

    from sage_live.api import create_app
    app = create_app()

Or run directly::

    uvicorn sage_live.api:app --reload
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger

from sage_live.api.routes import ALL_ROUTERS, ErrorResponse


def create_app() -> FastAPI:
    """Create and configure the SAGE-Live FastAPI application.

    Returns
    -------
    FastAPI
        Fully configured application instance.
    """
    application = FastAPI(
        title="SAGE-Live API",
        description=(
            "Self-Refreshing, Cryptographically Attested AI Safety Benchmark System. "
            "Provides endpoints for probe management, agent evaluation, staleness "
            "monitoring, and attestation chain verification."
        ),
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    # CORS
    application.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Restrict in production via env var
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Global unhandled exception handler
    @application.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        """Catch all unhandled exceptions and return a structured error response."""
        request_id = uuid.uuid4()
        logger.exception(
            "Unhandled exception [request_id={}] {} {}",
            request_id,
            request.method,
            request.url,
        )
        error = ErrorResponse(
            error="internal_server_error",
            detail=str(exc),
            request_id=request_id,
            timestamp=datetime.now(tz=timezone.utc),
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=error.model_dump(mode="json"),
        )

    # Register all routers
    for router in ALL_ROUTERS:
        application.include_router(router)

    logger.info("SAGE-Live FastAPI application created")
    return application


# Module-level app instance for uvicorn / gunicorn
app: FastAPI = create_app()

__all__: list[str] = ["app", "create_app"]
