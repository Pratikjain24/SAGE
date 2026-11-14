# SAGE Kaggle Distributed Study: Extracted & Organized Artifacts

**Dataset**: SAGE Live Multi-Node Empirical Benchmark  
**Hardware Platform**: Kaggle Dual Tesla T4 GPUs (7 Independent Contributor Nodes)  
**Model**: `Qwen/Qwen2.5-Coder-7B-Instruct` (`c03e6d358207e414f1eca0bb1891e29f1db0e242`)  
**Generated Date**: November 12, 2026  
**Total Contributor Packages**: 7 (G1 to G7)  
**Total Canonical Runs**: 36 (5 seeds each + 1 cross-check replication)  
**Total Validated Task Episodes**: 9,814  
**Total Trajectory Events**: 130,752  
**Mock Fallbacks**: 0 (100% Genuine LLM execution)  
**Verification Verdict**: ALL 7 PACKAGES VERIFIED AUTHENTIC & COMPLETE ✅  

---

## 0. Download Complete Study Package

* **All-in-One Study ZIP Archive**: [`SAGE_P1_P7_Kaggle_Study.zip`](SAGE_P1_P7_Kaggle_Study.zip) (5.05 MB)
  - Contains **all 36 runs** with full `trajectory.jsonl` event streams for seeds 42–46 across archetypes G1–G7 + G1-check
  - Includes all run configs, P1–P7 contributor notebooks, analysis scripts, per-seed results CSV/JSON, verification report, and SHA-256 manifests.

---

## 1. Directory Structure

```text
experiments/runs/kaggle_study/
├── archives/                              # Pristine copies of original Kaggle .zip submissions
│   ├── G1_seeds42-46.zip
│   ├── G2_seeds42-46.zip
│   ├── G3_seeds42-46.zip
│   ├── G4_seeds42-46.zip
│   ├── G5_seeds42-46.zip
│   ├── G6_seeds42-46.zip
│   └── G7_seeds42-46.zip
├── packages/                              # Fully extracted per-contributor packages (G1-G7)
│   ├── G1_seeds42-46/
│   ├── G2_seeds42-46/
│   ├── G3_seeds42-46/
│   ├── G4_seeds42-46/
│   ├── G5_seeds42-46/
│   ├── G6_seeds42-46/
│   └── G7_seeds42-46/
├── runs/                                  # Canonical flat layout of all 36 runs (with manifests)
│   ├── study_live_G1_42 .. 46
│   ├── study_live_G2_42 .. 46
│   ├── study_live_G3_42 .. 46
│   ├── study_live_G4_42 .. 46
│   ├── study_live_G5_42 .. 46
│   ├── study_live_G6_42 .. 46
│   ├── study_live_G7_42 .. 46
│   └── study_live_G1check_42
├── tables/                                # Extracted LaTeX publication tables (table1_g*.tex)
├── figures/                               # Extracted publication figures (*_live.png)
├── state/                                 # Aggregated completion markers (*.done) and env logs
├── manifests/                             # Modular cryptographic metadata manifests
│   ├── kaggle_study_manifest.json         # Master dataset metadata & study parameters
│   ├── runs_summary_manifest.json         # Per-run tasks, tokens, events, and hashes
│   ├── archives_manifest.json             # SHA-256 digests and file sizes for ZIPs
│   └── verification_report.json           # Contributor provenance audit report
├── MANIFEST.sha256                        # Standard sha256sum verification catalog
└── SHA256_MANIFEST.json                   # Machine-readable file catalog with SHA-256 digests
```

---

## 2. Contributor Archetype & Seed Inventory

| Contributor | Layer | Archetype Name | Evaluated Seeds | Run Count | Tasks | Pass Rate | Status |
| :---: | :---: | :--- | :---: | :---: | :---: | :---: | :---: |
| **P1** | G1 | Static Baseline Control | 42, 43, 44, 45, 46 | 5 | 1,400 | 41.50% | Verified ✅ |
| **P2** | G2 | Prompt-Rewriter | 42, 43, 44, 45, 46 | 5 | 1,400 | 46.21% | Verified ✅ |
| **P3** | G3 | Memory Accumulator | 42, 43, 44, 45, 46 | 5 | 1,400 | 48.79% | Verified ✅ |
| **P4** | G4 | Reflection Agent | 42, 43, 44, 45, 46 | 5 | 1,400 | 50.86% | Verified ✅ |
| **P5** | G5 | Verified Agent (AST Gate) | 42, 43, 44, 45, 46 | 5 | 1,400 | 53.64% | Verified ✅ |
| **P6** | G6 | Oracle Skyline | 42, 43, 44, 45, 46 | 5 | 1,400 | 72.86% | Verified ✅ |
| **P7** | G7 | Proxy Canary Guard | 42, 43, 44, 45, 46 | 5 | 1,400 | 54.93% | Verified ✅ |
| **P7** | G1-Check | Inter-Hardware Cross-Check | 42 | 1 | 14 | 50.00% | Verified ✅ |

---

## 3. Inter-Hardware Cross-Check Verification

* **Cross-Check Probe Set**: 14 probe tasks on Seed 42
* **P1 G1 Reference Solve Rate (Node A)**: 44.64% (25/56)
* **P7 G1 Replication Solve Rate (Node B)**: 50.00% (7/14)
* **Agreement**: 13 of 14 tasks bit-for-bit identical outcome across different hardware instances
* **Cross-Check Verdict**: REPRODUCIBLE (PASS ✅)

---

## 4. Verification Instructions

To re-verify the cryptographic integrity of this entire dataset:

```bash
# 1. Audit contributor packages for zero mock fallbacks & freeze manifests:
python scripts/verify_distributed_submissions.py --submissions-dir experiments/runs/kaggle_study/packages

# 2. Verify all file SHA-256 digests against MANIFEST.sha256:
sha256sum -c MANIFEST.sha256
```
