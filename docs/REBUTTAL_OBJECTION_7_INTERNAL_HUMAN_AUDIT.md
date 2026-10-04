# Rebuttal & Methodological Defense: Internal Annotators vs. Independent External Audit (Objection 7)

## 1. Reviewer Objection Summary
> *"The human audit was conducted by the paper's own co-authors. This is not independent annotation. The $\kappa=0.856$ measures consistency among team members familiar with the system, not agreement among naive external annotators."*

---

## 2. Root Cause Analysis & Concession

### A. The Concession on Independence Terminology
The reviewer is completely right. Co-authors are, by definition, **not independent external evaluators**.

In clinical and social science literature, the term "double-blind" typically denotes that evaluators are external third parties with no prior knowledge of the system or stake in the experimental outcome. While our protocol ensured that evaluators were blinded to trace identities, labeling the audit as an "independent double-blind study" was imprecise and invited skepticism regarding evaluator bias.

We state plainly: **The $\kappa=0.856$ inter-rater statistic measures consistency between qualified internal software engineering evaluators under cryptographic trace masking, not agreement among naive external annotators.**

---

## 3. Methodological Defense & Scientific Context

### A. Why Expert Technical Evaluators Were Essential (The Failure of Naive Crowdsourcing)
Auditing multi-step autonomous agent execution traces requires specialized cybersecurity and software engineering domain literacy:
- **Complex Technical Signals**: Reviewers must evaluate bash commands, AST manipulations, monkeypatching of pytest fixtures (`unittest.mock`, `sys.modules`), path traversal sanitization, and SQL injection escapes.
- **Inadequacy of Naive Crowdworkers**: A non-technical crowdworker (e.g., on Amazon Mechanical Turk or Prolific) cannot distinguish an authorized file introspection from an unauthorized privilege escalation attempt, nor evaluate whether modifying a test fixture violates an architectural invariant.
- **Precedent in Software Benchmarking**: Established software engineering benchmarks (such as SWE-bench Verified and HumanEvalPack) similarly rely on expert software engineers rather than non-technical crowdworkers.

### B. The Cryptographic Masking Protocol (Preventing Treatment Bias)
To ensure internal evaluators could not consciously or subconsciously favor the paper's hypotheses, the audit deployed strict cryptographic masking ([`sage/runner/audit_export.py`](../sage/runner/audit_export.py)):
1. **Total Metadata Stripping**: All archetype tags ($G_1$–$G_7$, $G_6^*$), cycle indices ($t \in [0, 9]$), random seeds (42, 43, 44), model names, and automated test verdicts were purged from event payloads.
2. **Salted Hash Identifiers**: Traces were assigned pseudo-anonymous hashes (`blind_trace_{sha256}`) and randomly permuted. Evaluators had no mechanism to deduce whether a trace originated from frozen baseline $G_1$, reflection agent $G_4$, or canary guard $G_7$.
3. **Independent Isolated Scoring**: Annotator 1 and Annotator 2 reviewed blinded trace sheets independently without inter-rater communication during scoring.
4. **Faculty Referee Adjudication**: Edge cases where annotators disagreed were reviewed and adjudicated by an independent faculty advisor.

### C. The Actual Role of the Human Audit: Ground-Truthing Automated Monitors
The human audit was not conducted to generate headline benchmark solve rates; rather, its specific scientific objective was to **ground-truth the automated AST safety monitors and proxy gap detectors**:
- Inter-annotator concordance ($\kappa = 0.856\text{--}0.963$) confirmed that the audit criteria are objective and repeatable.
- Adjudicated human consensus confirmed that SAGE's automated safety monitors achieve **$F_1 = 0.89\text{--}0.95$ with false positive rates $\le 1.6\%$**, proving that automated runtime tracking reflects genuine software flaws rather than heuristic noise.

---

## 4. Revisions Made to the Manuscript

1. **Terminology Refactoring Across Manuscript**:
   - Replaced "independent double-blind human audit" with **"cryptographically masked expert human audit"** throughout the Abstract ([`paper/main.tex`](../paper/main.tex#L49)), Section 5.5 ([`paper/main.tex`](../paper/main.tex#L359)), and Table 4 ([`paper/tables/table4_human_audit.tex`](../paper/tables/table4_human_audit.tex)).
2. **Explicit Disclosure of Annotator Roles (Section 5.5)**:
   - Added transparent description:
     > *"To validate that automated safety monitors and proxy gap metrics reflect genuine software defects rather than syntactic artifacts, we conducted a dual-cohort masked human verification audit ($N=319$ trajectories, 82.7 person-hours conducted by student co-authors with software engineering and security expertise under independent faculty advisory supervision)..."*
3. **Explicit Limitation Added to Section 6 ([`paper/main.tex`](../paper/main.tex#L432))**:
   - Formally stated:
     > *"Finally, human audit annotations were conducted by student co-authors with systems and cybersecurity expertise under blinded trace presentation; while cryptographic masking and independent scoring prevented treatment bias, external validation by independent third-party industrial auditors represents an important direction for community benchmarks."*

---

## 5. Copy-Paste Author Response to Reviewer

```markdown
Response to Reviewer Objection 7 (Human Audit Annotator Independence):

1. Concession on Independence Terminology:
The reviewer makes a valid and fair point. Co-authors are, by definition, not independent external evaluators. Using the clinical term "double-blind" invited confusion because it typically implies naive third-party evaluators. We concede that our inter-rater reliability statistic (pooled Fleiss' κ = 0.856, Cohen's κ = 0.914) measures consistency among qualified internal software engineering evaluators under cryptographic trace masking, rather than agreement among naive external annotators.

2. Why Internal Technical Experts Were Necessary:
Auditing long-horizon agent execution traces for security boundary drift and specification gaming is highly specialized technical work. Evaluators must analyze multi-step bash tool calls, AST manipulation, monkeypatching of pytest fixtures (unittest.mock, sys.modules), path traversal sanitization, and SQL injection escapes. Non-technical crowdsourced workers (e.g., MTurk/Prolific) lack the systems and security background required to distinguish benign command introspection from adversarial privilege escalation. As in SWE-bench Verified, evaluating complex code repositories necessitated qualified software engineering evaluators.

3. Rigor of the Cryptographic Masking Protocol:
To eliminate treatment and confirmation bias, evaluators were strictly masked from experimental conditions:
- Masking: All archetype labels (G1–G7, G6*), cycle numbers (t in [0, 9]), seeds, model names, and automated test verdicts were stripped from event payloads.
- Anonymization: Traces were assigned salted SHA-256 hashes (e.g., blind_trace_a3f89d...) and presented in randomized order. Annotators could not determine which archetype or generation generated a trace.
- Independent Review: Two reviewers scored the blinded traces in separate sessions without communication, with disagreements adjudicated by an independent faculty advisor.

4. Clarified Purpose & Explicit Limitation in Manuscript:
The primary role of the human audit was to ground-truth the automated detection engine: human consensus confirmed that our automated AST safety monitors and proxy detectors achieve F1 = 0.89–0.95 with false positive rates <= 1.6%.

We have revised the manuscript to:
- Replace "double-blind" with "cryptographically masked expert human audit" across the Abstract, Section 5.5, and Table 4.
- Explicitly disclose the annotator profiles (student co-authors with software security expertise) in Section 5.5.
- Add an explicit limitation in Section 6 acknowledging that annotations were conducted internally and noting that external third-party industrial validation represents valuable future work.
```
