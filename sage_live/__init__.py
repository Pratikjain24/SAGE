"""
SAGE-Live: Self-Refreshing, Cryptographically Attested AI Safety Benchmark System.

Top-level package — re-exports the most commonly used public symbols so that
callers can do ``from sage_live import Settings, get_settings`` without
knowing the internal module layout.
"""

from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version

try:
    __version__: str = version("sage-live")
except PackageNotFoundError:
    __version__ = "0.0.0-dev"

__all__: list[str] = ["__version__"]
