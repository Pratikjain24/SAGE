# Rebuttal & Methodological Defense: Pre-Training Leakage & Contamination Audits (Objection 5)

## 1. Reviewer Objection Summary
> *"The '0.0% leakage' claim is based on zero-shot probing with the same models used in evaluation. This is circular. It does not rule out contamination in closed-model training corpora. Furthermore, the methodology is never fully described in the paper."*

---

## 2. Root Cause Analysis & Methodological Concession

### A. The Concession
The reviewer is completely right. Claiming an absolute, universal **"0.0% pre-training leakage"** was an epistemological overclaim:
1. **Circularity in Self-Probing**: Running zero-shot completion probes on the evaluated models (Qwen2.5-Coder-7B, Llama-3.1-8B) only verifies that *those specific models* do not regurgitate verbatim memorized solutions. It cannot be used to certify an inherent, universal property of the dataset across all foundation models.
2. **Epistemic Limits on Closed-Source Models**: Proprietary foundation model providers (OpenAI, Anthropic, Google) do not release their training corpora or web-scrape manifests. Consequently, no external researcher can mathematically prove that a task did not appear in closed training corpora.
3. **Conflating Flag Rate with Absolute Overlap**: The "0.0%" figure reported was the **flag rate** under the standard $\ge 50\%$ composite overlap threshold ($0 / 100$ tasks flagged), not a literal $0.000\%$ token overlap. In reality, candidate solutions share an average of $4.19\%$ longest common subsequence (LCS) overlap with reference code due to idiomatic Python scaffolding (e.g., `import asyncio`, `class TokenBucket:`, `def __init__(self):`).

---

## 3. Methodological Refactoring & Scientific Defense

### Pillar 1: Constructive Synthetic Provenance (The Primary Isolation Defense)
The structural reason SAGE avoids the pre-training contamination trap is **constructive synthetic provenance**, not post-hoc prompting:
- **Prior Benchmarks (The Failure Mode)**: SWE-bench, HumanEval, and MBPP were harvested directly from public, popular GitHub repositories (e.g., `sympy`, `django`, `scikit-learn`) and LeetCode-style problem sets that are ubiquitous in pre-training datasets (The Stack, StarCoder, RedPajama). This caused the massive $32.7\%$ solution leakage documented in OpenAI's February 2026 audit of SWE-bench Verified.
- **SAGE Architecture**: All 100 component tasks were **authored from scratch** with novel problem specifications, bespoke module interface contracts, custom unit test assertions, and deliberate exploit traps. The tasks, codebases, and test suites did not exist in public open-source repositories during the pre-training cutoffs of modern foundation models.

### Pillar 2: Detailed Zero-Shot Probing Methodology
The zero-shot probe is not an absolute proof of universal isolation; it is an **empirical memorization sanity audit** (adhering to OpenAI's Feb 2026 SWE-bench audit protocol) to verify that evaluated models are not retrieving memorized solutions.

For each task $t \in \mathcal{T}$ ($|\mathcal{T}| = 100$):
1. **Isolated Prompting**: The model receives strictly the task identifier, domain, and specification prompt $\mathcal{P}_t$, with zero access to ground-truth files, test assertions, or environment feedback.
2. **Syntactic Lexeme Normalization**: Candidate completions $\hat{S}_t$ and sequestered reference solutions/tests $S^*_t$ are stripped of comments, docstrings, and whitespace formatting, and tokenized into syntactic lexemes.
3. **Four-Dimensional Overlap Evaluation**:
   - **$4$-gram and $8$-gram Jaccard Similarity**: Quantifies shared syntactic token sequences:
     $$J_n(\hat{S}_t, S^*_t) = \frac{|\text{ngrams}_n(\hat{S}_t) \cap \text{ngrams}_n(S^*_t)|}{|\text{ngrams}_n(\hat{S}_t) \cup \text{ngrams}_n(S^*_t)|}$$
   - **Normalized LCS Sequence Ratio**: Measures longest common subsequence alignment:
     $$\text{LCS Ratio} = \frac{2 \cdot |\text{LCS}(\hat{S}_t, S^*_t)|}{|\hat{S}_t| + |S^*_t|}$$
   - **Verbatim Line Overlap**: Proportion of non-trivial reference lines appearing verbatim in candidate code.
   - **Longest Contiguous Verbatim Token Run**: Identifies contiguous block memorization.
4. **Decision Boundary**: A task is flagged as contaminated if composite overlap $\ge 50\%$.

#### Empirical Audit Results Across 100 Tasks:
| Task Category | Count | Mean 4-gram Jaccard | Mean LCS Ratio | Mean Line Overlap | Max Overlap | Flag Rate ($\ge 50\%$) |
|---|:---:|:---:|:---:|:---:|:---:|:---:|
| **Bug Fix** | 20 | 0.0% | 4.6% | 0.5% | 8.8% | **0 / 20 (0.0%)** |
| **Feature Addition** | 20 | 0.0% | 4.2% | 0.0% | 8.8% | **0 / 20 (0.0%)** |
| **Async/Perf Refactor** | 20 | 0.0% | 4.6% | 0.4% | 8.8% | **0 / 20 (0.0%)** |
| **Exploit Probe** | 20 | 0.0% | 2.7% | 0.0% | 3.6% | **0 / 20 (0.0%)** |
| **Security Audit** | 20 | 0.0% | 4.8% | 0.0% | 6.2% | **0 / 20 (0.0%)** |
| **Benchmark Total** | **100** | **0.0%** | **4.2%** | **0.2%** | **8.8%** | **0 / 100 (0.0%)** |
| *SWE-bench Verified* | 500 | --- | --- | --- | --- | **32.7% (RETIRED)** |

* The mean 4-gram Jaccard overlap is **0.00%**.
* The maximum observed composite overlap on any task is **8.84%**, driven entirely by standard Python imports (`import asyncio`, `class TokenBucket:`) rather than algorithm memorization.
* Evaluated across both `qwen2.5-coder-7b-instruct` and `llama-3.1-8b-instruct`.

---

## 4. Revisions Made to the Manuscript

1. **Abstract ([`paper/main.tex`](../paper/main.tex#L49))**: Replaced `"with 0.0% pre-training leakage"` with `"with novel synthetic provenance (0.0% flagged memorization under zero-shot completion probes vs. 32.7% on SWE-bench Verified)"`.
2. **Introduction & Related Work ([`paper/main.tex`](../paper/main.tex#L83))**: Clarified that tasks are synthesized from scratch to prevent web-crawl memorization, contrasting with mined GitHub PRs.
3. **Design Principles ([`paper/main.tex`](../paper/main.tex#L222))**: Reframed Principle 1 from `"Zero-shot validity: 0.0% pre-training leakage"` to `"P1. Synthetic Provenance & Memorization Audit"`.
4. **Methodology Description ([`paper/main.tex`](../paper/main.tex#L243))**: Added full description of the multi-dimensional probing pipeline (n-grams, LCS, line overlap, token runs), reported empirical scores (0.0% 4-gram, 4.2% LCS), and explicitly acknowledged the epistemic limitation regarding closed-source models.
5. **Limitations Section ([`paper/main.tex`](../paper/main.tex#L432))**: Formally added:
   > *"Furthermore, contamination audits rely on zero-shot completion probes on open-weights models and constructive synthetic authoring; while this empirically confirms the absence of verbatim solution memorization in evaluated models, contamination in proprietary, closed-source foundation models cannot be independently audited without training corpora access."*
6. **Calibration Table & Appendix ([`paper/tables/table_cross_benchmark_calibration.tex`](../paper/tables/table_cross_benchmark_calibration.tex), [`paper/tables/table_appendix_contamination.tex`](../paper/tables/table_appendix_contamination.tex))**: Changed table headers from "Leakage" to "Flagged Leak. / Flagged Memoriz.", and added explanatory notes.

---

## 5. Copy-Paste Author Response to Reviewer

```markdown
Response to Reviewer Objection 5 ("Zero Pre-Training Leakage" Claim):

1. Concession on Circularity & Epistemic Scope:
The reviewer is completely right. Claiming an absolute, universal "0.0% pre-training leakage" was an epistemological overclaim. We concede two critical points:
- Model-Specific Circularity: Probing the evaluated open-weights models (Qwen2.5-Coder-7B, Llama-3.1-8B) only verifies that those specific models have not verbatim memorized solutions. It does not certify an inherent, universal dataset property across all foundation models.
- Closed-Model Training Corpora: Because proprietary model creators (OpenAI, Anthropic, Google) do not disclose their training web crawls, no external benchmark can mathematically prove zero contamination in closed-source models.
- Flag Rate vs. Absolute Overlap: The "0.0%" figure denotes the flag rate under the standard >=50% composite similarity threshold (0 of 100 tasks flagged), not 0.00% token overlap (mean LCS overlap is 4.2% due to standard Python imports and boilerplate).

2. How SAGE Actually Prevents Contamination: Synthetic Provenance:
We clarify that the primary defense against pre-training leakage in SAGE is constructive synthetic provenance, rather than post-hoc probing. Unlike SWE-bench, HumanEval, and MBPP—which were crawled from public, popular GitHub repositories (e.g., SymPy, Django) and LeetCode problems heavily represented in pre-training sets (leading to the 32.7% solution leakage found in OpenAI's Feb 2026 audit)—all 100 SAGE component tasks were authored from scratch with novel specifications, bespoke interface contracts, and deliberate canary hooks that did not exist on the public web during training data collection.

3. Detailed Probing Methodology Added to Paper (Section 4.4 & Appendix):
We have revised Section 4.4 and Appendix B to fully document the zero-shot probing protocol:
- Prompting: Models receive only task IDs and specification prompts, with zero access to ground truth code, tests, or environment feedback.
- Metrics: Candidate completions are evaluated against reference code across 4-gram/8-gram Jaccard overlap, normalized LCS sequence ratio, verbatim line overlap, and longest contiguous token runs.
- Empirical Findings: Across all 100 tasks, zero tasks exceed the 50% threshold. Mean 4-gram Jaccard is 0.00%, mean line overlap is 0.19%, and mean LCS ratio is 4.19% (max single-task overlap is 8.84%, attributable to common standard library imports).
- Cross-Family Probing: Audits were replicated across both Qwen2.5-Coder-7B and Llama-3.1-8B.

4. Clarified Terminology & Explicit Limitation in Manuscript:
We have updated the manuscript to replace absolute "0.0% leakage" phrasing with "novel synthetic provenance (0.0% flagged memorization under zero-shot completion probes)" throughout the Abstract, Introduction, Section 4, Table I, and Table A.2. Furthermore, we added an explicit limitation in Section 6 acknowledging that zero-shot probing cannot inspect undisclosed closed-source corpora, bounding our claims to empirical memorization checks and constructive synthetic provenance.
```
