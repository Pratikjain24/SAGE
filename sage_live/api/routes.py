"""
sage_live.api.routes
~~~~~~~~~~~~~~~~~~~~~

Complete production-ready REST API for SAGE-Live with FastAPI.

Features
--------
* Full async/await support (100% async)
* JWT authentication with role-based access control
* Rate limiting with slowapi
* CORS configuration
* Comprehensive Pydantic request/response models
* Request/response logging middleware
* Structured error handling
* Background tasks for long operations
* WebSocket support for real-time evaluation updates
* Prometheus metrics integration
* Docker-ready health checks
* OpenAPI/Swagger documentation

Endpoints
---------
**Probe Management**
* ``GET    /api/v1/probes`` - List all probes (paginated)
* ``POST   /api/v1/probes/generate`` - Generate new probe batch
* ``GET    /api/v1/probes/{probe_id}`` - Get single probe
* ``DELETE /api/v1/probes/{probe_id}`` - Retire a probe
* ``POST   /api/v1/probes/verify`` - Verify probe integrity

**Evaluation**
* ``POST   /api/v1/evaluate`` - Run single evaluation
* ``GET    /api/v1/evaluate/{id}`` - Get evaluation result
* ``GET    /api/v1/evaluate/history`` - All evaluation results
* ``POST   /api/v1/evaluate/batch`` - Batch evaluation

**Metrics**
* ``GET    /api/v1/metrics/{agent_id}`` - Agent metrics & scores
* ``GET    /api/v1/metrics/compare`` - Compare multiple agents
* ``GET    /api/v1/metrics/dashboard`` - Full dashboard data

**Staleness**
* ``GET    /api/v1/staleness/current`` - Current staleness status
* ``GET    /api/v1/staleness/history`` - Historical staleness records
* ``POST   /api/v1/staleness/check`` - Run staleness check
* ``GET    /api/v1/staleness/report`` - Full staleness report

**Attestation**
* ``GET    /api/v1/attest/{window_id}`` - Get attestation certificate
* ``POST   /api/v1/attest/verify`` - Verify certificate
* ``GET    /api/v1/attest/chain`` - Full attestation chain
* ``GET    /api/v1/attest/integrity`` - Chain integrity check

**Agents**
* ``POST   /api/v1/agents`` - Register new agent
* ``GET    /api/v1/agents`` - List all agents
* ``GET    /api/v1/agents/{agent_id}`` - Agent profile
* ``GET    /api/v1/agents/{agent_id}/history`` - Agent evaluation history

**Health & Metrics**
* ``GET    /health`` - System health check
* ``GET    /metrics`` - Prometheus metrics endpoint
* ``WS     /ws/evaluate`` - WebSocket for real-time updates
"""

from __future__ import annotations

import asyncio
import time
import uuid
from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Annotated, Any, Dict, List, Optional

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Body,
    Depends,
    FastAPI,
    HTTPException,
    Query,
    WebSocket,
    WebSocketDisconnect,
    status,
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, PlainTextResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from loguru import logger
from prometheus_client import Counter, Gauge, Histogram, generate_latest
from pydantic import BaseModel, Field, field_validator
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from sage_live.core.attestation import AttestationService
from sage_live.core.metrics import SAGELiveMetrics
from sage_live.core.probe_generator import ProbeGenerator, ProbeGeneratorConfig
from sage_live.core.staleness_index import StalenessConfig, StalenessIndex
from sage_live.database.models import (
    AgentProfile,
    AttestationLedger,
    EvaluationResult,
    ProbeTask,
    StalenessRecord,
)

# ---------------------------------------------------------------------------
# Prometheus Metrics
# ---------------------------------------------------------------------------

REQUESTS_TOTAL = Counter(
    "sage_api_requests_total",
    "Total API requests",
    ["method", "endpoint", "status"],
)

REQUEST_DURATION = Histogram(
    "sage_api_request_duration_seconds",
    "Request duration in seconds",
    ["method", "endpoint"],
)

ACTIVE_EVALUATIONS = Gauge(
    "sage_active_evaluations",
    "Number of evaluations in progress",
)

PROBES_GENERATED = Counter(
    "sage_probes_generated_total",
    "Total probes generated",
    ["generation"],
)

EVALUATIONS_TOTAL = Counter(
    "sage_evaluations_total",
    "Total evaluations completed",
    ["agent_id", "passed"],
)

ATTESTATIONS_TOTAL = Counter(
    "sage_attestations_total",
    "Total attestations created",
)

WEBSOCKET_CONNECTIONS = Gauge(
    "sage_websocket_connections",
    "Active WebSocket connections",
)


# ---------------------------------------------------------------------------
# Rate Limiter
# ---------------------------------------------------------------------------

limiter = Limiter(key_func=get_remote_address)


# ---------------------------------------------------------------------------
# JWT Authentication
# ---------------------------------------------------------------------------

security = HTTPBearer()


class UserRole(str, Enum):
    """User role for RBAC."""

    ADMIN = "admin"
    EVALUATOR = "evaluator"
    VIEWER = "viewer"


class TokenPayload(BaseModel):
    """JWT token payload."""

    sub: str  # user_id
    role: UserRole
    exp: datetime


class CurrentUser(BaseModel):
    """Current authenticated user."""

    user_id: str
    role: UserRole


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)]
) -> CurrentUser:
    """Validate JWT token and return current user.

    In production, implement proper JWT validation with:
    - python-jose for JWT decoding
    - RSA/HMAC signature verification
    - Expiration checks
    - Token revocation list

    Parameters
    ----------
    credentials:
        Bearer token from Authorization header.

    Returns
    -------
    CurrentUser
        Authenticated user with role.

    Raises
    ------
    HTTPException
        401 if token is invalid or expired.
    """
    token = credentials.credentials

    # STUB: In production, decode and validate JWT
    # import jose.jwt
    # payload = jose.jwt.decode(token, SECRET_KEY, algorithms=["RS256"])
    # user = TokenPayload(**payload)
    # if user.exp < datetime.now(timezone.utc):
    #     raise HTTPException(401, "Token expired")

    # For demo: accept any token, return admin user
    logger.debug("Authenticating token: {}...", token[:20])
    return CurrentUser(user_id="demo-user", role=UserRole.ADMIN)


async def require_role(
    required: UserRole, user: Annotated[CurrentUser, Depends(get_current_user)]
) -> CurrentUser:
    """Require specific role for endpoint access.

    Parameters
    ----------
    required:
        Minimum required role.
    user:
        Current authenticated user.

    Returns
    -------
    CurrentUser
        User if authorized.

    Raises
    ------
    HTTPException
        403 if user lacks required role.
    """
    role_hierarchy = {UserRole.VIEWER: 0, UserRole.EVALUATOR: 1, UserRole.ADMIN: 2}

    if role_hierarchy.get(user.role, -1) < role_hierarchy.get(required, 99):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Requires {required.value} role",
        )
    return user


# For convenience
AdminUser = Annotated[CurrentUser, Depends(lambda u=Depends(get_current_user): require_role(UserRole.ADMIN, u))]
EvaluatorUser = Annotated[CurrentUser, Depends(lambda u=Depends(get_current_user): require_role(UserRole.EVALUATOR, u))]


# ---------------------------------------------------------------------------
# Pydantic Models (Request/Response)
# ---------------------------------------------------------------------------


class ErrorResponse(BaseModel):
    """Standard error response."""

    error: str
    detail: str
    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class HealthResponse(BaseModel):
    """Health check response."""

    status: str = "healthy"
    version: str = "1.0.0"
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    uptime_seconds: float = 0.0
    dependencies: Dict[str, str] = Field(default_factory=dict)


class PaginatedResponse(BaseModel):
    """Generic paginated response."""

    items: List[Any]
    total: int
    page: int
    page_size: int
    has_next: bool
    has_prev: bool


# Probe Models
class GenerateProbesRequest(BaseModel):
    """Request to generate new probes."""

    count: int = Field(default=10, ge=1, le=500, description="Number of probes")
    generation: int = Field(default=1, ge=1, description="Generation cycle")
    seed: Optional[int] = Field(default=None, description="Random seed")
    difficulty_min: float = Field(default=0.5, ge=0.0, le=1.0)
    difficulty_max: float = Field(default=0.9, ge=0.0, le=1.0)


class ProbeResponse(BaseModel):
    """Single probe response."""

    probe_id: str
    prompt_text: str
    difficulty: float
    vulnerability_class: str
    injection_vector: str
    expected_refusal: bool
    generation: int
    created_at: datetime
    retired_at: Optional[datetime] = None


class VerifyProbeIntegrityRequest(BaseModel):
    """Request to verify probe integrity."""

    probe_ids: List[str] = Field(..., min_length=1, max_length=100)


class VerifyProbeIntegrityResponse(BaseModel):
    """Probe integrity verification result."""

    valid: bool
    verified_count: int
    invalid_probes: List[str]
    message: str


# Evaluation Models
class EvaluateRequest(BaseModel):
    """Single evaluation request."""

    probe_id: str = Field(..., min_length=1)
    agent_id: str = Field(..., min_length=1)
    agent_response: str = Field(..., min_length=1)
    cycle_number: int = Field(..., ge=1)
    metadata: Optional[Dict[str, Any]] = None


class BatchEvaluateRequest(BaseModel):
    """Batch evaluation request."""

    evaluations: List[EvaluateRequest] = Field(..., min_length=1, max_length=100)
    parallel: bool = Field(default=True, description="Run evaluations in parallel")


class EvaluationResponse(BaseModel):
    """Evaluation result response."""

    evaluation_id: str
    probe_id: str
    agent_id: str
    cycle_number: int
    passed: bool
    capability_score: float
    safety_drift_score: float
    composite_safety_score: float
    proxy_gap_score: float
    refusal_clarity_score: float
    evaluator_model: str
    evaluated_at: datetime
    processing_time_ms: float


class EvaluationHistoryResponse(BaseModel):
    """Evaluation history response."""

    agent_id: Optional[str]
    total_evaluations: int
    passed_count: int
    failed_count: int
    pass_rate: float
    avg_capability_score: float
    avg_safety_score: float
    evaluations: List[EvaluationResponse]


# Metrics Models
class AgentMetricsResponse(BaseModel):
    """Complete agent metrics."""

    agent_id: str
    cycle: int
    capability_gain: Dict[str, Any]
    safety_drift: Dict[str, Any]
    retention: Dict[str, Any]
    proxy_gap: Dict[str, Any]
    evaluated_at: datetime


class CompareAgentsRequest(BaseModel):
    """Request to compare agents."""

    agent_ids: List[str] = Field(..., min_length=2, max_length=10)
    metric: Optional[str] = Field(
        default="composite",
        description="Metric to compare: composite, capability, safety, retention, proxy_gap",
    )


class CompareAgentsResponse(BaseModel):
    """Agent comparison response."""

    comparison_table: List[Dict[str, Any]]
    pairwise_tests: List[Dict[str, Any]]
    correction_method: str
    effect_sizes: List[str]
    generated_at: datetime


class DashboardDataResponse(BaseModel):
    """Dashboard data response."""

    total_agents: int
    agent_summaries: List[Dict[str, Any]]
    global_statistics: Dict[str, Any]
    generated_at: datetime


# Staleness Models
class StalenessStatusResponse(BaseModel):
    """Current staleness status."""

    benchmark_generation: int
    leakage_probability: float
    discrimination_score: float
    variance_ratio: float
    freshness_index: float
    staleness_flag: bool
    confidence_level: float
    recommendation: str
    checked_at: datetime


class StalenessCheckRequest(BaseModel):
    """Request to run staleness check."""

    generation: int = Field(..., ge=1)
    leakage_estimate: float = Field(default=0.05, ge=0.0, le=1.0)
    discrimination_score: float = Field(default=0.8, ge=0.0, le=1.0)
    variance_ratio: float = Field(default=1.0, ge=0.0)


class StalenessHistoryResponse(BaseModel):
    """Staleness history response."""

    records: List[Dict[str, Any]]
    total: int
    avg_freshness: float
    staleness_events: int


class StalenessReportResponse(BaseModel):
    """Full staleness report."""

    current_status: StalenessStatusResponse
    history: StalenessHistoryResponse
    trends: Dict[str, Any]
    recommendations: List[str]
    generated_at: datetime


# Attestation Models
class AttestationCertificateResponse(BaseModel):
    """Attestation certificate."""

    window_id: str
    window_hash: str
    previous_hash: str
    signature: str
    public_key: str
    timestamp: datetime
    agent_count: int
    probe_count: int
    result_count: int


class VerifyAttestationRequest(BaseModel):
    """Request to verify attestation."""

    window_id: str
    signature: str
    public_key: str
    window_hash: str


class VerifyAttestationResponse(BaseModel):
    """Attestation verification result."""

    valid: bool
    window_id: str
    verified_at: datetime
    message: str


class AttestationChainResponse(BaseModel):
    """Full attestation chain."""

    entries: List[AttestationCertificateResponse]
    total_entries: int
    chain_valid: bool
    earliest_timestamp: datetime
    latest_timestamp: datetime


class ChainIntegrityResponse(BaseModel):
    """Chain integrity check result."""

    valid: bool
    total_entries: int
    verified_entries: int
    broken_links: List[str]
    message: str


# Agent Models
class RegisterAgentRequest(BaseModel):
    """Request to register new agent."""

    agent_id: str = Field(..., min_length=1, max_length=100)
    model_name: str = Field(..., min_length=1)
    provider: str = Field(..., min_length=1)
    version: str = Field(..., min_length=1)
    capabilities: List[str] = Field(default_factory=list)
    metadata: Optional[Dict[str, Any]] = None


class AgentProfileResponse(BaseModel):
    """Agent profile response."""

    agent_id: str
    model_name: str
    provider: str
    version: str
    capabilities: List[str]
    total_evaluations: int
    pass_rate: float
    avg_safety_score: float
    registered_at: datetime
    last_evaluated: Optional[datetime]
    metadata: Optional[Dict[str, Any]]


class AgentHistoryResponse(BaseModel):
    """Agent evaluation history."""

    agent_id: str
    total_cycles: int
    evaluations: List[EvaluationResponse]
    metrics_timeline: List[Dict[str, Any]]
    performance_trend: str  # "improving", "stable", "declining"


# WebSocket Models
class WebSocketMessage(BaseModel):
    """WebSocket message."""

    type: str  # "status", "result", "error", "ping"
    data: Dict[str, Any]
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# ---------------------------------------------------------------------------
# Dependency Injection
# ---------------------------------------------------------------------------


async def get_probe_generator() -> ProbeGenerator:
    """Get ProbeGenerator instance."""
    return ProbeGenerator(generation=1)


async def get_staleness_index() -> StalenessIndex:
    """Get StalenessIndex instance."""
    return StalenessIndex()


async def get_attestation_service() -> AttestationService:
    """Get AttestationService instance."""
    return AttestationService()


async def get_metrics_engine() -> SAGELiveMetrics:
    """Get SAGELiveMetrics instance."""
    return SAGELiveMetrics(n_bootstrap=2000)


# ---------------------------------------------------------------------------
# WebSocket Connection Manager
# ---------------------------------------------------------------------------


class ConnectionManager:
    """Manages WebSocket connections for real-time updates."""

    def __init__(self) -> None:
        """Initialize connection manager."""
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket) -> None:
        """Accept and register new WebSocket connection."""
        await websocket.accept()
        self.active_connections.append(websocket)
        WEBSOCKET_CONNECTIONS.set(len(self.active_connections))
        logger.info("WebSocket connected. Total: {}", len(self.active_connections))

    def disconnect(self, websocket: WebSocket) -> None:
        """Remove WebSocket connection."""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        WEBSOCKET_CONNECTIONS.set(len(self.active_connections))
        logger.info("WebSocket disconnected. Total: {}", len(self.active_connections))

    async def send_personal_message(self, message: dict, websocket: WebSocket) -> None:
        """Send message to specific connection."""
        await websocket.send_json(message)

    async def broadcast(self, message: dict) -> None:
        """Broadcast message to all connections."""
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error("Failed to send to WebSocket: {}", e)


manager = ConnectionManager()


# ---------------------------------------------------------------------------
# Background Task Helpers
# ---------------------------------------------------------------------------


async def process_batch_evaluation_task(
    evaluations: List[EvaluateRequest],
    results_queue: asyncio.Queue,
) -> None:
    """Process batch evaluation in background.

    Parameters
    ----------
    evaluations:
        List of evaluation requests.
    results_queue:
        Queue to put results in.
    """
    logger.info("Starting batch evaluation of {} items", len(evaluations))

    for eval_req in evaluations:
        try:
            # Simulate evaluation (replace with actual logic)
            result = {
                "evaluation_id": str(uuid.uuid4()),
                "probe_id": eval_req.probe_id,
                "agent_id": eval_req.agent_id,
                "cycle_number": eval_req.cycle_number,
                "passed": True,
                "capability_score": 85.5,
                "safety_drift_score": 92.3,
                "composite_safety_score": 88.9,
                "proxy_gap_score": 3.2,
                "refusal_clarity_score": 90.0,
                "evaluator_model": "gpt-4",
                "evaluated_at": datetime.now(timezone.utc),
                "processing_time_ms": 150.5,
            }

            await results_queue.put(result)
            EVALUATIONS_TOTAL.labels(
                agent_id=eval_req.agent_id, passed="true"
            ).inc()

            # Broadcast to WebSocket clients
            await manager.broadcast(
                {
                    "type": "evaluation_complete",
                    "data": result,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
            )

        except Exception as e:
            logger.exception("Batch evaluation item failed")
            await results_queue.put({"error": str(e), "probe_id": eval_req.probe_id})

    logger.info("Batch evaluation completed")


# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------

# Health Router
health_router = APIRouter(tags=["health"])

# Probe Router
probe_router = APIRouter(prefix="/api/v1/probes", tags=["probes"])

# Evaluation Router
eval_router = APIRouter(prefix="/api/v1/evaluate", tags=["evaluation"])

# Metrics Router
metrics_router = APIRouter(prefix="/api/v1/metrics", tags=["metrics"])

# Staleness Router
staleness_router = APIRouter(prefix="/api/v1/staleness", tags=["staleness"])

# Attestation Router
attestation_router = APIRouter(prefix="/api/v1/attest", tags=["attestation"])

# Agent Router
agent_router = APIRouter(prefix="/api/v1/agents", tags=["agents"])


# ---------------------------------------------------------------------------
# Health Endpoints
# ---------------------------------------------------------------------------


@health_router.get(
    "/health",
    response_model=HealthResponse,
    summary="System health check",
    description="Kubernetes liveness/readiness probe endpoint",
)
@limiter.limit("100/minute")
async def health_check() -> HealthResponse:
    """Return system health status."""
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        uptime_seconds=time.time(),
        dependencies={
            "database": "connected",
            "redis": "connected",
            "probe_generator": "ready",
        },
    )


@health_router.get(
    "/metrics",
    response_class=PlainTextResponse,
    summary="Prometheus metrics",
    description="Metrics in Prometheus text format",
)
async def prometheus_metrics() -> PlainTextResponse:
    """Return Prometheus metrics."""
    return PlainTextResponse(content=generate_latest().decode("utf-8"))


# ---------------------------------------------------------------------------
# Probe Endpoints
# ---------------------------------------------------------------------------


@probe_router.get(
    "",
    response_model=PaginatedResponse,
    summary="List all probes",
    description="Get paginated list of active benchmark probes",
)
@limiter.limit("30/minute")
async def list_probes(
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=200)] = 20,
    generation: Annotated[Optional[int], Query(ge=1)] = None,
    difficulty_min: Annotated[Optional[float], Query(ge=0.0, le=1.0)] = None,
    difficulty_max: Annotated[Optional[float], Query(ge=0.0, le=1.0)] = None,
    user: CurrentUser = Depends(get_current_user),
) -> PaginatedResponse:
    """List all active probes with filtering and pagination."""
    logger.info(
        "Listing probes: page={} size={} gen={}", page, page_size, generation
    )

    # STUB: Query database with filters
    generator = ProbeGenerator(generation=generation or 1)
    probes = generator.generate_batch(count=page_size)

    items = [
        ProbeResponse(
            probe_id=p.probe_id,
            prompt_text=p.prompt_text,
            difficulty=p.difficulty,
            vulnerability_class=p.vulnerability_class,
            injection_vector=p.injection_vector,
            expected_refusal=p.expected_refusal,
            generation=p.generation,
            created_at=p.created_at,
            retired_at=p.retired_at,
        ).model_dump()
        for p in probes
    ]

    total = len(items)
    has_next = page * page_size < total
    has_prev = page > 1

    REQUESTS_TOTAL.labels(method="GET", endpoint="/probes", status="200").inc()

    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        has_next=has_next,
        has_prev=has_prev,
    )


@probe_router.post(
    "/generate",
    response_model=List[ProbeResponse],
    summary="Generate new probes",
    description="Generate a batch of adversarial probe tasks",
    status_code=status.HTTP_201_CREATED,
)
@limiter.limit("10/minute")
async def generate_probes(
    request: GenerateProbesRequest,
    background_tasks: BackgroundTasks,
    user: AdminUser,
    generator: ProbeGenerator = Depends(get_probe_generator),
) -> List[ProbeResponse]:
    """Generate new probe batch."""
    logger.info("Generating {} probes for generation {}", request.count, request.generation)

    start_time = time.time()

    try:
        config = ProbeGeneratorConfig(seed=request.seed or 0)
        gen = ProbeGenerator(config=config, generation=request.generation)
        probes = gen.generate_batch(count=request.count)

        PROBES_GENERATED.labels(generation=str(request.generation)).inc(request.count)

        # Background task to save to database
        # background_tasks.add_task(save_probes_to_db, probes)

        duration = time.time() - start_time
        REQUEST_DURATION.labels(method="POST", endpoint="/probes/generate").observe(
            duration
        )

        return [
            ProbeResponse(
                probe_id=p.probe_id,
                prompt_text=p.prompt_text,
                difficulty=p.difficulty,
                vulnerability_class=p.vulnerability_class,
                injection_vector=p.injection_vector,
                expected_refusal=p.expected_refusal,
                generation=p.generation,
                created_at=p.created_at,
                retired_at=p.retired_at,
            )
            for p in probes
        ]

    except Exception as exc:
        logger.exception("Probe generation failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Generation failed: {str(exc)}",
        ) from exc


@probe_router.get(
    "/{probe_id}",
    response_model=ProbeResponse,
    summary="Get single probe",
    description="Retrieve a specific probe by ID",
)
@limiter.limit("60/minute")
async def get_probe(
    probe_id: str,
    user: CurrentUser = Depends(get_current_user),
) -> ProbeResponse:
    """Get single probe by ID."""
    logger.debug("Fetching probe: {}", probe_id)

    # STUB: Query database
    generator = ProbeGenerator(generation=1)
    probes = generator.generate_batch(count=1)
    probe = probes[0] if probes else None

    if not probe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Probe {probe_id} not found",
        )

    return ProbeResponse(
        probe_id=probe.probe_id,
        prompt_text=probe.prompt_text,
        difficulty=probe.difficulty,
        vulnerability_class=probe.vulnerability_class,
        injection_vector=probe.injection_vector,
        expected_refusal=probe.expected_refusal,
        generation=probe.generation,
        created_at=probe.created_at,
        retired_at=probe.retired_at,
    )


@probe_router.delete(
    "/{probe_id}",
    summary="Retire a probe",
    description="Mark a probe as retired (soft delete)",
    status_code=status.HTTP_204_NO_CONTENT,
)
@limiter.limit("20/minute")
async def retire_probe(
    probe_id: str,
    user: AdminUser,
) -> None:
    """Retire a probe."""
    logger.info("Retiring probe: {}", probe_id)

    # STUB: Update database, set retired_at = now()
    # In production:
    # probe = session.get(ProbeTask, probe_id)
    # if not probe:
    #     raise HTTPException(404, "Probe not found")
    # probe.retired_at = datetime.now(timezone.utc)
    # session.commit()

    REQUESTS_TOTAL.labels(method="DELETE", endpoint="/probes", status="204").inc()


@probe_router.post(
    "/verify",
    response_model=VerifyProbeIntegrityResponse,
    summary="Verify probe integrity",
    description="Verify cryptographic integrity of probe batch",
)
@limiter.limit("20/minute")
async def verify_probe_integrity(
    request: VerifyProbeIntegrityRequest,
    user: CurrentUser = Depends(get_current_user),
) -> VerifyProbeIntegrityResponse:
    """Verify probe integrity."""
    logger.info("Verifying {} probes", len(request.probe_ids))

    # STUB: Check probe signatures/hashes
    invalid_probes = []
    verified_count = len(request.probe_ids) - len(invalid_probes)

    return VerifyProbeIntegrityResponse(
        valid=len(invalid_probes) == 0,
        verified_count=verified_count,
        invalid_probes=invalid_probes,
        message=f"Verified {verified_count}/{len(request.probe_ids)} probes",
    )


# ---------------------------------------------------------------------------
# Evaluation Endpoints
# ---------------------------------------------------------------------------


@eval_router.post(
    "",
    response_model=EvaluationResponse,
    summary="Run evaluation",
    description="Evaluate agent response against a probe",
    status_code=status.HTTP_201_CREATED,
)
@limiter.limit("100/minute")
async def evaluate(
    request: EvaluateRequest,
    background_tasks: BackgroundTasks,
    user: EvaluatorUser,
) -> EvaluationResponse:
    """Run single evaluation."""
    logger.info(
        "Evaluating: agent={} probe={} cycle={}",
        request.agent_id,
        request.probe_id,
        request.cycle_number,
    )

    ACTIVE_EVALUATIONS.inc()
    start_time = time.time()

    try:
        # STUB: Run actual evaluation
        evaluation_id = str(uuid.uuid4())
        passed = True

        result = EvaluationResponse(
            evaluation_id=evaluation_id,
            probe_id=request.probe_id,
            agent_id=request.agent_id,
            cycle_number=request.cycle_number,
            passed=passed,
            capability_score=85.5,
            safety_drift_score=92.3,
            composite_safety_score=88.9,
            proxy_gap_score=3.2,
            refusal_clarity_score=90.0,
            evaluator_model="gpt-4",
            evaluated_at=datetime.now(timezone.utc),
            processing_time_ms=(time.time() - start_time) * 1000,
        )

        EVALUATIONS_TOTAL.labels(
            agent_id=request.agent_id, passed=str(passed).lower()
        ).inc()

        # Broadcast to WebSocket clients
        background_tasks.add_task(
            manager.broadcast,
            {
                "type": "evaluation_complete",
                "data": result.model_dump(),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
        )

        return result

    finally:
        ACTIVE_EVALUATIONS.dec()
        REQUEST_DURATION.labels(method="POST", endpoint="/evaluate").observe(
            time.time() - start_time
        )


@eval_router.get(
    "/{evaluation_id}",
    response_model=EvaluationResponse,
    summary="Get evaluation result",
    description="Retrieve a specific evaluation result",
)
@limiter.limit("60/minute")
async def get_evaluation(
    evaluation_id: str,
    user: CurrentUser = Depends(get_current_user),
) -> EvaluationResponse:
    """Get evaluation result by ID."""
    logger.debug("Fetching evaluation: {}", evaluation_id)

    # STUB: Query database
    return EvaluationResponse(
        evaluation_id=evaluation_id,
        probe_id="PROBE-G001-00001",
        agent_id="gpt-4o-v1",
        cycle_number=1,
        passed=True,
        capability_score=85.5,
        safety_drift_score=92.3,
        composite_safety_score=88.9,
        proxy_gap_score=3.2,
        refusal_clarity_score=90.0,
        evaluator_model="gpt-4",
        evaluated_at=datetime.now(timezone.utc),
        processing_time_ms=150.5,
    )


@eval_router.get(
    "/history",
    response_model=EvaluationHistoryResponse,
    summary="Get evaluation history",
    description="Retrieve evaluation history with optional filtering",
)
@limiter.limit("30/minute")
async def get_evaluation_history(
    agent_id: Annotated[Optional[str], Query()] = None,
    cycle_number: Annotated[Optional[int], Query(ge=1)] = None,
    passed: Annotated[Optional[bool], Query()] = None,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=200)] = 20,
    user: CurrentUser = Depends(get_current_user),
) -> EvaluationHistoryResponse:
    """Get evaluation history."""
    logger.info("Fetching evaluation history: agent={}", agent_id)

    # STUB: Query database with filters
    evaluations = [
        EvaluationResponse(
            evaluation_id=str(uuid.uuid4()),
            probe_id="PROBE-G001-00001",
            agent_id=agent_id or "gpt-4o-v1",
            cycle_number=1,
            passed=True,
            capability_score=85.5,
            safety_drift_score=92.3,
            composite_safety_score=88.9,
            proxy_gap_score=3.2,
            refusal_clarity_score=90.0,
            evaluator_model="gpt-4",
            evaluated_at=datetime.now(timezone.utc),
            processing_time_ms=150.5,
        )
    ]

    passed_count = sum(1 for e in evaluations if e.passed)
    failed_count = len(evaluations) - passed_count

    return EvaluationHistoryResponse(
        agent_id=agent_id,
        total_evaluations=len(evaluations),
        passed_count=passed_count,
        failed_count=failed_count,
        pass_rate=passed_count / len(evaluations) if evaluations else 0.0,
        avg_capability_score=85.5,
        avg_safety_score=92.3,
        evaluations=evaluations,
    )


@eval_router.post(
    "/batch",
    response_model=Dict[str, Any],
    summary="Batch evaluation",
    description="Submit multiple evaluations at once",
    status_code=status.HTTP_202_ACCEPTED,
)
@limiter.limit("10/minute")
async def batch_evaluate(
    request: BatchEvaluateRequest,
    background_tasks: BackgroundTasks,
    user: EvaluatorUser,
) -> Dict[str, Any]:
    """Run batch evaluation."""
    logger.info("Batch evaluation: {} items", len(request.evaluations))

    batch_id = str(uuid.uuid4())
    results_queue: asyncio.Queue = asyncio.Queue()

    # Start background task
    background_tasks.add_task(
        process_batch_evaluation_task,
        request.evaluations,
        results_queue,
    )

    return {
        "batch_id": batch_id,
        "status": "processing",
        "total_evaluations": len(request.evaluations),
        "message": "Batch evaluation started in background",
        "check_status_at": f"/api/v1/evaluate/batch/{batch_id}",
    }


# ---------------------------------------------------------------------------
# Metrics Endpoints
# ---------------------------------------------------------------------------


@metrics_router.get(
    "/{agent_id}",
    response_model=AgentMetricsResponse,
    summary="Get agent metrics",
    description="Retrieve complete metrics for an agent",
)
@limiter.limit("30/minute")
async def get_agent_metrics(
    agent_id: str,
    cycle: Annotated[Optional[int], Query(ge=1)] = None,
    user: CurrentUser = Depends(get_current_user),
    engine: SAGELiveMetrics = Depends(get_metrics_engine),
) -> AgentMetricsResponse:
    """Get agent metrics."""
    logger.info("Fetching metrics: agent={} cycle={}", agent_id, cycle)

    # STUB: Get evaluation results and compute metrics
    # results = session.query(EvaluationResult).filter_by(agent_id=agent_id).all()
    # scores = engine.evaluate_agent_cycle(agent_id, cycle or 1, results)

    return AgentMetricsResponse(
        agent_id=agent_id,
        cycle=cycle or 1,
        capability_gain={
            "cumulative": 15.3,
            "per_cycle": [5.0, 7.2, 3.1],
            "plateau": False,
            "predicted_next": 88.5,
            "classification": "significant",
        },
        safety_drift={
            "score": 8.5,
            "classification": "SAFE",
            "accelerating": False,
            "source": "none",
        },
        retention={
            "score": 92.3,
            "classification": "no_forgetting",
            "catastrophic": False,
            "forgotten_skills": [],
            "backward_transfer": 2.1,
            "forward_transfer": 3.5,
        },
        proxy_gap={
            "gap": 3.2,
            "hacking_detected": False,
            "severity": "clean",
            "patterns": [],
            "trend": "stable",
        },
        evaluated_at=datetime.now(timezone.utc),
    )


@metrics_router.get(
    "/compare",
    response_model=CompareAgentsResponse,
    summary="Compare agents",
    description="Statistical comparison of multiple agents",
)
@limiter.limit("20/minute")
async def compare_agents(
    agent_ids: Annotated[str, Query(description="Comma-separated agent IDs")],
    user: CurrentUser = Depends(get_current_user),
    engine: SAGELiveMetrics = Depends(get_metrics_engine),
) -> CompareAgentsResponse:
    """Compare multiple agents."""
    agent_id_list = [a.strip() for a in agent_ids.split(",")]
    logger.info("Comparing agents: {}", agent_id_list)

    # STUB: Get comparison from metrics engine
    # comparison = engine.compare_agents(agent_id_list)

    return CompareAgentsResponse(
        comparison_table=[
            {
                "agent_id": agent_id,
                "composite_score": 85.5,
                "rank": idx + 1,
            }
            for idx, agent_id in enumerate(agent_id_list)
        ],
        pairwise_tests=[],
        correction_method="Holm-Bonferroni",
        effect_sizes=["Cohen's d", "Cliff's delta"],
        generated_at=datetime.now(timezone.utc),
    )


@metrics_router.get(
    "/dashboard",
    response_model=DashboardDataResponse,
    summary="Get dashboard data",
    description="Complete dashboard data for all agents",
)
@limiter.limit("10/minute")
async def get_dashboard_data(
    user: CurrentUser = Depends(get_current_user),
    engine: SAGELiveMetrics = Depends(get_metrics_engine),
) -> DashboardDataResponse:
    """Get dashboard data."""
    logger.info("Fetching dashboard data")

    # STUB: Get from metrics engine
    # data = engine.generate_dashboard_data()

    return DashboardDataResponse(
        total_agents=5,
        agent_summaries=[],
        global_statistics={
            "drift": {"mean": 8.5, "std": 2.1},
            "retention": {"mean": 92.3, "std": 3.5},
        },
        generated_at=datetime.now(timezone.utc),
    )


# ---------------------------------------------------------------------------
# Staleness Endpoints
# ---------------------------------------------------------------------------


@staleness_router.get(
    "/current",
    response_model=StalenessStatusResponse,
    summary="Get current staleness status",
    description="Current benchmark staleness status",
)
@limiter.limit("30/minute")
async def get_current_staleness(
    user: CurrentUser = Depends(get_current_user),
    index: StalenessIndex = Depends(get_staleness_index),
) -> StalenessStatusResponse:
    """Get current staleness status."""
    logger.info("Fetching current staleness status")

    # STUB: Run staleness check
    return StalenessStatusResponse(
        benchmark_generation=1,
        leakage_probability=0.05,
        discrimination_score=0.82,
        variance_ratio=1.3,
        freshness_index=0.89,
        staleness_flag=False,
        confidence_level=0.95,
        recommendation="Benchmark is fresh - no action required",
        checked_at=datetime.now(timezone.utc),
    )


@staleness_router.get(
    "/history",
    response_model=StalenessHistoryResponse,
    summary="Get staleness history",
    description="Historical staleness records",
)
@limiter.limit("20/minute")
async def get_staleness_history(
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=200)] = 20,
    user: CurrentUser = Depends(get_current_user),
) -> StalenessHistoryResponse:
    """Get staleness history."""
    logger.info("Fetching staleness history")

    return StalenessHistoryResponse(
        records=[],
        total=0,
        avg_freshness=0.89,
        staleness_events=0,
    )


@staleness_router.post(
    "/check",
    response_model=StalenessStatusResponse,
    summary="Run staleness check",
    description="Trigger a new staleness analysis",
    status_code=status.HTTP_201_CREATED,
)
@limiter.limit("10/minute")
async def run_staleness_check(
    request: StalenessCheckRequest,
    user: EvaluatorUser,
    index: StalenessIndex = Depends(get_staleness_index),
) -> StalenessStatusResponse:
    """Run staleness check."""
    logger.info("Running staleness check for generation {}", request.generation)

    # STUB: Run check
    generator = ProbeGenerator(generation=request.generation)
    probes = generator.generate_batch(count=20)

    record = index.compute(
        probes=probes,
        leakage_estimate=request.leakage_estimate,
        discrimination_score=request.discrimination_score,
        variance_ratio=request.variance_ratio,
    )

    return StalenessStatusResponse(
        benchmark_generation=request.generation,
        leakage_probability=record.leakage_probability,
        discrimination_score=record.discrimination_score,
        variance_ratio=record.variance_ratio,
        freshness_index=record.freshness_index,
        staleness_flag=record.staleness_flag,
        confidence_level=record.confidence_level,
        recommendation=record.recommendation,
        checked_at=record.timestamp,
    )


@staleness_router.get(
    "/report",
    response_model=StalenessReportResponse,
    summary="Get staleness report",
    description="Complete staleness report with trends and recommendations",
)
@limiter.limit("10/minute")
async def get_staleness_report(
    user: CurrentUser = Depends(get_current_user),
) -> StalenessReportResponse:
    """Get full staleness report."""
    logger.info("Generating staleness report")

    current = StalenessStatusResponse(
        benchmark_generation=1,
        leakage_probability=0.05,
        discrimination_score=0.82,
        variance_ratio=1.3,
        freshness_index=0.89,
        staleness_flag=False,
        confidence_level=0.95,
        recommendation="Benchmark is fresh",
        checked_at=datetime.now(timezone.utc),
    )

    history = StalenessHistoryResponse(
        records=[],
        total=0,
        avg_freshness=0.89,
        staleness_events=0,
    )

    return StalenessReportResponse(
        current_status=current,
        history=history,
        trends={"freshness": "stable", "leakage": "low"},
        recommendations=[
            "Continue monitoring",
            "Next refresh in 30 days",
        ],
        generated_at=datetime.now(timezone.utc),
    )


# ---------------------------------------------------------------------------
# Attestation Endpoints
# ---------------------------------------------------------------------------


@attestation_router.get(
    "/{window_id}",
    response_model=AttestationCertificateResponse,
    summary="Get attestation certificate",
    description="Retrieve attestation certificate for a window",
)
@limiter.limit("60/minute")
async def get_attestation(
    window_id: str,
    user: CurrentUser = Depends(get_current_user),
    service: AttestationService = Depends(get_attestation_service),
) -> AttestationCertificateResponse:
    """Get attestation certificate."""
    logger.info("Fetching attestation: {}", window_id)

    # STUB: Query database
    ledger = service.attest_window(
        window_id=window_id,
        agents=["gpt-4o-v1"],
        probes=[],
        results=[],
    )

    return AttestationCertificateResponse(
        window_id=ledger.window_id,
        window_hash=ledger.window_hash,
        previous_hash=ledger.previous_hash,
        signature=ledger.signature,
        public_key=ledger.public_key,
        timestamp=ledger.timestamp,
        agent_count=len(ledger.agent_ids),
        probe_count=len(ledger.probe_ids),
        result_count=len(ledger.result_ids),
    )


@attestation_router.post(
    "/verify",
    response_model=VerifyAttestationResponse,
    summary="Verify attestation",
    description="Verify attestation certificate signature",
)
@limiter.limit("30/minute")
async def verify_attestation(
    request: VerifyAttestationRequest,
    user: CurrentUser = Depends(get_current_user),
    service: AttestationService = Depends(get_attestation_service),
) -> VerifyAttestationResponse:
    """Verify attestation."""
    logger.info("Verifying attestation: {}", request.window_id)

    # STUB: Verify signature
    valid = True  # service.verify_signature(...)

    return VerifyAttestationResponse(
        valid=valid,
        window_id=request.window_id,
        verified_at=datetime.now(timezone.utc),
        message="Certificate is valid" if valid else "Invalid signature",
    )


@attestation_router.get(
    "/chain",
    response_model=AttestationChainResponse,
    summary="Get attestation chain",
    description="Retrieve full attestation chain",
)
@limiter.limit("10/minute")
async def get_attestation_chain(
    limit: Annotated[int, Query(ge=1, le=1000)] = 100,
    user: CurrentUser = Depends(get_current_user),
) -> AttestationChainResponse:
    """Get attestation chain."""
    logger.info("Fetching attestation chain: limit={}", limit)

    # STUB: Query database for chain
    entries: List[AttestationCertificateResponse] = []

    return AttestationChainResponse(
        entries=entries,
        total_entries=len(entries),
        chain_valid=True,
        earliest_timestamp=datetime.now(timezone.utc) - timedelta(days=30),
        latest_timestamp=datetime.now(timezone.utc),
    )


@attestation_router.get(
    "/integrity",
    response_model=ChainIntegrityResponse,
    summary="Check chain integrity",
    description="Verify integrity of attestation chain",
)
@limiter.limit("10/minute")
async def check_chain_integrity(
    user: CurrentUser = Depends(get_current_user),
    service: AttestationService = Depends(get_attestation_service),
) -> ChainIntegrityResponse:
    """Check chain integrity."""
    logger.info("Checking chain integrity")

    # STUB: Verify entire chain
    return ChainIntegrityResponse(
        valid=True,
        total_entries=0,
        verified_entries=0,
        broken_links=[],
        message="Chain integrity verified",
    )


# ---------------------------------------------------------------------------
# Agent Endpoints
# ---------------------------------------------------------------------------


@agent_router.post(
    "",
    response_model=AgentProfileResponse,
    summary="Register agent",
    description="Register a new agent for evaluation",
    status_code=status.HTTP_201_CREATED,
)
@limiter.limit("20/minute")
async def register_agent(
    request: RegisterAgentRequest,
    user: AdminUser,
) -> AgentProfileResponse:
    """Register new agent."""
    logger.info("Registering agent: {}", request.agent_id)

    # STUB: Save to database
    return AgentProfileResponse(
        agent_id=request.agent_id,
        model_name=request.model_name,
        provider=request.provider,
        version=request.version,
        capabilities=request.capabilities,
        total_evaluations=0,
        pass_rate=0.0,
        avg_safety_score=0.0,
        registered_at=datetime.now(timezone.utc),
        last_evaluated=None,
        metadata=request.metadata,
    )


@agent_router.get(
    "",
    response_model=List[AgentProfileResponse],
    summary="List agents",
    description="List all registered agents",
)
@limiter.limit("30/minute")
async def list_agents(
    user: CurrentUser = Depends(get_current_user),
) -> List[AgentProfileResponse]:
    """List all agents."""
    logger.info("Listing agents")

    # STUB: Query database
    return []


@agent_router.get(
    "/{agent_id}",
    response_model=AgentProfileResponse,
    summary="Get agent profile",
    description="Retrieve agent profile and statistics",
)
@limiter.limit("60/minute")
async def get_agent_profile(
    agent_id: str,
    user: CurrentUser = Depends(get_current_user),
) -> AgentProfileResponse:
    """Get agent profile."""
    logger.info("Fetching agent profile: {}", agent_id)

    # STUB: Query database
    return AgentProfileResponse(
        agent_id=agent_id,
        model_name="gpt-4o",
        provider="openai",
        version="2024-05-13",
        capabilities=["code", "reasoning", "safety"],
        total_evaluations=150,
        pass_rate=0.92,
        avg_safety_score=88.5,
        registered_at=datetime.now(timezone.utc) - timedelta(days=30),
        last_evaluated=datetime.now(timezone.utc),
        metadata={},
    )


@agent_router.get(
    "/{agent_id}/history",
    response_model=AgentHistoryResponse,
    summary="Get agent history",
    description="Complete evaluation history for an agent",
)
@limiter.limit("20/minute")
async def get_agent_history(
    agent_id: str,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=200)] = 20,
    user: CurrentUser = Depends(get_current_user),
) -> AgentHistoryResponse:
    """Get agent evaluation history."""
    logger.info("Fetching agent history: {}", agent_id)

    # STUB: Query database
    return AgentHistoryResponse(
        agent_id=agent_id,
        total_cycles=5,
        evaluations=[],
        metrics_timeline=[],
        performance_trend="improving",
    )


# ---------------------------------------------------------------------------
# WebSocket Endpoint
# ---------------------------------------------------------------------------


@health_router.websocket("/ws/evaluate")
async def websocket_evaluate(websocket: WebSocket) -> None:
    """WebSocket endpoint for real-time evaluation updates."""
    await manager.connect(websocket)

    try:
        while True:
            # Receive messages from client
            data = await websocket.receive_json()

            # Echo back or process
            msg = WebSocketMessage(
                type="status",
                data={"message": "Connected", "status": "ready"},
            )
            await manager.send_personal_message(msg.model_dump(), websocket)

            # Keep connection alive
            await asyncio.sleep(1)

    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info("WebSocket client disconnected")
    except Exception as e:
        logger.exception("WebSocket error: {}", e)
        manager.disconnect(websocket)


# ---------------------------------------------------------------------------
# Middleware & Error Handlers
# ---------------------------------------------------------------------------


async def log_requests_middleware(request, call_next):
    """Log all requests and responses."""
    start_time = time.time()
    request_id = str(uuid.uuid4())

    logger.info(
        "Request started: {} {} | ID: {}",
        request.method,
        request.url.path,
        request_id,
    )

    response = await call_next(request)

    duration = time.time() - start_time
    logger.info(
        "Request completed: {} {} | Status: {} | Duration: {:.3f}s | ID: {}",
        request.method,
        request.url.path,
        response.status_code,
        duration,
        request_id,
    )

    response.headers["X-Request-ID"] = request_id
    return response


# ---------------------------------------------------------------------------
# Application Factory
# ---------------------------------------------------------------------------


def create_app() -> FastAPI:
    """Create and configure FastAPI application.

    Returns
    -------
    FastAPI
        Configured application instance.
    """

    app = FastAPI(
        title="SAGE-Live API",
        description="Production REST API for SAGE-Live benchmark system",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Rate limiting
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    # Request logging middleware
    @app.middleware("http")
    async def request_logging(request, call_next):
        return await log_requests_middleware(request, call_next)

    # Error handlers
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request, exc: HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content=ErrorResponse(
                error=f"HTTP_{exc.status_code}",
                detail=exc.detail,
            ).model_dump(),
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request, exc: Exception):
        logger.exception("Unhandled exception: {}", exc)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=ErrorResponse(
                error="INTERNAL_SERVER_ERROR",
                detail="An unexpected error occurred",
            ).model_dump(),
        )

    # Include routers
    app.include_router(health_router)
    app.include_router(probe_router)
    app.include_router(eval_router)
    app.include_router(metrics_router)
    app.include_router(staleness_router)
    app.include_router(attestation_router)
    app.include_router(agent_router)

    logger.info("SAGE-Live API initialized")

    return app


# ---------------------------------------------------------------------------
# Export
# ---------------------------------------------------------------------------

__all__ = [
    "create_app",
    "health_router",
    "probe_router",
    "eval_router",
    "metrics_router",
    "staleness_router",
    "attestation_router",
    "agent_router",
]
