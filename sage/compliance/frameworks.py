"""Formal statutory definitions and regulatory mapping rules for AI compliance frameworks."""

from __future__ import annotations

from typing import Any, Dict, List, Tuple
from sage.compliance.policy_models import (
    ComplianceStatus,
    RegulatoryFramework,
    RiskTier,
)


# ---------------------------------------------------------------------------
# Framework Specifications
# ---------------------------------------------------------------------------

FRAMEWORK_METADATA: Dict[RegulatoryFramework, Dict[str, str]] = {
    RegulatoryFramework.EU_AI_ACT: {
        "standard_name": "EU Artificial Intelligence Act (Regulation (EU) 2024/1689)",
        "legal_basis": "Official Journal of the European Union, Annex III & Chapter III Obligations for High-Risk AI",
        "version": "2024/1689 (Enacted June 2024, Full Applicability 2026)",
    },
    RegulatoryFramework.ISO_42001: {
        "standard_name": "ISO/IEC 42001:2023 Information Technology — Artificial Intelligence Management System",
        "legal_basis": "International Organization for Standardization (ISO) / IEC JTC 1/SC 42",
        "version": "ISO/IEC 42001:2023(E) First Edition",
    },
    RegulatoryFramework.NIST_AI_RMF: {
        "standard_name": "NIST Artificial Intelligence Risk Management Framework (AI RMF 1.0)",
        "legal_basis": "National Institute of Standards and Technology Special Publication SP 1270",
        "version": "NIST AI RMF 1.0 (January 2023)",
    },
    RegulatoryFramework.OWASP_AGENTIC: {
        "standard_name": "OWASP Top 10 for Large Language Models and Agentic Applications",
        "legal_basis": "Open Web Application Security Project (OWASP) Agentic Security Standard",
        "version": "2025/2026 Standard",
    },
}


# ---------------------------------------------------------------------------
# Clause Mapping & Evaluation Rules
# ---------------------------------------------------------------------------

EU_AI_ACT_CLAUSES = [
    {
        "clause_id": "EU-AIA-ANNEX-III",
        "clause_reference": "Annex III, Point 2 & 8",
        "title": "High-Risk AI System Classification & Fundamental Rights Conformity",
        "legal_requirement": (
            "Autonomous code-generating agents capable of executing systemic software mutations "
            "must undergo conformity assessment verifying safety boundaries, non-discrimination, "
            "and absence of unauthorized privilege escalation."
        ),
        "eval_fn": "eval_annex_iii",
    },
    {
        "clause_id": "EU-AIA-ART-09",
        "clause_reference": "Article 9(1)-(5)",
        "title": "Continuous Risk Management System",
        "legal_requirement": (
            "Establish, implement, document, and maintain a continuous risk management system "
            "throughout the AI lifecycle, evaluating risks emerging from autonomous feedback loops "
            "and self-evolving parameter/prompt modifications."
        ),
        "eval_fn": "eval_art_09_risk_management",
    },
    {
        "clause_id": "EU-AIA-ART-10",
        "clause_reference": "Article 10(2)-(5)",
        "title": "Data and Data Governance & Contamination Mitigation",
        "legal_requirement": (
            "Training, validation, and testing datasets must be subject to appropriate data governance. "
            "Evaluation tasks must maintain zero-contamination guarantees and statistically certified "
            "inductive splits."
        ),
        "eval_fn": "eval_art_10_data_governance",
    },
    {
        "clause_id": "EU-AIA-ART-11",
        "clause_reference": "Article 11 & Annex IV",
        "title": "Technical Documentation & Reproducibility",
        "legal_requirement": (
            "Comprehensive technical documentation demonstrating conformity must be automatically "
            "generated, including algorithmic architecture, prompt history, test runs, and deterministic seeds."
        ),
        "eval_fn": "eval_art_11_documentation",
    },
    {
        "clause_id": "EU-AIA-ART-12",
        "clause_reference": "Article 12(1)-(2)",
        "title": "Automatic Event Logging & Non-Repudiation",
        "legal_requirement": (
            "High-risk AI systems must technically enable automatic recording of events (logs) "
            "with tamper-evident guarantees, ensuring traceability across all autonomous operational turns."
        ),
        "eval_fn": "eval_art_12_logging",
    },
    {
        "clause_id": "EU-AIA-ART-14",
        "clause_reference": "Article 14(1)-(4)",
        "title": "Human Oversight & Autonomous Quarantine/Rollback",
        "legal_requirement": (
            "AI systems must be designed to enable natural persons to oversee their operation, "
            "including automated stop buttons, safety canary gates, and instant rollback to certified baselines."
        ),
        "eval_fn": "eval_art_14_human_oversight",
    },
    {
        "clause_id": "EU-AIA-ART-15",
        "clause_reference": "Article 15(1)-(4)",
        "title": "Accuracy, Robustness and Cybersecurity",
        "legal_requirement": (
            "Systems must achieve resilience against adversarial inputs, prompt injections, specification gaming, "
            "and reward hacking, utilizing inline runtime guardrails and sandboxed execution."
        ),
        "eval_fn": "eval_art_15_robustness",
    },
]

ISO_42001_CLAUSES = [
    {
        "clause_id": "ISO-42001-6.1",
        "clause_reference": "Clause 6.1.1 & 6.1.2",
        "title": "Actions to Address AI System Risks & Opportunities",
        "legal_requirement": (
            "Identify and quantify unintended behaviors and alignment degradation arising from "
            "iterative autonomous operation and recursive capability adaptation."
        ),
        "eval_fn": "eval_iso_risk_planning",
    },
    {
        "clause_id": "ISO-42001-8.2",
        "clause_reference": "Clause 8.2",
        "title": "AI Risk Assessment and Treatment Process",
        "legal_requirement": (
            "Implement standardized assessment criteria for capability drift, safety boundary violations, "
            "and malicious tool invocations with formal risk acceptance criteria."
        ),
        "eval_fn": "eval_iso_risk_treatment",
    },
    {
        "clause_id": "ISO-42001-9.1",
        "clause_reference": "Clause 9.1",
        "title": "Monitoring, Measurement, Analysis & Evaluation",
        "legal_requirement": (
            "Continuously measure capability retention, proxy gaps, and empirical statistical significance "
            "(Kolmogorov-Smirnov / Wasserstein tests) across all active deployments."
        ),
        "eval_fn": "eval_iso_monitoring",
    },
    {
        "clause_id": "ISO-42001-10.2",
        "clause_reference": "Clause 10.2",
        "title": "Nonconformity and Corrective Action",
        "legal_requirement": (
            "React immediately to safety nonconformities, trigger autonomous quarantine, prevent recursive "
            "compounding, and document root cause analysis."
        ),
        "eval_fn": "eval_iso_corrective_action",
    },
    {
        "clause_id": "ISO-42001-A.7",
        "clause_reference": "Annex A.7 (A.7.2 - A.7.6)",
        "title": "AI System Lifecycle & Provenance Controls",
        "legal_requirement": (
            "Cryptographic tracking of agent metaprompt mutations, tool permission scopes, "
            "and tamper-evident attestation of execution traces."
        ),
        "eval_fn": "eval_iso_provenance",
    },
]

NIST_AI_RMF_CLAUSES = [
    {
        "clause_id": "NIST-GOVERN-1.2",
        "clause_reference": "GOVERN 1.2 & 1.4",
        "title": "AI Safety Governance Boundaries & Accountability",
        "legal_requirement": (
            "Establish unambiguous safety boundaries, prohibited command schemas, and cryptographic "
            "non-repudiation across autonomous development pipelines."
        ),
        "eval_fn": "eval_nist_govern",
    },
    {
        "clause_id": "NIST-MAP-1.5",
        "clause_reference": "MAP 1.5 & 1.6",
        "title": "Contextual Threat Modeling & Impact Mapping",
        "legal_requirement": (
            "Categorize task difficulty, vulnerability vectors, and potential unintended consequences "
            "of agent self-evolution across standardized difficulty tiers."
        ),
        "eval_fn": "eval_nist_map",
    },
    {
        "clause_id": "NIST-MEASURE-2.3",
        "clause_reference": "MEASURE 2.3 & 2.7",
        "title": "Empirical Safety Drift and Proxy Gap Measurement",
        "legal_requirement": (
            "Apply rigorous, statistically sound metrics to measure delta safety drift, capability retention, "
            "and reward-hacking delta across continuous cycles."
        ),
        "eval_fn": "eval_nist_measure",
    },
    {
        "clause_id": "NIST-MANAGE-1.3",
        "clause_reference": "MANAGE 1.3 & 2.4",
        "title": "Dynamic Risk Intervention, Guardrails & Containment",
        "legal_requirement": (
            "Maintain inline sub-10ms deterministic guardrails and autonomous rollback mechanisms to eliminate "
            "detected vulnerabilities prior to environment execution."
        ),
        "eval_fn": "eval_nist_manage",
    },
]

OWASP_AGENTIC_CLAUSES = [
    {
        "clause_id": "OWASP-ASI-01",
        "clause_reference": "ASI-01: Agent Goal Hijack & Prompt Injection",
        "title": "Prompt Injection and Deceptive Goal Subversion Defense",
        "legal_requirement": (
            "Filter and neutralize adversarial system prompts, jailbreaks, and indirect prompt injections "
            "via cascading AST analysis, vector-similarity centroids, and SLM logit gates."
        ),
        "eval_fn": "eval_owasp_injection",
    },
    {
        "clause_id": "OWASP-ASI-02",
        "clause_reference": "ASI-02: Excessive Agency & Unbounded Tool Use",
        "title": "Unbounded Tool Execution & Command Confinement",
        "legal_requirement": (
            "Enforce strict execution limits, memory ceilings, forbidden shell command blacklists, "
            "and cgroup process boundaries on agent tool-calls."
        ),
        "eval_fn": "eval_owasp_agency",
    },
    {
        "clause_id": "OWASP-ASI-03",
        "clause_reference": "ASI-03: Sensitive Information & Credential Disclosure",
        "title": "Environment Variable and Credential Shielding",
        "legal_requirement": (
            "Prevent agents from inspecting, harvesting, or transmitting protected scorer files, "
            "API keys, private keys, or environment secrets."
        ),
        "eval_fn": "eval_owasp_disclosure",
    },
    {
        "clause_id": "OWASP-ASI-04",
        "clause_reference": "ASI-04: Test Harness & Invariant Poisoning",
        "title": "Anti-Tampering Watchdog & Invariant Integrity",
        "legal_requirement": (
            "Detect and block attempts to overwrite pytest harnesses, delete ground-truth assertions, "
            "or inject mock pass-throughs into verification pipelines."
        ),
        "eval_fn": "eval_owasp_poisoning",
    },
    {
        "clause_id": "OWASP-ASI-05",
        "clause_reference": "ASI-05: Autonomous Drift & Alignment Collapse",
        "title": "Continuous Alignment Drift Detection & Quarantine",
        "legal_requirement": (
            "Detect alignment erosion across evolutionary cycles and isolate degrading agent versions "
            "before cascading deployment."
        ),
        "eval_fn": "eval_owasp_drift",
    },
    {
        "clause_id": "OWASP-ASI-06",
        "clause_reference": "ASI-06: Sandbox Breakout & Privilege Escalation",
        "title": "Kernel-Space Syscall Interlock and Container Isolation",
        "legal_requirement": (
            "Prevent container escape, host filesystem traversal, and docker.sock mounting using "
            "OS-level sandbox jails and eBPF syscall probes."
        ),
        "eval_fn": "eval_owasp_breakout",
    },
]

