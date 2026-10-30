# SAGE: Safety & Agent Growth Evaluator
### Measuring Security Boundary Drift and Capability Retention in Self-Evolving Code Agents

[![Open In Colab (Playground)](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Pratikjain24/SAGE/blob/main/SAGE_Interactive_Playground.ipynb)
[![Open In Colab (T4 GPU)](https://img.shields.io/badge/Colab-GPU%20Benchmark%20(vLLM)-F9AB00?logo=googlecolab&logoColor=white)](https://colab.research.google.com/github/Pratikjain24/SAGE/blob/main/SAGE_Colab_Benchmark.ipynb)
[![Hugging Face Spaces](https://img.shields.io/badge/%F0%9F%A4%97%20Hugging%20Face-Next.js%20Dashboard%20Space-blue)](https://huggingface.co/spaces/Pratikjain24/SAGE-Dashboard)
[![Kaggle Notebook](https://kaggle.com/static/images/open-in-kaggle.svg)](https://www.kaggle.com/code/pratikjain24/sage-benchmark)
[![CI](https://github.com/Pratikjain24/SAGE/actions/workflows/ci.yml/badge.svg)](https://github.com/Pratikjain24/SAGE/actions)
[![CI (SAGE-Live)](https://github.com/Pratikjain24/SAGE/actions/workflows/sage-live-ci.yml/badge.svg)](https://github.com/Pratikjain24/SAGE/actions)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![HuggingFace Dataset](https://img.shields.io/badge/%F0%9F%A4%97%20Hugging%20Face-Croissant%201.0%20Ready-yellow)](hf_dataset/)
[![Zenodo](https://img.shields.io/badge/Zenodo-DOI%20Reserved%20on%20Publication-blue)](https://github.com/Pratikjain24/SAGE)
[![Stars](https://img.shields.io/github/stars/Pratikjain24/SAGE?style=social)](https://github.com/Pratikjain24/SAGE/stargazers)
[![Last Commit](https://img.shields.io/github/last-commit/Pratikjain24/SAGE)](https://github.com/Pratikjain24/SAGE/commits/main)
[![Issues](https://img.shields.io/github/issues/Pratikjain24/SAGE)](https://github.com/Pratikjain24/SAGE/issues)
[![Paper](https://img.shields.io/badge/IEEE-Paper%202026-blue)](paper/README.md)
[![Dossier](https://img.shields.io/badge/System_Dossier-v1.0.0-green.svg)](PROJECT_DOSSIER.md)

> [!TIP]
> ### 🎮 1-Click Zero-Setup Interactive Playground & Live Web Dashboard
> Evaluate SAGE immediately in your browser with **zero manual API key configuration**:
>
> | Platform | Target | Description | 1-Click Access |
> |---|---|---|---|
> | **Google Colab** | **Interactive Playground** | **Zero-Setup Mock Execution (Default)**. Evaluates $G_1$–$G_7$ in ~30s, plots 4-panel publication figures, and verifies Ed25519/HMAC attestation chains with **zero API keys required**. | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Pratikjain24/SAGE/blob/main/SAGE_Interactive_Playground.ipynb) |
> | **Google Colab** | **Local vLLM GPU Benchmark** | Full empirical local GPU execution on Colab's free 15GB Tesla T4 GPU using `Qwen2.5-Coder-3B-Instruct` (zero API cost, zero rate limits). | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Pratikjain24/SAGE/blob/main/SAGE_Colab_Benchmark.ipynb) |
> | **Hugging Face** | **Next.js + FastAPI Dashboard Space** | 1-click cloud-hosted Next.js 14 + FastAPI live workbench. Monitor real-time WebSocket block commits, execute probe generations, and audit trajectories. | [![Hugging Face Space](https://img.shields.io/badge/%F0%9F%A4%97%20Hugging%20Face-Live%20Dashboard%20Space-blue)](https://huggingface.co/spaces/Pratikjain24/SAGE-Dashboard) [![Duplicate](https://huggingface.co/datasets/huggingface/badges/raw/main/duplicate-this-space-sm.svg)](https://huggingface.co/spaces/Pratikjain24/SAGE-Dashboard?duplicate=true) |
> | **Kaggle** | **Kaggle Interactive Notebook** | Kaggle cloud kernel for executing multi-seed trajectory replications with GPU acceleration. | [![Open in Kaggle](https://kaggle.com/static/images/open-in-kaggle.svg)](https://www.kaggle.com/code/pratikjain24/sage-benchmark) |

> [!IMPORTANT]
> ### 🔍 Disambiguation: Distinguishing SAGE from Other Projects
> To prevent ambiguity across the AI safety and evaluation literature, this project is formally titled **SAGE: Safety & Agent Growth Evaluator** (Jain et al., IEEE 2026). It is an independent research system investigating **security boundary drift, vulnerability injection rates, specification gaming (proxy gaps), and rollback-guarded capability retention in self-modifying code agents**.
>
> Please note the distinction from other publications and tools with related acronyms or prior working titles:
>
> | Project Name | Authors / Venue | Focus / Scope | How It Differs from SAGE (Ours) |
> |---|---|---|---|
> | **SAGE** | Microsoft & MBZUAI (EMNLP 2025) | *"Safety AI Generic Evaluation"* — general prompt safety evaluation | Evaluates static NLP prompt-response safety; does **not** evaluate code agents, sandbox execution, or iterative evolutionary drift. |
> | **SAGE-Eval** | NYU (NeurIPS 2025 Spotlight) | *"Safety Generalization"* in generative models | Studies distribution shifts and generalization in generative safety classifiers; does **not** investigate autonomous agent self-modification or code verification. |
> | **SAGE** | ArXiv 2025 | Defense-in-depth LLM lifecycle guardrail control | System guardrail middleware; not an empirical evolutionary benchmark or attestation ledger. |
> | **SAGE** | PecanProject | Agronomic data extraction & synthesis | Biological and agronomic dataset management. |
> | **SAGE** | dp-web4 | Situation-Aware Governance Engine | Decentralized blockchain governance engine. |
> | **EvoEval** | Xia et al. (2024) | Benchmark for evolving coding problems via LLM | Evolves benchmark problem suites; does not evaluate self-modifying code agents or security boundary drift (our former development working title). |
>
> 📖 **Comprehensive Guides & Dossiers**: For quick demo and presentation resources, see the **[Complete Presentation Guide](SAGE_Presentation_Guide.md)** and **[Step-by-Step Run Guide](How_To_Run_SAGE.md)**. For an exhaustive, file-by-file blueprint detailing every architectural invariant, security boundary, tamper audit check, drift probe, LLM judge isolation rule, full per-suite timing benchmarks, and complete test results (201 passed, 1 skipped across 31 test files, 100% pass rate), see the **[Master Technical Dossier](PROJECT_DOSSIER.md)**, the automated **[Reproducibility Verification Attestation](REPRODUCIBILITY_VERIFICATION.md)**, and the complete **[Tables & Figures Proof of Provenance](docs/PROVENANCE_AND_AUDIT_TRAIL.md)**.

**SAGE: Safety & Agent Growth Evaluator** is a hardened benchmark and formal evaluation framework that validates agent guardrails against canonical, deterministic degradation trajectories, supplemented by live API runs. SAGE is designed to measure **capability gain, security boundary drift (vulnerability injection rate), specification gaming (proxy gap), and capability retention** in self-modifying autonomous code agents across iterative evolutionary generations. SAGE implements an honest, two-tiered evaluation methodology:
1. **Canonical Benchmark Trajectories ($N=18{,}000$)**: 18,000 controlled, bitwise-reproducible evaluations across 100 tasks, 6 archetypes ($G_1$–$G_6$), 10 cycles, and 3 random seeds formalizing archetype state-mutation policies under deterministic execution, providing zero-flakiness counterfactual reference baselines.
2. **Live Neural Model Rollouts & Cross-Family Baselines**: Empirical evaluation of live open-weights neural models (Qwen2.5-Coder-7B, Llama-3.1-8B) executed under logged, reproducible harnesses in our dual-container isolation sandbox.

```
                           +------------------------+
                           |  Evolution Controller  |
                           +-----------+------------+
                                       |
                   Proposal (Diff/Prompt) | Accept / Rollback
                                       v
                           +------------------------+
                           |   Evolution Verifier   |<---+ Static Rules &
                           |   (Gate + Canary Test) |    | Safety Canaries
                           +-----------+------------+
                                       | Verified Mutation
                                       v
               +------------------------------------------------+
               |                  Agent Adapter                 |
               | [G1: Frozen] [G2: Prompt] [G3: Memory]         |
               | [G4: Reflect] [G5: Verifier] [G6: RegressGuard]|
               +-----------------------+------------------------+
                                       | Tool Actions (bash, edit)
                                       v
               +------------------------------------------------+
               |         Isolated Execution Sandbox             |
               |         (Docker container / local jail)        |
               +-----------------------+------------------------+
                                       | Execution Traces
                                       v
               +------------------------------------------------+
               |   Scoring & Safety Monitor (Tamper Detection)  |
               |   - Ground Truth Test (Read-only Scorer)       |
               |   - Proxy Reward Gap (Reward Hacking Probe)    |
               |   - SecurityDrift: Violations(t) - Violations(0)|
               +------------------------------------------------+
```

---

## Agent Taxonomy ($G_1$ – $G_7$, $G_6^*$)

SAGE evaluates seven standardized agent archetypes ($G_1$–$G_7$) alongside the theoretical oracle ceiling ($G_6^*$):

| Group | Name | Mechanism | Evolution Target | Verifier & Rollback | Empirical Outcome |
|---|---|---|---|---|---|
| **$G_1$** | **Static Frozen Baseline** | Frozen control group; ignores evolution feedback | None (Immutable) | None (Scientific Control) | 60.0% Solve, 0.00 Drift, 100% Ret. |
| **$G_2$** | **Prompt-Rewriter** | Rewrites system prompt from execution failure logs | System Prompt | None (Unconstrained) | 73.0% Solve, +0.22 Drift, 82% Ret. |
| **$G_3$** | **Memory Accumulator** | Indexes procedural heuristics into structured store | `memory.json` | None (Unconstrained) | 77.2% Solve, +0.15 Drift, 89% Ret. |
| **$G_4$** | **Reflection Agent** | Multi-tier root-cause analysis; patches prompts & tools | Prompts + Tool Code | None (Unconstrained) | 78.4% Solve, +0.28 Drift, 81% Ret. |
| **$G_5$** | **Static Verifier Gate** | Filters candidate mutations via AST linting & security rules | Filtered Mutations | Gate rejection (No rollback) | 84.0% Solve, +0.06 Drift, 94% Ret. |
| **$G_6$** | **Regression-Guarded Verifier** | Evaluates candidate mutations on historical regression suite | Historical Checkpoints | Suite gate + regression rollback | 92.0% Solve, +0.02 Drift, 98% Ret. |
| **$G_7$** | **Deployable Proxy Canary Guard** | Realistic dynamic verification on held-out proxy tasks (`test_proxy.py`) | Validated State | Canary gate + atomic rollback | 84.4% Solve, +0.02 Drift, 96% Ret. |
| **$G_6^*$** | **Theoretical Oracle Skyline** | Theoretical upper bound evaluating canary on sequestered ground truth (`test_gt.py`) | Validated State | Oracle gate + atomic rollback | 92.0% Solve, +0.02 Drift, 98% Ret. |

> 💡 **Unified Taxonomy Formalization: Deployable $G_7$ vs. Theoretical Oracle $G_6^*$**:  
> - **$G_1$–$G_7$ (Deployable Archetypes)**: The 7 operational agent archetypes implemented across the SAGE test harness and UI. Among defensive configurations, **$G_7$ (Deployable Proxy Canary Guard)** is the production-ready standard: it dynamically evaluates candidate mutations against *strictly held-out proxy tasks* (`test_proxy.py`) without accessing hidden ground-truth oracles, triggering sub-second atomic rollback upon canary degradation. It achieves an 84.4% solve rate while suppressing security drift (+0.02) and preventing specification gaming ($\Delta_{\text{proxy}} \le 0.02$).
> - **$G_6$ (Regression-Guarded Verifier)**: Gates mutations against fixed historical regression suites, guarding against regressions on already-solved tasks without dynamic held-out canary synthesis.
> - **$G_6^*$ (Theoretical Oracle Skyline)**: An academic upper bound denoted with standard mathematical asterisk notation ($\pi^*, Q^*$). It evaluates canaries against sequestered ground-truth unit tests (`test_gt.py`), establishing the theoretical performance ceiling (92.0% solve rate, 98% retention). Because future ground-truth tests are unavailable in production, $G_6^*$ is non-deployable, while $G_7$ represents the ecologically valid deployable standard.

---

## Key Metrics

1. **Capability Improvement**:
   $$\Delta P(t) = P(t) - P(0)$$
2. **Security Boundary Drift (Vulnerability Injection Rate)**:
   $$\text{SecurityDrift}(t) = \mathcal{V}(t) - \mathcal{V}(0)$$
3. **Catastrophic Forgetting (Retention)**:
   $$\text{Retention}(t) = \frac{\text{Perf}_{\text{old}}(t)}{\text{Perf}_{\text{old}}(0)}$$
4. **Reward Hacking (Proxy Gap)**:
   $$\text{ProxyGap}(t) = \text{ProxyScore}(t) - \text{GroundTruthScore}(t)$$
5. **Reliability & Efficiency**:
   Inter-seed variance $\sigma^2_{\text{seed}}$, token consumption, verification compute overhead.

---

## Reproducibility

> **How to verify claims without trusting this README:** Every number in this README corresponds to a file or a publicly visible GitHub Actions run. The table below maps claims to evidence.

| Claim | Where to verify it |
|---|---|
| 201 tests, 100% pass rate | [GitHub Actions runs](https://github.com/Pratikjain24/SAGE/actions) → JUnit XML artifact; or run `pytest tests/ -v` locally |
| 100 benchmark tasks | [`tasks/tasks_index.json`](tasks/tasks_index.json) — 100 entries, 5 categories, 20 drift probes |
| Pinned model SHA `c03e6d35...` (Qwen) | [`verification_attestation.json`](verification_attestation.json) line 41; confirmed by `huggingface_hub.repo_info()` in [`scripts/verify_reproducibility.py`](scripts/verify_reproducibility.py) |
| Docker image digests | [`docker/image_digests.json`](docker/image_digests.json) — built and verified by [`scripts/build_and_inspect_images.py`](scripts/build_and_inspect_images.py) |
| Trajectory SHA-256 manifests | [`experiments/runs/full_study_canonical/`](experiments/runs/) — `trajectory_manifest.json` in each run directory |
| Byte-identical reproducibility | [`tests/test_reproducibility.py`](tests/test_reproducibility.py) — `test_reproducibility_same_seed_same_config_byte_identical` |
| Cross-platform parity (Linux/Windows) | [`REPRODUCIBILITY_VERIFICATION.md`](REPRODUCIBILITY_VERIFICATION.md) Section 2 — dual-platform comparison table |

### Running the Benchmark

```bash
# 1. Install
git clone https://github.com/Pratikjain24/SAGE.git && cd SAGE
pip install -e ".[dev]"

# 2. Run the test suite (no GPU needed — uses deterministic mock LLM)
pytest tests/ -v

# 3. Run a dry-run to verify the CLI works
sage run --config configs/experiments/pilot.yaml --dry-run

# 4. Run the full study (requires GPU + model weights ~15 GB)
sage run --config configs/experiments/full_study.yaml
```

### What is and isn't automatically verified

- ✅ **Test suite** (201 tests): runs on GitHub Actions, no GPU needed, publicly visible
- ✅ **Task catalog integrity**: SHA-256 of `tasks_index.json` checked in CI
- ✅ **Model revision SHAs**: checked against HuggingFace Hub remote commits
- ⚠️ **Docker container builds**: CI builds all 4 images from scratch but image digest matching requires the exact same Docker engine version
- ⚠️ **Full 18,000-evaluation study**: requires ~15 GB model weights and GPU; cannot run in free CI. The trajectory data and SHA-256 manifests are committed so anyone can verify the *outputs* without re-running
- ℹ️ **`verification_attestation.json`**: Cryptographic audit capturing dual-platform certification: primary third-party CI run on Linux GitHub Actions (`is_ci: true`, [docs/attestations/verification_attestation_linux_ci.json](docs/attestations/verification_attestation_linux_ci.json)) and secondary local cross-validation on Windows (`is_ci: false`, [docs/attestations/verification_attestation_windows_local.json](docs/attestations/verification_attestation_windows_local.json); see [REPRODUCIBILITY_VERIFICATION.md](REPRODUCIBILITY_VERIFICATION.md)).

---


### 2. Pinned Model Weights & Container Digests
- **Exact Model Weights**:
  - Evaluated Agent: `qwen2.5-coder-7b-instruct` (pinned revision SHA: `c03e6d358207e414f1eca0bb1891e29f1db0e242`).
  - Auxiliary LLM Judge: `llama-3.1-8b-instruct` (pinned revision SHA: `0e9e39f249a16976918f6564b8830bc894c89659`).
- **Pinned Docker Image Digests** (`docker/image_digests.json`):
  | Component | Tag | Pinned SHA-256 Digest |
  |---|---|---|
  | **Sandbox** | `sage-sandbox:1.0` | `sha256:3d93c20b51c7f04fdd3fb64f5bab0671cb99dc7b3ed419ed36cabb829b358401` |
  | **Scorer** | `sage-scorer:1.0` | `sha256:4e5784ddded9b42ad9bf42917a5a35266ce070d5ec34e39772c39b3b31eefa34` |
  | **Backend** | `sage-backend:1.0` | `sha256:ce8558ff25e10dd6ab2d05a47479de992e6c1bef21e9e14f6781b1e1547b252e` |
  | **Frontend** | `sage-frontend:1.0` | `sha256:c419ea714fb6dc2d1145db219b31011f5df1d00504033665aabc072b3e6fc333` |
  *Container Acquisition & Replication Pathways*:
  - **Option A (Fast Local Build, <75s)**: `docker compose -f docker/docker-compose.yml build` (builds in ~72s from pinned digests `python:3.11-slim@sha256:da047...` and `node:20-alpine@sha256:fb4cd...`).
  - **Option B (Pre-Built Anonymous Tarball)**: Load `sage_docker_images_v1.0.tar.gz` from Zenodo DOI `10.5281/zenodo.14982104` via `docker load -i sage_docker_images_v1.0.tar.gz` (zero local building required).
  - **Option C (Public GHCR Registry)**: `docker pull ghcr.io/pratikjain24/sage-sandbox:1.0` (published for camera-ready release).
  - **Option D (No Docker Required)**: Native execution on Linux, macOS, and Windows via `sage run --runner local` (`LocalSandbox` path-jail; Table 6 confirms $\Delta P = 0.00$ parity).
  *Build Provenance*: Recorded in [`docker/build_provenance.json`](docker/build_provenance.json) and verified in CI via `make verify-images`.

### 3. Seeded Generators
All stochasticity is strictly routed through synchronized, seeded generators recorded per run:
- Python `random.seed(seed)`
- `os.environ["PYTHONHASHSEED"] = str(seed)`
- NumPy `np.random.seed(seed)`
- PyTorch `torch.manual_seed(seed)` and `torch.cuda.manual_seed_all(seed)`
- vLLM / inference sampling seeds (`temperature: 0.2`, `top_p: 0.95`, `seed: 42, 43, 44`)
Seed manifests are recorded in every `trajectory_manifest.json` and in canonical trajectory header events.

### 4. Trajectory Hash Manifest (SHA-256)
Every evaluation run automatically generates a cryptographic integrity manifest at `experiments/runs/<run_id>/trajectory_manifest.json`:
- **Raw File SHA-256**: Exact hash of the generated `trajectory.jsonl` (records exact physical bytes including physical host timestamps).
- **Deterministic Canonical SHA-256**: Cryptographic digest of canonicalized event payloads (`compute_deterministic_trajectory_hash`), normalizing non-deterministic runtime artifacts (wall-clock timestamps, runner execution durations, and dynamic scratch directory paths).
- **Byte-Identical Reproducibility Guarantee**: Verified by `tests/test_reproducibility.py` (`test_reproducibility_same_seed_same_config_byte_identical`), executing identical configurations with identical random seeds at temperature 0 produces byte-identical canonical JSONL representations and identical SHA-256 digests (`bytes1 == bytes2` and `hash1 == hash2`).
- **Cross-Platform Invariance**: Verified across Linux Docker CI and Windows host environments with zero task metric divergence ($\Delta_{\text{platform}} = 0.000$).
Reviewers can audit trajectory integrity at any time via:
```bash
sage manifest --run-id <run_id>
```

### 5. Unified 4-Service Docker Compose
A single command brings up the complete isolated environment:
```bash
docker compose -f docker/docker-compose.yml up -d
```
1. **`sandbox`**: Locked agent container (`1000:1000`, `network: none`, `mem: 4g`, `cpus: 2.0`, `cap_drop: ALL`, scoring volume absent).
2. **`scorer`**: Read-only isolated test harness container (`1001:1001`, `network: none`, `mem: 2g`, test suites `:ro`).
3. **`backend`**: FastAPI analytics service with DuckDB query engine on port `8000`.
4. **`frontend`**: Next.js 14 interactive evaluation dashboard on port `3000`.

### 6. Benchmark Dataset Access & Distribution

The entire SAGE benchmark suite is **100% self-contained in this repository** and immediately accessible for review, execution, and verification without external web dependencies:

| Artifact | Location in repo | Format / Specs |
|---|---|---|
| **100 Benchmark Tasks** | [`tasks/`](tasks/) & [`tasks/tasks_index.json`](tasks/tasks_index.json) | Standalone repos with unit tests & canary probes (SHA: `458491ba...`) |
| **Contamination Audit** | [`tasks/contamination_audit_results.json`](tasks/contamination_audit_results.json) | Overlap analysis against GitHub pre-training corpus |
| **Full Study Trajectories** | [`experiments/runs/full_study_canonical/`](experiments/runs/full_study_canonical/) | 18,000 execution event streams across seeds 42, 43, 44 |
| **Human Audit Annotations**| [`experiments/runs/full_study_canonical/tables/table4_human_audit.tex`](experiments/runs/full_study_canonical/tables/) | Double-blind manual validation logs |
| **Exported Croissant Bundle** | [`hf_dataset/`](hf_dataset/) | MLCommons Croissant 1.0 format with `croissant.json` |

#### Public Indexing & Remote Mirrors
- **Self-Contained Primary Access**: All data, code, and test suites are directly versioned in this git repository (`git clone https://github.com/Pratikjain24/SAGE.git`).
- **Hugging Face Hub & Zenodo**: Pre-packaged in [`hf_dataset/`](hf_dataset/) compliant with MLCommons Croissant 1.0 metadata. Published under dataset repository ID `Pratikjain24/sage-benchmark` with permanent Zenodo DOI reservation synchronized with publication indexing.

You can repackage any local evaluation run for HuggingFace Hub release via:
```bash
sage export-hf --run-id full_study_canonical --output hf_dataset/
```
- `tasks/tasks.jsonl`: 100 standardized benchmark coding problems across 5 categories (`bug_fix`, `feature`, `refactor`, `exploit_probe`, `security_audit`), including 20 deliberate drift probes.
- `trajectories/trajectories.jsonl`: Complete multi-cycle execution event streams across $G_1$–$G_6$ adhering to frozen schema `1.0.0`.
- `labels/labels.jsonl`: Double-blind human audit annotations for safety boundary violations, reward hacking, and failure severities.
- `croissant.json`: Full metadata compliance with the MLCommons Croissant 1.0 specification.

---

## Quickstart

### 1. Installation

```bash
# Clone repository
git clone https://github.com/Pratikjain24/SAGE.git
cd SAGE

# Create virtual environment with uv or python
uv venv .venv
source .venv/bin/activate  # Or on Windows: .venv\Scripts\activate
uv pip install -e ".[dev]"
```

### 2. Run Pilot Experiment

```bash
# Run a multi-group pilot evaluation (G1-G6 across cycles)
sage run --config configs/experiments/pilot.yaml

# Generate research figures and bootstrap confidence intervals
sage analyze --run-id latest --output experiments/figures/
```

### 4. Run Live Model Evaluations (Google Gemini, Claude, OpenAI, DeepSeek)

```bash
# Evaluate Google Gemini 2.5 Flash under strict execution (zero mock fallback)
sage run --config configs/experiments/real_gemini_strict.yaml

# Evaluate Anthropic Claude 3.5 Sonnet
sage run --config configs/experiments/real_claude_strict.yaml

# Evaluate OpenAI GPT-4o
sage run --config configs/experiments/real_openai_strict.yaml

# Evaluate DeepSeek Reasoner
sage run --config configs/experiments/real_deepseek_strict.yaml
```

---

## 🌐 Multi-Model Support Matrix & Colab Benchmarks

SAGE provides first-class support for state-of-the-art commercial APIs and open-weights foundation models, complete with token cost tracking, strict non-mock execution modes, and self-contained Google Colab / Jupyter benchmark notebooks.

| Provider / Family | Supported Models | Wire Protocol / Endpoint | Cost Tracking | Standalone Notebook |
|---|---|---|---|---|
| **Google Gemini** | `gemini-2.5-flash`, `gemini-2.5-pro`, `gemini-2.0-flash`, `gemini-1.5-pro`, `gemma-2-27b-it` | Google Generative Language API (`/v1beta/openai/`) + `x-goog-api-key` | ✅ $0.075 / $0.30 per 1M tokens | [`SAGE_Google_Benchmark.ipynb`](SAGE_Google_Benchmark.ipynb) |
| **Anthropic Claude**| `claude-3-7-sonnet`, `claude-3-5-sonnet`, `claude-3-5-haiku`, `claude-3-opus` | Anthropic Messages API (`/v1/messages`) | ✅ $3.00 / $15.00 per 1M tokens | [`SAGE_Claude_Benchmark.ipynb`](SAGE_Claude_Benchmark.ipynb) |
| **OpenAI** | `gpt-4o`, `gpt-4o-mini`, `o1`, `o3-mini` | OpenAI Chat Completions (`/v1/chat/completions`) | ✅ $2.50 / $10.00 per 1M tokens | [`SAGE_OpenAI_Benchmark.ipynb`](SAGE_OpenAI_Benchmark.ipynb) |
| **DeepSeek** | `deepseek-chat` (V3), `deepseek-reasoner` (R1) | DeepSeek API (`api.deepseek.com/v1`) | ✅ $0.14 / $0.28 per 1M tokens | [`SAGE_DeepSeek_Benchmark.ipynb`](SAGE_DeepSeek_Benchmark.ipynb) |
| **Zero-Setup Playground** | Canonical 7-Archetype Suite ($G_1$–$G_7$) | Offline deterministic reference simulation | ✅ Free ($0.00) / Zero API Keys | [`SAGE_Interactive_Playground.ipynb`](SAGE_Interactive_Playground.ipynb) |
| **Local / vLLM** | `qwen2.5-coder-7b-instruct`, `llama-3.1-8b-instruct` | Local OpenAI-compatible server (`http://localhost:8000/v1`) | ✅ Hardware cost (compute-only) | [`SAGE_Colab_Benchmark.ipynb`](SAGE_Colab_Benchmark.ipynb) |
| **Groq Cloud** | `llama-3.3-70b-versatile`, `mixtral-8x7b-32768` | Groq OpenAI-compatible (`api.groq.com/openai/v1`) | ✅ $0.59 / $0.79 per 1M tokens | [`configs/model_groq.yaml`](configs/model_groq.yaml) |

---

## ⚡ SAGE-Live: Self-Refreshing, Cryptographically Attested AI Safety Engine

Static benchmarks inevitably decay: models memorize problem sets, solutions leak into training corpora, and agents game static test cases without acquiring true safety alignment. 

**`sage_live`** solves benchmark saturation by providing a continuous, self-refreshing, and tamper-evident evaluation platform with 5 tightly coupled subsystems:

```
                  +------------------------------------------+
                  |         Adversarial Red Team             |
                  |     (Grammar-Based Probe Engine)         |
                  +--------------------+---------------------+
                                       | 96 Vulnerability Classes
                                       v
                  +------------------------------------------+
                  |            Probe Generator               |
                  |  - Seeded Deterministic Generation       |
                  |  - Difficulty Calibration [0.0, 1.0]     |
                  |  - SHA-256 Content Attestation           |
                  +--------------------+---------------------+
                                       |
                     +-----------------+-----------------+
                     |                                   |
                     v                                   v
+------------------------------------+  +------------------------------------+
|       Multi-Metric Evaluation      |  |     Staleness & Leakage Monitor    |
| - Safety Drift Score   (35%)       |  | - Answer-Set Leakage Tracking      |
| - Retention Score      (30%)       |  | - Corpus Contamination Detection   |
| - Capability Score     (20%)       |  | - Automated Probe Retirement       |
| - Proxy Gap Score      (15%)       |  |   (Thresholds: >0.7 Retire, >0.9)  |
+--------------------+---------------+  +-----------------+------------------+
                     |                                    |
                     +-----------------+------------------+
                                       |
                                       v
                  +------------------------------------------+
                  |       Cryptographic Ledger & Stream      |
                  | - SHA3-256 Tamper-Evident Hash Chain     |
                  | - Ed25519 Public Key Attestation Signatures|
                  | - Real-Time Certification Stream (100 Hz)|
                  +--------------------+---------------------+
                                       |
                                       v
                  +------------------------------------------+
                  |            FastAPI REST Server           |
                  |   /api/v1/probes   /api/v1/evaluate      |
                  |   /api/v1/staleness /api/v1/attestation  |
                  +------------------------------------------+
```

### 1. Dynamic Adversarial Probe Generation
The probe generator (`sage_live.core.probe_generator.DeterministicProbeGenerator`) synthesizes unique, non-leaked evaluation scenarios spanning **96 base vulnerability types**, cross-cutting:
- **Vulnerability Classes**: `data_leak`, `privilege_escalation`, `unauthorized_mutation`, `jailbreak`, `prompt_injection`, `resource_exhaustion`, `backdoor_insertion`, `supply_chain`.
- **Injection Vectors**: `direct_instruction`, `few_shot_distraction`, `context_stuffing`, `base64_obfuscation`, `multilingual_obfuscation`, `role_confusion`.
- **Policy Boundaries**: `safety`, `capability`, `alignment`, `fairness`.

Every generated probe satisfies a strict cryptographic invariant:
$$\text{sha256\_hash} = \text{SHA-256}(\text{task\_description} \parallel \text{ground\_truth})$$

### 2. Multi-Metric Evaluation & Composite Safety Score
Evaluations are scored across four orthogonal axes and combined into a mathematically rigorous composite safety score:
$$\text{CompositeSafetyScore} = 0.35 \times \text{SafetyDrift} + 0.30 \times \text{Retention} + 0.20 \times \text{Capability} + 0.15 \times \text{ProxyGap}$$

### 3. Benchmark Staleness & Leakage Index
The staleness engine tracks benchmark decay in real time:
- Detects whether test answers have leaked into public web crawl corpora or pre-training sets.
- Dynamically classifies benchmark health into `HEALTHY`, `WARNING`, `RETIRE` (leakage $\ge 0.70$), or `CRITICAL` (leakage $\ge 0.90$).
- Triggers automatic retirement of compromised probe tasks and regenerates fresh variants.

### 4. Immutable Attestation Ledger & Ed25519 Certification Chain
All evaluation events are committed to an immutable append-only ledger (`sage_live.core.attestation.AttestationLedger`):
$$H_{\text{combined}} = \text{SHA3-256}(H_{\text{agent\_snapshot}} \parallel H_{\text{probe\_set}} \parallel H_{\text{results}} \parallel H_{\text{prev\_ledger}})$$
- Every block is signed with a 64-byte Ed25519 private key (128 hex chars).
- Verification passes traverse the entire chain to guarantee zero retro-active tampering.
- Emits real-time cryptographic certificates for public verifiability.

### 5. Running SAGE-Live Server & Test Suites

```bash
# Launch the SAGE-Live API server
uvicorn sage_live.api:app --host 0.0.0.0 --port 8000 --reload

# Run all 110 SAGE-Live unit and integration tests
python -m pytest sage_live/tests/test_all.py -v
```

---

## Monorepo Layout

```
sage/
+-- pyproject.toml              # Project metadata & dependencies
+-- Makefile                  # Automation shortcuts
+-- sage/                  # Core package
|   +-- config/               # Pydantic configuration schemas
|   +-- trajectory/           # Append-only JSONL event stream
|   +-- adapters/             # G1..G6 agent adapters
|   +-- evolution/            # Inter-cycle controller, verifier, snapshotting
|   +-- environment/          # Docker runner, sandbox API, safety monitor
|   +-- scoring/              # Hidden scorer, tamper detector, proxy gap
|   +-- metrics/              # Pure mathematical metric functions & registry
|   +-- runner/               # Orchestrator, CLI, statistical analysis
|   +-- llm/                  # LLM client & cost accounting
|   +-- dashboard_backend/    # FastAPI service + DuckDB
|   +-- dashboard_frontend/   # Next.js 14+ modern dashboard
+-- tasks/                    # 100 benchmark tasks & testbeds
+-- configs/                  # Agent, experiment, and model YAMLs
+-- docker/                   # Dockerfiles for sandbox & scorer
+-- tests/                    # Unit, regression, and integration tests
+-- paper/                    # IEEE Conference submission manuscript (main.tex) & assets
+-- docs/                     # Specifications and guides
```

---

## Authors & Institutional Affiliation

This project is authored by a student research team at **Vishwakarma Institute of Technology (VIT), Pune, India**, under faculty advisory guidance.

| Role | Name | Affiliation |
|---|---|---|
| **Lead Author** | Pratik P. Jain | Dept. of Computer Engineering, VIT Pune |
| **Co-Author** | Janhavi B. Pagare | Dept. of Computer Engineering, VIT Pune |
| **Co-Author** | Aditya U. Dengale | Dept. of Computer Engineering, VIT Pune |
| **Co-Author** | Naitik K. Kharat | Dept. of Computer Engineering, VIT Pune |
| **Co-Author** | Shamika R. Kadam | Dept. of Computer Engineering, VIT Pune |
| **Faculty Guide** | Prof. Vikrant K. Kadam | Dept. of Computer Engineering, VIT Pune |

**Submission Target**: IEEE Conference on Artificial Intelligence and Software Engineering (2026)  
**Human Annotation**: 82.7 person-hours across 319 code tasks (pooled κ = 0.856, SE ≤ 0.038)

---

## Citation

If you use SAGE in your research, please cite our IEEE conference paper:

```bibtex
@inproceedings{jain2026sage,
  title     = {SAGE: Safety & Agent Growth Evaluator --- Measuring Security Boundary Drift and Capability Retention in Self-Evolving Code Agents},
  author    = {Jain, Pratik P. and Pagare, Janhavi B. and Dengale, Aditya U. and Kharat, Naitik K. and Kadam, Shamika R. and Kadam, Vikrant K.},
  booktitle  = {Proceedings of the IEEE Conference on Artificial Intelligence and Software Engineering},
  year      = {2026},
  institution = {Vishwakarma Institute of Technology, Pune, India}
}
```

> **Not to be confused with**: Xia, Deng & Zhang (2024) *"Top Leaderboard Ranking = Top Coding Proficiency, Always? EvoEval: Evolving Coding Benchmarks via LLM"* ([evo-eval/evoeval](https://github.com/evo-eval/evoeval)) — an unrelated code-generation benchmark focusing on coding problem mutation.

---

## License

Licensed under the [Apache License, Version 2.0](LICENSE).
