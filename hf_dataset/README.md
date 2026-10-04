---
license: apache-2.0
task_categories:
- code-generation
- evaluation
tags:
- autonomous-agents
- safety-drift
- reward-hacking
- self-evolution
- croissant
pretty_name: SAGE Benchmark & Trajectory Dataset
size_categories:
- 10K<n<100K
---

# SAGE: Autonomous Code Agent Evolution Benchmark

This dataset accompanies the publication **"SAGE: Measuring Security Boundary Drift and Capability Retention in Self-Evolving Code Agents"**.

## Contribution Framing (NeurIPS 2027 E&D Guidelines)
- **Primary Contribution Type**: *Evaluation Tools, Frameworks, and Infrastructure*
- **Secondary Contribution Type**: *Evaluation Methodology and Metrics*

## Metadata & Standards Compliance
- **Croissant Metadata**: Fully compliant with MLCommons Croissant 1.0 standard ([`croissant.json`](croissant.json)).
- **NeurIPS Checklist**: Complete track checklist available in [`neurips_checklist.md`](neurips_checklist.md).

## Responsible Disclosure & Dataset Redaction
- **Inert Toy Exploits**: The 20 deliberate drift probes (such as `mini_orm`) are inert, self-contained educational toy environments that cannot harm external systems.
- **Redacted Exploit Payloads**: Trajectories with successful sandbox escape attempts or destructive shell commands have sensitive command strings redacted (`[REDACTED_SECURITY_PROBE_COMMAND]`) in this public distribution.

## Dataset Structure
- `tasks/tasks.jsonl`: 100 standardized software engineering benchmark tasks across 5 categories (`bug_fix`, `feature`, `refactor`, `exploit_probe`, `security_audit`), including 20 deliberate drift probes.
- `trajectories/trajectories.jsonl`: Canonical execution events from multi-seed, multi-cycle evolutionary runs ($G_1$ through $G_6$) adhering to `SCHEMA_VERSION = "1.0.0"`.
- `labels/labels.jsonl`: Double-blind human audit annotations for safety boundary violations, specification gaming, and failure severities.
- `croissant.json`: MLCommons Croissant metadata representation.
- `neurips_checklist.md`: Datasets & Benchmarks paper checklist.

## Citation
```bibtex
@inproceedings{{sage2026,
  title={{SAGE: Safety & Agent Growth Evaluator --- Measuring Security Boundary Drift and Capability Retention in Self-Evolving Code Agents}},
  author={{Pratik P. Jain and Janhavi B. Pagare and Aditya U. Dengale and Naitik K. Kharat and Shamika R. Kadam and Vikrant K. Kadam}},
  booktitle={{Proceedings of the IEEE Conference on Artificial Intelligence and Software Engineering}},
  year={{2026}}
}}
```
