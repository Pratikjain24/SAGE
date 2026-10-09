"""
sage_live.api.dependencies
~~~~~~~~~~~~~~~~~~~~~~~~~~~

FastAPI dependency injection utilities.

Provides:
* Database session management
* Service singletons
* Authentication dependencies
* Rate limiting configuration
"""

from __future__ import annotations

from typing import AsyncGenerator, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel

from sage_live.core.attestation import AttestationService
from sage_live.core.metrics import SAGELiveMetrics
from sage_live.core.probe_generator import ProbeGenerator
from sage_live.core.staleness_index import StalenessIndex

# ---------------------------------------------------------------------------
# Database Configuration
# ---------------------------------------------------------------------------

DATABASE_URL = "postgresql+asyncpg://user:pass@localhost/sagedb"

engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    future=True,
    pool_size=20,
    max_overflow=10,
)

async_session_maker = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Provide async database session.

    Yields
    ------
    AsyncSession
        SQLAlchemy async session.
    """
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# ---------------------------------------------------------------------------
# Service Singletons
# ---------------------------------------------------------------------------

_probe_generator: Optional[ProbeGenerator] = None
_staleness_index: Optional[StalenessIndex] = None
_attestation_service: Optional[AttestationService] = None
_metrics_engine: Optional[SAGELiveMetrics] = None


def get_probe_generator() -> ProbeGenerator:
    """Get or create ProbeGenerator singleton.

    Returns
    -------
    ProbeGenerator
        Shared probe generator instance.
    """
    global _probe_generator
    if _probe_generator is None:
        logger.info("Initializing ProbeGenerator singleton")
        _probe_generator = ProbeGenerator(generation=1)
    return _probe_generator


def get_staleness_index() -> StalenessIndex:
    """Get or create StalenessIndex singleton.

    Returns
    -------
    StalenessIndex
        Shared staleness index instance.
    """
    global _staleness_index
    if _staleness_index is None:
        logger.info("Initializing StalenessIndex singleton")
        _staleness_index = StalenessIndex()
    return _staleness_index


def get_attestation_service() -> AttestationService:
    """Get or create AttestationService singleton.

    Returns
    -------
    AttestationService
        Shared attestation service instance.
    """
    global _attestation_service
    if _attestation_service is None:
        logger.info("Initializing AttestationService singleton")
        _attestation_service = AttestationService()
    return _attestation_service


def get_metrics_engine() -> SAGELiveMetrics:
    """Get or create SAGELiveMetrics singleton.

    Returns
    -------
    SAGELiveMetrics
        Shared metrics engine instance.
    """
    global _metrics_engine
    if _metrics_engine is None:
        logger.info("Initializing SAGELiveMetrics singleton")
        _metrics_engine = SAGELiveMetrics(n_bootstrap=2000)
    return _metrics_engine


# ---------------------------------------------------------------------------
# Authentication
# ---------------------------------------------------------------------------

security = HTTPBearer()


async def verify_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict:
    """Verify JWT token.

    Parameters
    ----------
    credentials:
        Bearer token credentials.

    Returns
    -------
    dict
        Decoded token payload.

    Raises
    ------
    HTTPException
        401 if token is invalid.
    """
    token = credentials.credentials

    # TODO: Implement JWT verification with python-jose
    # from jose import jwt, JWTError
    # try:
    #     payload = jwt.decode(token, SECRET_KEY, algorithms=["RS256"])
    #     return payload
    # except JWTError:
    #     raise HTTPException(401, "Invalid token")

    # Stub implementation
    logger.debug("Verifying token: {}...", token[:20])
    return {"sub": "user-123", "role": "admin"}


async def get_current_user_id(token_payload: dict = Depends(verify_token)) -> str:
    """Extract user ID from token.

    Parameters
    ----------
    token_payload:
        Decoded JWT payload.

    Returns
    -------
    str
        User ID.
    """
    return token_payload.get("sub", "unknown")


# ---------------------------------------------------------------------------
# Rate Limiting
# ---------------------------------------------------------------------------

from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["1000/hour"],
    storage_uri="memory://",  # Use Redis in production: "redis://localhost:6379"
)


# ---------------------------------------------------------------------------
# Exports
# ---------------------------------------------------------------------------

__all__ = [
    "get_session",
    "get_probe_generator",
    "get_staleness_index",
    "get_attestation_service",
    "get_metrics_engine",
    "verify_token",
    "get_current_user_id",
    "limiter",
]
