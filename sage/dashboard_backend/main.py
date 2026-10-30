"""FastAPI Dashboard Backend Service for SAGE (Hardened Production Release)."""

from __future__ import annotations
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

from sage.dashboard_backend.api.audit import router as audit_router
from sage.dashboard_backend.api.cycles import router as cycles_router
from sage.dashboard_backend.api.leaderboard import router as leaderboard_router
from sage.dashboard_backend.api.runs import router as runs_router
from sage.dashboard_backend.api.trajectories import router as trajectories_router
from sage.dashboard_backend.api.redteam import router as redteam_router
from sage.dashboard_backend.api.telemetry import router as telemetry_router
from sage.dashboard_backend.db.models import init_db
from sage.dashboard_backend.ingest.watcher import RunWatcher
from sage_live.api.routes import (
    health_router,
    probe_router,
    eval_router,
    metrics_router,
    staleness_router,
    attestation_router,
    agent_router,
    websocket_evaluate,
    manager,
)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Enforce defense-in-depth HTTP security headers."""

    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "accelerometer=(), camera=(), geolocation=(), microphone=()"
        return response


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize SQLite database and sync runs
    init_db()
    watcher = RunWatcher()
    watcher.sync_all_runs()
    yield


app = FastAPI(
    title="SAGE Dashboard Backend",
    description="Evaluation and monitoring API for self-evolving agent safety drift and capability retention.",
    version="1.0.0",
    lifespan=lifespan,
)

# Hardened CORS policy: restrict to explicit origins in production
raw_origins = os.environ.get("ALLOWED_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000,http://localhost:3001,http://127.0.0.1:3001,*")
allowed_origins = [o.strip() for o in raw_origins.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if "*" in allowed_origins else allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    max_age=86400,
)

# Add security headers
app.add_middleware(SecurityHeadersMiddleware)

# Mount API routers (Static Benchmark + SAGE-Live Real-Time Dynamic Evaluation)
app.include_router(runs_router)
app.include_router(cycles_router)
app.include_router(trajectories_router)
app.include_router(audit_router)
app.include_router(leaderboard_router)
app.include_router(redteam_router)
app.include_router(telemetry_router)

@app.get("/health")
def health_check():
    """Liveness probe for container orchestrator."""
    return {"status": "ok", "service": "sage-dashboard-backend", "version": "1.0.0"}


# Mount SAGE-Live Dynamic Evaluation & Real-Time WebSocket Telemetry Endpoints
app.include_router(probe_router)
app.include_router(eval_router)
app.include_router(metrics_router)
app.include_router(staleness_router)
app.include_router(attestation_router)
app.include_router(agent_router)
app.include_router(health_router)
app.add_api_websocket_route("/ws/evaluate", websocket_evaluate)


@app.post("/admin/sync")
def sync_runs():
    """Re-scan experiments/runs/ and update the database without restarting the server.

    Call this after every `sage run` to make new results visible on the dashboard.
    Example: curl -X POST http://localhost:8000/admin/sync
    """
    watcher = RunWatcher()
    count = watcher.sync_all_runs()
    return {"status": "ok", "runs_synced": count, "message": f"Database refreshed: {count} run(s) synced."}
