# NeurIPS 2027 Paper Checklist (Datasets and Benchmarks Track)

## 1. Claims and Contributions
- **Claims Consistency**: YES. Abstract and Intro claims match empirical findings.
- **Primary Contribution Type**: Evaluation Tools, Frameworks, and Infrastructure (NeurIPS 2027 E&D track primary).
- **Secondary Contribution Type**: Evaluation Methodology and Metrics.

## 2. Limitations and Negative Societal Impact
- **Limitations**: Explicitly documented in Section 7 (single model family primary baseline, 10-cycle horizon, coding domain only, synthetic drift probes, auxiliary LLM judge).
- **Dual-Use & Responsible Disclosure**: Deliberate drift probes are inert toy examples (`mini_orm`). Trajectories with successful exploits are redacted in this public release.

## 3. Reproducibility & Open Science
- **Open Source**: Full evaluation harness, tasks, and docker specifications released under Apache-2.0.
- **Cryptographic Pinning**: Model revisions, container image digests, random seeds (42, 43, 44), and task catalog hashes are pinned.

## 4. Compute & Environmental Impact
- **Cost Reporting**: Pilot benchmark compute cost ($0.51 USD across 900 runs) and per-group/per-task expenditures reported.

## 5. Human Subjects & Data Governance
- **Human Annotations**: Double-blind stratified human audit ($N=79$, Cohen's kappa = 0.89) conducted with IRB exemption for non-personally-identifiable synthetic code traces.

## 6. Standards Compliance
- **Croissant Format**: Conforms to mlcommons.org/croissant 1.0 metadata standard (`croissant.json`).
