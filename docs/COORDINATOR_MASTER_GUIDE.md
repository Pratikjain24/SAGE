# SAGE Distributed Study: Coordinator Master Operational Guide

This document defines the operational protocol, verification procedures, and replication synthesis workflows for the SAGE Distributed Empirical Study across Kaggle Tesla T4 GPU nodes.

---

## 1. Study Topology & Role Allocation

The empirical benchmark distributes the evaluation of 7 agent evolution archetypes across 7 independent Kaggle contributor environments ($P_1$ through $P_7$) running unsloth/vLLM inference on `Qwen/Qwen2.5-Coder-7B-Instruct` (Pinned revision `c03e6d358207e414f1eca0bb1891e29f1db0e242`).

| Contributor | Assigned Layer | Notebook | Primary Scope | Cryptographic Cross-Check |
| :--- | :--- | :--- | :--- | :--- |
| **P1** | **G1 Static Baseline** | `P1_G1_Static_Kaggle.ipynb` | Baseline control across 5 seeds | Establishes G1 ground truth |
| **P2** | **G2 Prompt Rewriter** | `P2_G2_PromptRewriter_Kaggle.ipynb` | Evolutionary metaprompt mutation | Zero-mock provenance audit |
| **P3** | **G3 Memory Accumulator** | `P3_G3_MemoryAccumulator_Kaggle.ipynb` | Epistemic memory accumulation | Buffer isolation per seed |
| **P4** | **G4 Reflection Agent** | `P4_G4_Reflection_Kaggle.ipynb` | Self-reflection drift loop | Assertion bypass capture |
| **P5** | **G5 Verified Agent** | `P5_G5_Verified_Kaggle.ipynb` | Static AST invariant quarantine | AST sandbox enforcement |
| **P6** | **G6 Proxy Canary Guard** | `P6_G6_ProxyCanaryGuard_Kaggle.ipynb` | Production canary gating | Automated rollback trigger |
| **P7** | **G7 Oracle Skyline** | `P7_G7_OracleSkyline_CrossCheck_Kaggle.ipynb` | Upper-bound oracle verification | **Replicates P1 G1 (Cross-Check)** |

---

## 2. Ingestion & Provenance Audit Protocol

When contributors complete their assignments, they submit an encrypted ZIP bundle structured as:
```text
<GROUP>_seeds42-46_submission.zip
├── notes.txt
├── state/
│   ├── done_<GROUP>_42
│   └── ...
└── runs/
    ├── study_live_distributed_<GROUP>_s42/
    │   ├── trajectory.jsonl
    │   └── trajectory_manifest.json
    └── ...
```

### Audit Verification Command
The coordinator must audit every submission package prior to merging using `scripts/verify_distributed_submissions.py`:

```bash
# Verify all contributor packages in the intake directory
python scripts/verify_distributed_submissions.py \
  --submissions-dir ./intake/ \
  --strict-tasks 100 \
  --expected-model "Qwen/Qwen2.5-Coder-7B-Instruct" \
  --json-out ./intake_audit_report.json
```

### Strict Rejection Criteria (Automatic Disqualification)
A submission package is rejected if:
1. **Mock Fallback Detected**: Any event in `trajectory.jsonl` has `is_fallback: true`.
2. **Zero-Token Invocation**: Any task invocation records `tokens_in + tokens_out == 0`.
3. **Model Tampering**: `model_name` recorded in trajectory events deviates from `Qwen/Qwen2.5-Coder-7B-Instruct`.
4. **Digest Mismatch**: The SHA-256 hash of `trajectory.jsonl` does not match `raw_sha256` recorded in `trajectory_manifest.json`.
5. **Seed Incompleteness**: Trajectories do not cover all 5 designated seeds: `[42, 43, 44, 45, 46]`.

---

## 3. Merging & Inter-Hardware Cross-Check Execution

Once all 7 contributor packages pass verification, synthesize them into the canonical dataset:

```bash
python scripts/merge_distributed_runs.py \
  --submissions-dir ./intake/ \
  --output-dir experiments/runs/study_live_distributed_merged \
  --cross-check-tol 0.025 \
  --attestation-db experiments/attestation.db
```

### Inter-Hardware Replication Invariance
The merger script compares the baseline solve rate of $G_1$ executed on Contributor 1's Kaggle instance ($PassRate_{P1}$) against the replication $G_1$ executed on Contributor 7's distinct physical instance ($PassRate_{P7}$):

$$\Delta_{\text{hardware}} = \left| \text{PassRate}_{P1} - \text{PassRate}_{P7} \right| \le 2.5\%$$

If $\Delta_{\text{hardware}} > 2.5\%$, the coordinator halts the pipeline and inspects GPU microarchitecture differences, vLLM CUDA kernel versions, and thermal throttling records.

---

## 4. Cryptographic Sealing & Attestation

The merger automatically registers each evaluation window into the hash-chained `experiments/attestation.db` using HMAC-SHA256 signatures:
1. Every evaluation window generates an `AttestationBlock`.
2. The block computes `current_hash = SHA256(payload + previous_hash)`.
3. SQL triggers `prevent_attestation_block_update` and `prevent_attestation_block_delete` guarantee database-level write-once immutability.
4. Ledger integrity is verified via `ledger.verify_chain_integrity()`.

---

## 5. Post-Merge Dashboard & Rebuttal Synchronization

After merging:
1. Copy the merged run to the active dashboard root:
   ```bash
   cp -r experiments/runs/study_live_distributed_merged experiments/runs/study_live_canonical
   ```
2. Render updated publication figures:
   ```bash
   python scripts/render_paper_figures.py
   python scripts/render_dashboard_figures.py
   ```
3. Launch dashboard backend & frontend to inspect live telemetry:
   ```bash
   uvicorn sage.dashboard_backend.main:app --port 8000 &
   cd sage/dashboard_frontend && npm run dev
   ```
