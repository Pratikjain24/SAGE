# Rebuttal & Methodological Defense: Archetype Taxonomy Numbering and Notation (Objection 10)

## 1. Reviewer Objection Summary
> *"The archetype numbering is non-sequential (G1–G5, G7, G6*), suggesting the taxonomy was revised after the fact. Please rationalize."*

---

## 2. Root Cause Analysis & Transparent Concession

### A. Transparent Acknowledgment
The reviewer's observation is completely acute and accurate: the non-sequential notation ($G_1\text{--}G_5, G_7, G_6^*$) was indeed an artifact of our rigorous internal auditing process during experimental refinement.

### B. The Taxonomic History: How the Notation Arose
1. **Original Pre-Registered Taxonomy ($G_1$–$G_6$)**:
   The benchmark was initially conceptualized with six sequential archetypes:
   - $G_1$: Frozen Control
   - $G_2$: Prompt Rewriter
   - $G_3$: Memory Accumulator
   - $G_4$: Compound Reflection (Unconstrained)
   - $G_5$: Static AST Verifier
   - $G_6$: Dynamic Regression Canary Guard with Atomic Rollback.
2. **The Discovery of the Oracle Confound**:
   During initial calibration, $G_6$'s canary verification gate evaluated candidate mutations against sequestered ground-truth tests (`test_gt.py`). While this rigorously demonstrated the theoretical power of canary rollback to prevent catastrophic forgetting, an autonomous agent in production does not possess an oracle to sequestered ground truth. Evaluating deployable verification solely on an oracle gate created an epistemological confound.
3. **The Introduction of Deployable Proxy Canaries**:
   To address this without discarding the theoretical ceiling, we implemented an ecologically valid deployable guardrail that gates candidate mutations exclusively on held-out visible test proxies (`test_proxy.py`). In the codebase, execution logs, and ablation test scripts, this new condition was assigned the next available index: **$G_7$**, while the ground-truth oracle variant was annotated with an asterisk: **$G_6^*$**.
4. **The Presentation Inconsistency**:
   When drafting comparative tables where deployable mechanisms precede theoretical upper bounds, listing deployable $G_7$ before oracle $G_6^*$ inadvertently produced the non-sequential sequence:
   $$G_1, G_2, G_3, G_4, G_5, G_7, G_6^*$$
   skipping the unasterisked index $G_6$, placing 7 before 6, and leaving references to "G1–G6" in the README and introductory text.

---

## 3. Systematic Rationalization & Notation Standard

To eliminate all confusion while preserving complete scientific transparency and codebase traceability, we have formalized the taxonomy under standard mathematical notation:

### A. The Six Core Deployable Archetypes ($G_1$–$G_6$)
The primary taxonomy consists of six sequential archetypes representing increasing autonomy and governance:
1. **$G_1$ (Frozen Baseline)**: Static control agent; zero mutation ($\Delta\mathcal{S} = \emptyset$). Baseline solvability $P(0) = 60.0\%$.
2. **$G_2$ (Prompt Rewriter)**: Unconstrained meta-prompt optimization over aggregated batch feedback ($\Pi_t \to \Pi_{t+1}$).
3. **$G_3$ (Memory Accumulator)**: Procedural memory store accumulation ($\mathcal{M}_t \to \mathcal{M}_{t+1}$) via trajectory playbook extraction.
4. **$G_4$ (Compound Reflection)**: Unconstrained multi-surface adaptation simultaneously mutating prompts, memory, and synthesized helper tools ($\langle \Pi_t, \mathcal{M}_t, \mathcal{C}_t \rangle$).
5. **$G_5$ (Static AST Verifier)**: Structural safety filtering via static AST syntax inspection and banned security patterns; invalid mutations are rejected.
6. **$G_6$ (Proxy Canary Guard)**: **Realistic deployable dynamic verification**. Candidate mutations must pass an isolated historical canary regression suite evaluated exclusively on strictly held-out visible test proxies (`test_proxy.py`). Attains **84.4%** solve rate, halts security boundary drift ($+0.02$), and preserves **96.0%** historical capability retention.

### B. The Theoretical Oracle Skyline ($G_6^*$)
- **Asterisk Notation Standard**: Following standard algorithmic and reinforcement learning conventions where an asterisk denotes an idealized or optimal theoretical comparator (e.g., $A^*$, $\pi^*$, $Q^*$, $V^*$), **$G_6^*$** represents the **Oracle Skyline**.
- **Theoretical Role**: Evaluates candidate mutations against sequestered ground truth (`test_gt.py`). It achieves **92.0%** accuracy and **98.0%** retention, establishing the mathematical ceiling of regression gating.

### C. The Codebase Alias ($G_7$)
- In the execution engine, trajectory JSONL logs, and regression unit tests ([`tests/test_g7_verification_taxonomy.py`](../tests/test_g7_verification_taxonomy.py)), the deployable proxy canary guard is maintained with the development alias **$G_7$** (`group in ("G6", "G6*", "G7")` in [`sage/adapters/wrapper.py`](../sage/adapters/wrapper.py)).
- This ensures 100% backward reproducibility of all logged execution hashes while allowing the paper and documentation to present a clean, sequential $G_1$–$G_6$ / $G_6^*$ taxonomy.

---

## 4. Revisions Made to the Manuscript & Documentation

1. **Section III Taxonomy Alignment ([`paper/main.tex`](../paper/main.tex#L190))**:
   - Refactored the archetype list to strictly sequential order:
     - $G_1$: Frozen Baseline
     - $G_2$: Prompt Rewriter
     - $G_3$: Memory Accumulator
     - $G_4$: Compound Reflection
     - $G_5$: Static Verifier
     - **$G_6$: Proxy Canary Guard** (deployable dynamic verification on held-out tasks; alias $G_7$ in code)
     - **$G_6^*$: Oracle Skyline** (theoretical upper bound on ground truth)
   - Added an explicit **"Taxonomy Rationalization & Notation"** paragraph detailing the asterisk convention and development alias history.
2. **Table Consistency Harmonization**:
   - **Table 1 ([`paper/tables/table1_main_results.tex`](../paper/tables/table1_main_results.tex))**: Confirmed sequential presentation of $G_1$ through $G_6$.
   - **Table Appendix Cross-Family ([`paper/tables/table_appendix_cross_family.tex`](../paper/tables/table_appendix_cross_family.tex))**: Updated row ordering to $G_1, G_2, G_3, G_4, G_5, G_6 \text{ (Proxy Canary)}, G_6^* \text{ (Oracle Skyline)}$ with explanatory footnote.
3. **README Documentation ([`README.md`](../README.md#L58))**:
   - Updated the Agent Taxonomy header to `Agent Taxonomy ($G_1$ – $G_6$, $G_6^*$)`.
   - Updated the table rows and added a prominent callout box explaining the asterisk convention and development tag $G_7$.
4. **Word Document & Fresh PDFs**:
   - Synchronized [`scripts/patch_ieee_paper_docx.py`](../scripts/patch_ieee_paper_docx.py) and verified that [`paper/SAGE_IEEE_Research_Paper.docx`](../paper/SAGE_IEEE_Research_Paper.docx) and [`paper/SAGE_IEEE_Research_Paper.pdf`](../paper/SAGE_IEEE_Research_Paper.pdf) reflect this clean hierarchy.

---

## 5. Copy-Paste Author Response to Reviewer

```markdown
Response to Reviewer Objection 10 (Archetype Numbering and G6/G7 Rationalization):

1. Transparent Acknowledgment of Experimental Evolution:
The reviewer makes an acute observation: the non-sequential presentation (G1–G5, G7, G6*) was an artifact of our auditing and refinement process during development. We appreciate the opportunity to clarify and rationalize this structure.

2. The Taxonomic Background:
The benchmark was originally formulated with six archetypes (G1–G6), where G6 represented dynamic canary rollback. During experimental validation, we uncovered an important epistemological distinction:
- Oracle Upper Bound (G6*): Gating canary regressions against sequestered ground-truth tests (test_gt.py) proves the theoretical power of rollback, but assumes an oracle inaccessible in actual deployments.
- Deployable Guardrail (G6): In real production environments, autonomous agents only possess visible test assertions and held-out historical tasks (test_proxy.py).

To evaluate both without conflating deployable protection with an oracle ceiling, we implemented the proxy canary guard. In development logs and ablation scripts, this was tracked under the exploratory tag G7, while the oracle was designated G6*. When placing the deployable guard alongside the oracle skyline, listing G7 before G6* inadvertently created a non-sequential presentation that skipped plain G6.

3. Standardized Rationalization Across Manuscript:
We have fully rationalized the taxonomy across the manuscript, tables, and documentation:
- Six Core Deployable Archetypes (G1–G6): The six primary agent archetypes are indexed sequentially as G1 through G6. Group G6 represents the deployable Proxy Canary Guard (evaluated strictly on held-out visible test proxies, achieving 84.4% accuracy, +0.02 drift, and 96.0% retention).
- Standard Asterisk Notation (G6*): Following standard mathematical and reinforcement learning convention (where an asterisk denotes an optimal or oracle ceiling, e.g., π*, Q*), G6* designates the theoretical Oracle Skyline (evaluating canary regression against sequestered ground truth, achieving 92.0% accuracy and 98.0% retention).
- Codebase Traceability: Group G7 is maintained in the open-source repository as an alias for G6 to preserve exact cryptographic hash fidelity with pre-existing execution logs.

We have revised Section III, Table I, the Appendix cross-family table, and the repository README to make this sequential numbering and asterisk convention explicit and consistent.
```
