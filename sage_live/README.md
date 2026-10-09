# SAGE-Live

> **Self-Refreshing, Cryptographically Attested AI Safety Benchmark System**

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi)](https://fastapi.tiangolo.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Coverage: 80%+](https://img.shields.io/badge/coverage-80%25+-brightgreen.svg)]()

SAGE-Live is a production-grade AI safety benchmarking platform that automatically refreshes its probe pool, detects benchmark staleness and contamination, and provides cryptographic proof-of-integrity for every evaluation window via an Ed25519 hash chain.

---

## Architecture

```
sage_live/
├── core/               # Business logic
│   ├── probe_generator.py   # Adversarial probe synthesis & dedup
│   ├── staleness_index.py   # Multi-dim staleness scoring
│   ├── attestation.py       # Ed25519 hash-chain signing
│   └── metrics.py           # Prometheus instrumentation
├── agents/             # Agent abstractions
│   ├── base_agent.py        # Abstract BaseAgent + AgentResponse
│   └── evaluator.py         # Judge LLM scoring agent
├── red_blue/           # Adversarial evaluation
│   ├── red_team.py          # Iterative attacker agent
│   └── blue_team.py         # Defender + defence-report agent
├── database/           # SQLModel ORM + Pydantic v2 models
│   └── models.py            # ProbeTask, EvaluationResult, …
├── api/                # FastAPI REST layer
│   └── routes.py            # All versioned endpoints
├── configs/
│   └── default.yaml         # Default configuration
├── tests/
│   └── test_all.py          # Comprehensive pytest suite
└── docker/
    └── Dockerfile           # Multi-stage production image
```

---

## Quickstart

### 1. Clone & install

```bash
git clone https://github.com/sage-live/sage-live.git
cd sage-live

# Install Poetry (if not already installed)
curl -sSL https://install.python-poetry.org | python3 -

# Install all dependencies (including dev)
poetry install

# Alternatively, with pip
pip install -r requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
# Edit .env — at minimum set:
#   SECRET_KEY, OPENAI_API_KEY, ANTHROPIC_API_KEY
#   ATTESTATION_PRIVATE_KEY, ATTESTATION_PUBLIC_KEY
```

### 3. Run the API server

```bash
# Development (auto-reload)
poetry run uvicorn sage_live.api:app --reload --port 8000

# Or with the CLI entry point
poetry run sage-live
```

Open **http://localhost:8000/docs** for the interactive Swagger UI.

### 4. Run tests

```bash
poetry run pytest tests/ -v --cov=sage_live
```

---

## Key Subsystems

### Probe Generator
Synthesises adversarial probes across six vulnerability classes using a
configurable template bank (swap in a real LLM call in `probe_generator.py`).
Character-trigram cosine similarity deduplification prevents near-duplicates
from entering the benchmark pool.

### Staleness Index
Computes a four-dimensional composite staleness score (age, leakage,
coverage, variance) and recommends one of four actions:
`healthy → warning → retire → critical`.

### Attestation
Every evaluation window is signed with an Ed25519 private key.  Each ledger
entry includes the SHA3-256 of the previous entry's `combined_hash`, forming
a tamper-evident chain.  Call `POST /api/v1/attestation/verify` to verify any
sub-chain.

### Red / Blue Team
`RedTeamAgent` iteratively refines adversarial prompts across up to N rounds,
using target-model responses as feedback.  `BlueTeamAgent` analyses the
resulting `RedTeamResult` and produces a structured `DefenceReport` with
actionable system-prompt patches and filter rules.

---

## API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Liveness / readiness probe |
| `GET` | `/api/v1/probes` | List active probes (paginated) |
| `POST` | `/api/v1/probes/generate` | Generate a new probe batch |
| `GET` | `/api/v1/probes/{probe_id}` | Fetch a single probe |
| `POST` | `/api/v1/evaluate` | Submit agent response for scoring |
| `GET` | `/api/v1/results` | List evaluation results |
| `GET` | `/api/v1/staleness` | Run staleness scan |
| `GET` | `/api/v1/attestation/latest` | Latest ledger entry |
| `POST` | `/api/v1/attestation/verify` | Verify hash chain |

Full OpenAPI schema: **http://localhost:8000/openapi.json**

---

## Docker

```bash
# Build
docker build -f docker/Dockerfile -t sage-live:latest .

# Run
docker run -p 8000:8000 --env-file .env sage-live:latest

# Health check
curl http://localhost:8000/health
```

---

## Configuration

All configuration is driven by:
1. **`configs/default.yaml`** — base values for every subsystem
2. **`.env`** — environment variable overrides (take precedence)

Key variables:

| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | SQLAlchemy async DB URL |
| `ATTESTATION_PRIVATE_KEY` | Hex-encoded Ed25519 seed (32 bytes) |
| `OPENAI_API_KEY` | OpenAI API key |
| `ANTHROPIC_API_KEY` | Anthropic API key |
| `STALENESS_THRESHOLD_DAYS` | Days before a probe is considered stale |
| `PROMETHEUS_PORT` | Port for the Prometheus `/metrics` endpoint |

---

## Contributing

1. Fork the repo and create a feature branch
2. Write tests for all new behaviour (`pytest --cov` must stay ≥ 80 %)
3. Run `ruff check .` and `mypy sage_live/` before pushing
4. Open a pull request against `main`

---

## License

MIT — see [LICENSE](LICENSE).
