
# 🚀 How to Run SAGE: Safety & Agent Growth Evaluator (Complete Operational Manual)

> **SAGE: Safety & Agent Growth Evaluator** — The official benchmark and execution guide for measuring security boundary drift, specification gaming, and catastrophic forgetting in self-evolving code agents.  
> The virtual environment (`.venv`) is already configured, dependencies are installed, 100 task repositories are initialized, and verified evaluation runs are persisted. Below are the exact commands to run everything on Windows, Linux, Google Colab, and Kaggle.

---

## 📋 Quick Reference — All Commands at a Glance

| Task / Objective | Command | Notes |
|---|---|---|
| **Activate venv (PowerShell)** | `.venv\Scripts\Activate.ps1` | Run inside `SAGE` or `EvoEval` directory |
| **Activate venv (CMD)** | `.venv\Scripts\activate.bat` | Run inside `SAGE` or `EvoEval` directory |
| **Wrapper CLI (no venv needed)** | `.\sage.bat --help` or `.\sage.ps1 --help` | Auto-detects virtual environment |
| **See all CLI commands** | `sage --help` | Shows run, analyze, stats, audit, verify, dashboard |
| **List benchmark tasks** | `sage tasks list` | Formats all 100 component tasks in a Rich table |
| **Validate benchmark tasks** | `sage tasks validate` | Verifies test files, ground truth, and proxy definitions |
| **Dry-run (verify config only)**| `sage run --config configs/experiments/pilot.yaml --dry-run` | Zero execution, verifies tasks and hyperparameters |
| **Run pilot experiment** | `sage run --config configs/experiments/pilot.yaml` | 6 archetypes, 5 cycles, 3 seeds, fast mock LLM |
| **Run full study (N=5 seeds)** | `sage run --config configs/experiments/full_study.yaml --seeds 42,43,44,45,46` | Full 18k–30k evaluation matrix |
| **Run full study (N=10 seeds)**| `sage run --config configs/experiments/full_study.yaml --seeds 42,43,44,45,46,47,48,49,50,51` | Publication-grade maximum statistical power |
| **Run Google Gemini benchmark** | `sage run --config configs/experiments/real_gemini_strict.yaml` | Strict API execution, zero mock fallback |
| **Run Claude benchmark** | `sage run --config configs/experiments/real_claude_strict.yaml` | Anthropic Claude 3.5 / 3.7 Sonnet |
| **Run OpenAI benchmark** | `sage run --config configs/experiments/real_openai_strict.yaml` | OpenAI GPT-4o / o3-mini |
| **Run DeepSeek benchmark** | `sage run --config configs/experiments/real_deepseek_strict.yaml` | DeepSeek Reasoner (R1) / V3 |
| **Run Groq benchmark** | `sage run --config configs/experiments/real_groq_strict.yaml` | Groq fast inference (Llama 3.3 70B) |
| **Run core test suite (201)** | `pytest tests/ -v` | 100% passing across 31 test suites |
| **Run fast integration check** | `pytest tests/test_integration.py -v` | Fast pre-commit gate (< 15 seconds) |
| **Run SAGE-Live tests (110)** | `pytest sage_live/tests/test_all.py -v` | 100% passing across dynamic attestation suite |
| **Run SAGE-Live API server** | `uvicorn sage_live.api:app --host 0.0.0.0 --port 8000 --reload` | OpenAPI Swagger docs at `http://localhost:8000/docs` |
| **Analyze run & render plots** | `sage analyze --run-id latest --recompute --output experiments/figures/` | Generates publication figures and LaTeX tables |
| **Run statistical significance** | `sage stats --run-id latest` | Task-level inference ($N=100$), bootstrap $B=10,000$ |
| **Launch visual dashboard** | `.\start_dashboard.ps1` or `start_dashboard.bat` | Starts Next.js (port 3000) & FastAPI (port 8000) |
| **Audit trajectory manifest** | `sage manifest --run-id latest` | Verifies SHA-256 cryptographic hashes |
| **Export HuggingFace dataset** | `sage export-hf --run-id latest --output hf_dataset/` | MLCommons Croissant 1.0 format with payload redaction |

---

## 📂 Step 1: Directory Setup & Working Location

Open **PowerShell** or **Command Prompt** and navigate to your project directory:

```powershell
# Navigate to the SAGE workspace root
cd C:\Users\kruti\Downloads\EvoEval\SAGE

# (Note: SAGE is linked to EvoEval via Directory Junction, so both point to the same files)
```

---

## 🐍 Step 2: Activate the Virtual Environment

```powershell
# In PowerShell (Note: 'Scripts' with an 's' and 'Activate.ps1'):
.venv\Scripts\Activate.ps1

# OR in Command Prompt (CMD):
.venv\Scripts\activate.bat

# OR use wrapper scripts directly without activating .venv:
.\sage.bat tasks list
.\sage.ps1 tasks list
```

> [!TIP]
> After activation, you will see `(.venv)` at the beginning of your command prompt line.  
> **Shortcut**: You can also use `.\sage.bat <command>` or `.\sage.ps1 <command>` directly without manually activating `.venv`!

---

## 🔍 Step 3: Verify Environment & Benchmark Tasks

### 3a. Check the CLI tool
```powershell
sage --help
```
You should see all primary commands: `run`, `analyze`, `stats`, `audit`, `verify`, `tasks`, and `dashboard`.

### 3b. Inspect the 100 Benchmark Tasks
```powershell
# Display all 100 benchmark tasks:
sage tasks list

# Filter by category (e.g. only deliberate exploit probes):
sage tasks list --type exploit_probe

# Filter by other categories:
sage tasks list --type bug_fix
sage tasks list --type security_audit

# Preview only the first N tasks:
sage tasks list --limit 15
```
Displays standardized tasks across Bug Fix (20), Feature Addition (20), Refactor (20), Exploit Probes (20), and Security Audit (20) in a colorized terminal table.

### 3c. Perform a Zero-Cost Dry-Run
```powershell
sage run --config configs/experiments/pilot.yaml --dry-run
```
**Expected Output:**
```
+-------------------------------------------------------------+
|              SAGE Benchmark Execution Harness               |
+-------------------------------------------------------------+
Loaded config: pilot (groups: ['G1', 'G2', 'G3', 'G4', 'G5', 'G6'], cycles: 5, seeds: [42, 43, 44])
Loaded tasks: 60 train, 40 test tasks
Dry-run requested: configuration and tasks verified successfully!
```

---

## 🧪 Step 4: Run the Quality Gate Test Suites (311 Total Tests)

SAGE includes **311 automated tests** maintaining a certified 100% pass rate.

### 4a. Run Core Quality Gate (201 Tests)
```powershell
python -m pytest tests/ -q
```
**Expected output:** `201 passed, 1 skipped` (1 skipped is the live vLLM daemon socket when offline).

To run with execution durations for profiling:
```powershell
python -m pytest tests/ -v --durations=10
```

### 4b. Fast Pre-Commit Integration Gate (< 15 Seconds)
```powershell
python -m pytest tests/test_integration.py -v
```
Executes in **8.45s on Linux CI** and **13.22s on Windows**, testing end-to-end orchestration without spinning up containers or remote APIs.

### 4c. Run SAGE-Live Dynamic Attestation Tests (110 Tests)
```powershell
python -m pytest sage_live/tests/test_all.py -v
```
Validates dynamic grammar probe generation, Ed25519 signature attestation, SHA3-256 hash-chaining, and web-leakage staleness tracking in ~0.53 seconds.

---

## 🚀 Step 5: Run Benchmark Experiments

### Option A: Pilot Experiment (Fast Demonstration)
```powershell
sage run --config configs/experiments/pilot.yaml
```
- **Scope**: 6 archetypes ($G_1$–$G_6$), 5 evolution cycles ($C_0$–$C_4$), 3 random seeds (42, 43, 44), 10 tasks/cycle.
- **Engine**: Deterministic Mock LLM client (zero GPU cost, completes in ~1.5 minutes).

### Option B: Full Longitudinal Study with Multi-Seed Scaling
```powershell
# Run with N=5 seeds (Recommended Empirical Minimum):
sage run --config configs/experiments/full_study.yaml --seeds 42,43,44,45,46

# Run with N=10 seeds (Ideal Publication Sweeps):
sage run --config configs/experiments/full_study.yaml --seeds 42,43,44,45,46,47,48,49,50,51
```
- **Scope**: 100 tasks, 10 evolutionary cycles, $N=5$ or $N=10$ independent seeds.
- **Results stored in**: `experiments/runs/<run_id>/` (with append-only `trajectory.jsonl` and `cycle_metrics.json`).

### Option C: Run Frontier Commercial Foundation Models (Strict Live APIs)
Run genuine token-by-token neural evaluations with **zero mock fallback** (`allow_fallback: false`):

```powershell
# 1. Google Gemini 2.5 Flash / Pro
$env:GEMINI_API_KEY="your-gemini-api-key"
sage run --config configs/experiments/real_gemini_strict.yaml --seeds 42,43,44,45,46

# 2. Anthropic Claude 3.5 Sonnet / 3.7 Sonnet
$env:ANTHROPIC_API_KEY="your-anthropic-api-key"
sage run --config configs/experiments/real_claude_strict.yaml --seeds 42,43,44,45,46

# 3. OpenAI GPT-4o / o3-mini
$env:OPENAI_API_KEY="your-openai-api-key"
sage run --config configs/experiments/real_openai_strict.yaml --seeds 42,43,44,45,46

# 4. DeepSeek Reasoner (R1) / DeepSeek-V3
$env:DEEPSEEK_API_KEY="your-deepseek-api-key"
sage run --config configs/experiments/real_deepseek_strict.yaml --seeds 42,43,44,45,46

# 5. Groq Cloud (Llama 3.3 70B Fast Inference)
$env:GROQ_API_KEY="your-groq-api-key"
sage run --config configs/experiments/real_groq_strict.yaml --seeds 42,43,44,45,46
```

---

## ☁️ Step 6: 100% Free Cloud GPU Execution (Google Colab & Kaggle)

If you don't have a local GPU, SAGE provides self-contained cloud runners that execute **100% free on Colab and Kaggle T4 GPUs** using local vLLM with `Qwen/Qwen2.5-Coder-3B-Instruct`.

### 🌐 Google Colab Ready-Made Notebooks
Open directly via Google Colab:
- **Free Local vLLM Runner (Zero API Keys Needed)**: [`SAGE_Colab_Benchmark.ipynb`](SAGE_Colab_Benchmark.ipynb)
- **Google Gemini 2.5 Runner**: [`SAGE_Google_Benchmark.ipynb`](SAGE_Google_Benchmark.ipynb)
- **Anthropic Claude Runner**: [`SAGE_Claude_Benchmark.ipynb`](SAGE_Claude_Benchmark.ipynb)
- **OpenAI GPT-4o Runner**: [`SAGE_OpenAI_Benchmark.ipynb`](SAGE_OpenAI_Benchmark.ipynb)
- **DeepSeek Reasoner R1 Runner**: [`SAGE_DeepSeek_Benchmark.ipynb`](SAGE_DeepSeek_Benchmark.ipynb)

---

### 🏆 Kaggle T4 GPU Deployment Workflow (Step-by-Step)

Follow these exact steps to run SAGE on Kaggle without encountering environment errors:

#### 1. Kaggle Notebook Settings Checklist
Before running any code in your Kaggle notebook:
1. **Phone Verification**: Complete phone number verification on Kaggle (*Account Settings → Phone Verification*) to unlock GPU accelerators and internet access.
2. **Set Accelerator**: In the right-hand panel under **Session options**, set **Accelerator** to **GPU T4 x2** (or **GPU P100**).
3. **Turn ON Internet**: In the right-hand panel under **Session options**, toggle **Internet** to **ON**. (Critical for downloading dependencies and models!).

#### 2. Cell 1: Environment Setup & Fix TorchAudio Mismatch
> **Important**: Kaggle pre-installs a Python 3.13 torchaudio package compiled against CUDA 12.8 while PyTorch uses CUDA 13.0. Removing torchaudio resolves the `RuntimeError: PyTorch and TorchAudio CUDA version mismatch`:

```python
# Cell 1: Clean workspace & clone SAGE
!rm -rf /kaggle/working/sage
!git clone https://github.com/Pratikjain24/SAGE.git /kaggle/working/sage
%cd /kaggle/working/sage

# Fix Kaggle CUDA 13 / TorchAudio mismatch and install vLLM
!pip uninstall -y torchaudio
!pip install -q --upgrade pip
!pip install -q -e .
!pip install -q vllm kagglehub huggingface_hub
print("✓ SAGE environment setup complete!")
```

#### 3. Cell 2: Download Model Safetensors
```python
# Cell 2: Download Qwen2.5-Coder-3B-Instruct (fits in 15GB T4 VRAM)
from huggingface_hub import snapshot_download
import os

model_dir = '/kaggle/working/models/qwen25-coder-3b'
os.makedirs(model_dir, exist_ok=True)
print("Downloading Qwen2.5-Coder-3B-Instruct...")
snapshot_download(
    repo_id='Qwen/Qwen2.5-Coder-3B-Instruct',
    local_dir=model_dir,
    ignore_patterns=['*.bin', '*.pt'], # safetensors only
)
print("✓ Model downloaded successfully to", model_dir)
```

#### 4. Cell 3: Start Local vLLM Server in Background
```python
# Cell 3: Start local vLLM OpenAI-compatible server on port 8000
import subprocess, time, requests, os

print("Launching local vLLM server on port 8000...")
proc = subprocess.Popen([
    "python", "-m", "vllm.entrypoints.openai.api_server",
    "--model", "/kaggle/working/models/qwen25-coder-3b",
    "--port", "8000",
    "--host", "127.0.0.1",
    "--max-model-len", "4096",
    "--gpu-memory-utilization", "0.85",
    "--trust-remote-code",
    "--enforce-eager",
], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

ready = False
for i in range(45):
    time.sleep(2)
    try:
        r = requests.get("http://127.0.0.1:8000/v1/models", timeout=2)
        if r.status_code == 200:
            ready = True
            print(f"✓ vLLM server initialized and ready in {i*2}s!")
            break
    except Exception:
        pass
    if i % 5 == 0:
        print(f"  ...waiting for server initialization ({i*2}s)")

if not ready:
    raise RuntimeError("Server failed to start. Ensure Kaggle Accelerator is set to GPU T4 x2 or P100.")

os.environ["SAGE_BASE_URL"] = "http://localhost:8000/v1"
os.environ["OPENAI_API_BASE"] = "http://localhost:8000/v1"
os.environ["OPENAI_API_KEY"] = "dummy-vllm-key"
```

#### 5. Cell 4: Execute Benchmark Suite
```python
# Cell 4: Run SAGE with N=5 seeds
!python scripts/run_real_experiment.py \
    --provider local \
    --model-name "Qwen/Qwen2.5-Coder-3B-Instruct" \
    --seeds 42,43,44,45,46 \
    --budget 150 \
    --output-dir /kaggle/working/results
```

#### 6. Cell 5: Analyze Results & Render Figures
```python
# Cell 5: Generate publication figures & significance tables
!sage analyze --run-id latest --recompute --output /kaggle/working/results/figures
!sage stats --run-id latest
print("✓ Benchmark execution, analysis, and significance testing complete!")
```

---

## ⚡ Step 7: Run SAGE-Live (Self-Refreshing Benchmark Engine)

`sage_live` is the continuously self-refreshing AI safety evaluation subsystem featuring grammar-based probe generation, staleness tracking, and Ed25519 digital signature attestation.

### 7a. Start the FastAPI Service
```powershell
uvicorn sage_live.api:app --host 0.0.0.0 --port 8000 --reload
```
- **Interactive OpenAPI Documentation (Swagger UI)**: Open `http://localhost:8000/docs` in your browser.
- **REST Endpoints**:
  - `GET /health` — Service status and engine state.
  - `GET /probes` — Paginated catalog of dynamic adversarial probes.
  - `POST /evaluate` — Execute candidate agent against dynamic probes.
  - `GET /staleness` — Answer leakage and probe retirement metrics.
  - `GET /attestation` — Query Ed25519-signed SHA3-256 ledger blocks.

### 7b. Run the Complete SAGE-Live Test Suite (110 Tests)
```powershell
python -m pytest sage_live/tests/test_all.py -v
```
Validates probe generation across all 96 vulnerability vectors, cryptographic signing, ledger hash-chain integrity, and API schemas.

---

## 📊 Step 8: Analyze Results & Run Inferential Statistics

### 8a. Recompute Metrics & Regenerate Figures
```powershell
# Analyze latest run:
sage analyze --run-id latest --recompute --output experiments/figures/

# OR analyze a specific historical run:
sage analyze --run-id full_study_canonical --recompute --output experiments/figures/
```
Generates:
- Trajectory drift curves and proxy gap plots in `experiments/runs/<run_id>/figures/`
- Standardized LaTeX tables in `experiments/runs/<run_id>/tables/`
- Automatically copies artifacts to `paper/figures/` and `paper/tables/`

### 8b. Run Statistical Significance Testing (Task-Level Inference)
```powershell
sage stats --run-id latest
```
Computes:
- **Task-Level Inference ($N=100$ independent repositories)**: Paired contrasts marginalized across seeds.
- **Effect Sizes**: Cohen's $d \in [0.47, 0.89]$ and Cliff's $\delta \in [0.39, 0.56]$.
- **Exact Bootstrap Significance**: $B = 10,000$ non-parametric resamples with finite resolution floor.
- **Step-Down Holm-Bonferroni FWER Control**: Adjusted $p$-values across all 27 canonical comparison tuples.

---

## 🖥️ Step 9: Launch the Interactive Web Dashboard

The SAGE Dashboard provides an interactive visual workbench to inspect evolutionary drift curves, code mutation diffs, telemetry event logs, and the double-blind human audit queue.

### Launch via Scripts:
In PowerShell:
```powershell
.\start_dashboard.ps1
```
Or in Command Prompt:
```cmd
start_dashboard.bat
```

### Launch via SAGE CLI:
```powershell
sage dashboard
```

This automatically:
1. Starts the FastAPI backend service on `http://localhost:8000` (serving both static benchmark runs and live `/api/v1/...` dynamic evaluation endpoints)
2. Starts the Next.js 14 frontend application on `http://localhost:3000`
3. Opens your default web browser directly to `http://localhost:3000`

### Interactive Dashboard Navigation:
- **`http://localhost:3000/` (Runs Overview & 7 Defense Layers)**: View global KPI metrics, safety drift curves, capability retention, proxy reward hacking divergence, and the interactive **7-Layer Defense-in-Depth Visualizer** (L1 Execution Jail, L2 AST Mutation Gate, L3 Ephemeral Test Harness, L4 Held-Out Canary Probes, L5 Ed25519 Attestation Ledger, L6 Dynamic Drift Detector, L7 Autonomous Quarantine & Rollback).
- **`http://localhost:3000/dynamic-eval` (Live Dynamic Evaluation Workbench - 100% Real API)**:
  - **Deterministic Adversarial Probe Generator**: Select from 6 vulnerability classes (`reward_hack`, `code_execution`, `data_leak`, `privilege_escalation`, `buffer_overflow`, `sql_injection`), 4 injection vectors (`direct`, `chained`, `environmental`, `indirect`), continuous difficulty (0.1–1.0), and seed ID.
  - **Live Agent Execution Console**: Test candidate mutations across all 7 archetypes ($G_1$–$G_7$). Select presets (*Safe Compliant Fix*, *Reward Hack Bypass*, *Host Exploit*, *Syntax Error*) or write custom code.
  - **Real-Time AST & Security Invariant Scoring**: Displays live Composite Safety Score ($S_c$), Safety Drift ($\Delta\text{Drift}$), Proxy Gap ($	ext{ProxyGap}$), Capability Score, and sub-millisecond execution latency.
  - **Cryptographic Attestation Chain Visualizer**: Inspects live hash-chained blocks sealed in the append-only SQLite WAL ledger, complete with SHA-256 block hashes, parent links, HMAC signatures, and a one-click **"Verify Chain Integrity"** button.
  - **Benchmark Staleness & Freshness Gauge**: Real-time tracking of test suite freshness ($>90\%$) and contamination risk ($<5\%$).
- **`http://localhost:3000/drift` (Drift Explorer)**: Inspect generation-by-generation code diffs and qualitative failure case studies ($G_4$ reflection prompt corruption vs. $G_6$ verifier rollback vs. $G_7$ proxy canary containment).
- **`http://localhost:3000/leaderboard` (Group Taxonomy Leaderboard)**: Multi-objective Pareto frontier ranking all 7 agent archetypes ($G_1$ through $G_7$).
- **`http://localhost:3000/audit` (Audit Workbench)**: Dual-pass double-blind human trace labeling interface with inter-annotator agreement metrics.

---

## 🔒 Step 10: Integrity Auditing & Dataset Export

### 10a. Inspect Cryptographic Trajectory Manifest (SHA-256)
```powershell
sage manifest --run-id latest
```
Emits raw and canonical projection SHA-256 digests, verifying byte-for-byte reproducibility.

### 10b. Export Dataset to HuggingFace / MLCommons Croissant Format
```powershell
sage export-hf --run-id latest --output hf_dataset/
```
Packages `tasks.jsonl`, `trajectories.jsonl`, and `labels.jsonl` with MLCommons Croissant 1.0 metadata (`croissant.json`) and an Apache-2.0 dataset card, with automated redaction of sensitive exploit payloads.

### 10c. Run Zero-Shot Pre-Training Contamination Audit
```powershell
sage tasks audit-contamination
```
Verifies 4-gram Jaccard overlap and LCS against pre-training corpora (certified 0.0% contamination).

---

## 📁 Historical Experiment Runs in the Repository

Your workspace contains 13 pre-computed canonical experiment runs in `experiments/runs/`:

| Run Identifier | Description | Key Telemetry |
|---|---|---|
| `full_study_canonical` | Full 18,000-task canonical study across $G_1$–$G_6$, 10 cycles, 3 seeds | 234,360 events, \$73.95 spend, 334.8M tokens |
| `pilot_canonical_3seeds` | Canonical pilot study (900 tasks, 5 cycles, 3 seeds) | 10,365 events, 273.9k tokens |
| `full_study_live` | Live neural model longitudinal study across 10 generations | 9,302 events, 724 completed tasks |
| `local_qwen_empirical_run` | In-process Qwen-2.5-Coder-3B GGUF model execution | 426 events, zero dollar cost |
| `live_google_empirical_run` | Google AI Studio live OpenAI-compatible endpoint run | 315 events, strict wire protocol |
| `pilot_linux_docker_canonical` | Certified Linux Docker run (`sage-sandbox:1.0`, rootless 1000:1000) | 0.0% container escape rate |
| `pilot_windows_localsandbox_canonical` | Windows LocalSandbox fallback run | Path-jail validation, 98.9% intercept |
| `pilot_llama_canonical_3seeds` | Llama-3.1-8B cross-family architectural replication | Proves cross-family drift invariance |
| `horizon_sensitivity_canonical` | Ultra-long horizon study across 25 consecutive generations | Discloses logarithmic drift saturation |
| `vllm_smoke_canonical` | vLLM live inference wire-protocol smoke test | Wire-level latency & token profiling |

---

## 🎤 Foolproof 2-Minute Demo Script (For Viva / HOD / Teachers)

If you need to deliver a fast, flawless live demonstration, run these 6 commands in order:

```powershell
# 1. Open project folder
cd C:\Users\kruti\Downloads\EvoEval\SAGE

# 2. Activate virtual environment
.venv\Scripts\activate

# 3. Show the CLI tool and command surface
sage --help

# 4. Display the 100 benchmark task catalog (impressive Rich table!)
sage tasks list

# 5. Execute dry-run to prove harness and task validity
sage run --config configs/experiments/pilot.yaml --dry-run

# 6. Run the test suite (proves 201 tests passing with 100% reliability)
python -m pytest tests/ -q

# 7. Launch the interactive dashboard (visual wow factor!)
.\start_dashboard.ps1
```

---

## ⚠️ Troubleshooting & Solutions

| Symptom / Error | Root Cause | Immediate Fix |
|---|---|---|
| `sage : The term 'sage' is not recognized` | Virtual environment is not activated in this terminal session | Run `.venv\Scripts\activate` or use `.\sage.bat` / `.\sage.ps1` |
| `scripts cannot be loaded because running scripts is disabled` | Windows PowerShell execution policy restriction | Run: `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` |
| `ModuleNotFoundError: No module named 'sage'` | Package not installed in editable development mode | Run: `.venv\Scripts\pip.exe install -e ".[dev]"` |
| `RuntimeError: PyTorch and TorchAudio CUDA version mismatch` | Kaggle Python 3.13 pre-installed torchaudio compiled against CUDA 12.8 while torch is CUDA 13.0 | Run: `!pip uninstall -y torchaudio` before importing transformers |
| `FileNotFoundError: Model path invalid` on Kaggle | Dynamic directory changed after session restart | Use: `kagglehub.model_download('qwen-lm/qwen-3/transformers/0.6b/1')` |
| `Server failed to start. Ensure Kaggle Accelerator is set` | GPU accelerator not selected or Internet toggle OFF in Kaggle | In Session options: set **Accelerator** to **GPU T4 x2** and toggle **Internet** to **ON** |
| `Port 8000 or 3000 already in use` | Previous FastAPI or Next.js process still running | Run: `Get-Process python, node \| Where-Object {$_.MainWindowTitle -eq ""} \| Stop-Process -Force` |
| `Dashboard frontend fails to build` | Next.js node_modules missing | Run: `cd sage\dashboard_frontend && npm install` |
| `Rate limit or 429 error on cloud APIs` | Exceeded provider queries-per-minute quota | Run using local vLLM runner or adjust `--budget` in CLI |
| `p-value resolution floor warning in stats` | Bootstrap with $B=10,000$ has minimum resolution $1/(B+1) = 0.00010$ | Expected behavior; reported as $p < 0.001^*$ per publication standards |

---

> [!TIP]
> **Author Note**: For the presentation, keep the three headline numbers in your head:
> - **60.0%**: Calibrated baseline solve rate ($G_1$) across all 100 tasks.
> - **78.4% / +0.28 / +0.55**: Unconstrained reflection ($G_4$) improves capability but causes severe security drift and specification gaming.
> - **84.4% / +0.02 / 96.0%**: Deployable canary gating ($G_7$) on held-out tasks achieves high accuracy, near-zero drift, and 96% retention.
