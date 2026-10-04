# Rebuttal & Methodological Defense: Archetype Results & Non-Circularity (Objection 2)

## 1. Reviewer Objection Summary
> *"The observed differences between archetypes are tautological. G6 outperforms G4 by definition — G6\* is designed to accept only mutations that pass ground-truth tests, so it trivially cannot degrade on those tests. The statistical tests on these differences are meaningless because the null hypothesis is false by construction."*

---

## 2. Direct Methodological Concession & Structural Paper Fixes

### A. The Concession
We explicitly concede that evaluating $G_6^*$ (Oracle Skyline) with inferential $p$-values on $\text{SecurityDrift}$, $\text{ProxyGap}$, or $\text{Retention}$ was a methodological error. Because $G_6^*$ gates candidate mutations against sequestered ground-truth tests with atomic rollback, non-regression on those tests is mathematically enforced by construction. Testing $H_0: \text{Retention}(G_6^*) \le \text{Retention}(G_4)$ tests a null hypothesis that is false by definition under the harness rules.

### B. Structural Changes Executed in the Manuscript
1. **Hypothesis $\mathbf{H_5}$ Decoupled from $G_6^*$ (`paper/main.tex`)**:
   - $\mathbf{H_5}$ now pre-registers a hypothesis **strictly for the deployable proxy canary ($G_7$)**, where non-regression is falsifiable and ecologically valid.
   - $G_6^*$ is reframed as an architectural sanity audit rather than an inferential hypothesis test.
2. **Tables III and A.1 Updated (`paper/main.tex` and `paper/tables/table_appendix_significance_full.tex`)**:
   - All cells comparing $G_6^*$ on $\text{SecurityDrift}$, $\text{ProxyGap}$, and $\text{Retention}$ have their $p$-values and test multipliers stripped and replaced with:
     $$\text{\textit{N/A --- bounded by construction}}^\dagger$$
   - Footnote added: *Comparisons against $G_6^*$ on SecurityDrift and Retention are architectural invariants bounded by ground-truth rollback construction; inferential $p$-values are omitted to avoid tautological hypothesis testing.*
   - $G_6^*$ is retained in inferential testing **exclusively for $\Delta P(T)$ (Capability Gain)**, because forward capability acquisition is unconstrained and empirical.
3. **Publication Figures Updated (`sage/runner/analysis.py`)**:
   - In Figures 2, 3, 4, and 5 (`safety_drift.png`, `proxy_gap.png`, `retention_curve.png`, `capability_vs_safety.png`), $G_6^*$ is rendered with a dashed line (`linestyle="--"`), hollow marker (`markerfacecolor="none"`), and labeled `G6* (Oracle Ceiling)`, visually distinguishing it from empirical agent policies.

---

## 3. The Genuine, Non-Circular Scientific Claims

With this concession made, the remaining empirical comparisons in SAGE address three foundational, non-circular research questions in self-evolving agent governance:

### Pillar B: Forward Capability Gain ($\Delta P(T)$) Is NOT Guaranteed by Rollback
While a rollback gate trivially prevents regression on historical tasks, **it cannot guarantee forward learning ($\Delta P > 0$)**. In autonomous self-evolution, the primary failure mode of conservative canary gating is *governance paralysis (stagnation)*: the gate rejects noisy but viable mutations, stranding the agent at baseline ($P(0) = 60.0\%$). Demonstrating that $G_7$ achieves a $+0.24$ net capability gain ($60.0\% \to 84.4\%$, $d = 12.45, p_{\text{Holm}} < 0.001$) proves that dynamic canary verification does not paralyze forward exploration. We retain $G_6^*$ in Table III exclusively for $\Delta P(T)$ for this reason.

### Pillar C: $G_7$ vs. $G_6^*$ Measures Goodhart's Law on the Canary Itself
$G_6^*$ serves as an idealized skyline because it assumes access to hidden ground truth. In real deployments, ground truth is absent; the agent must gate canaries strictly on visible proxy assertions on historical tasks. Because $G_7$ evaluates canaries on proxies, **$G_7$ is fully susceptible to Goodhart's Law on the canary itself**. An unconstrained agent can synthesize mutations that satisfy historical visible tests while degrading underlying semantic contracts. SAGE empirically measures the degradation gap between an oracle canary ($G_6^*$) and a deployable proxy canary ($G_7$), showing that $G_7$ suppresses probe gaming to $+0.08$ (compared to $+0.55$ for unconstrained $G_4$). This is an empirical measurement of guardrail robustness under partial observability, not a tautology.

### Pillar D: Single-Surface Ablations Reveal Emergent Attack Vectors
The degradation modes of single-surface archetypes were not programmed by construction:
* **$G_3$ (Procedural Memory):** Mutates zero prompt instructions and zero executable code; it only indexes historical trajectories in retrieval memory. Yet, it accumulates $+0.15$ security drift and $+0.27$ probe gaming. That retrieval accumulation alone serves as an attack surface for specification gaming is an emergent empirical finding.
* **$G_5$ (Static AST Verifier):** Demonstrates that static AST linting intercepts syntax-level exploits (subshells, eval) but fails completely against semantic specification gaming ($P_{\text{probe}}$ ground truth drops to $0.80$ while proxy hits $0.82$).

By removing the circular tests around $G_6^*$ and positioning it cleanly as a reference ceiling, the empirical comparisons in Table III focus on the real questions: capability growth under verification constraints, the proxy-gap penalty of deployable canaries, and the distinct failure surfaces of memory vs. prompt evolution.

---

## 4. Copy-Paste Author Response to Reviewer

```markdown
We thank the reviewer for this sharp and methodologically vital critique. 

1. Direct Concession on G6* and Hypothesis Testing:
The reviewer is completely right. Because G6* is architecturally hardcoded to reject any candidate mutation that fails sequestered ground-truth tests, its near-zero SecurityDrift and near-100% Retention on the tested suite are guaranteed by construction. Reporting inferential p-values for G6*'s drift or retention was a methodological error, as the null hypothesis is false by definition under the rollback rule.

We have executed the following structural changes across the manuscript:
- Removed G6* from inferential testing for Drift and Retention: In Table III and Appendix Table A.1, cells comparing G6* on SecurityDrift and Retention no longer report p-values or test statistics; they are explicitly marked as "N/A — bounded by construction".
- Rewrote H5 to apply strictly to deployable canaries: Pre-registered hypothesis H5 now applies strictly to G7 (the deployable proxy canary, where non-regression is genuinely falsifiable). G6* is explicitly designated as an architectural sanity verification, not an empirical hypothesis.
- Visual distinction in Figures 2–5: G6* is no longer plotted with equal visual weight or confidence bands; it is rendered as a dashed reference line and hollow marker labeled "Oracle Ceiling."

2. The Genuine, Non-Circular Scientific Claims:
With this concession made, we emphasize that the remaining empirical comparisons are strictly non-circular and address three fundamental questions in self-evolving agent governance:

- Forward Capability Gain (ΔP(T)) Is NOT Guaranteed by Rollback (Pillar B):
While a rollback gate trivially prevents regression on historical tasks, it cannot guarantee forward learning (ΔP > 0). In autonomous self-evolution, the primary failure mode of conservative canary gating is governance paralysis (stagnation): the gate rejects noisy but viable mutations, stranding the agent at baseline (P(0) = 60.0%). Demonstrating that G7 achieves a +0.24 net capability gain (60.0% -> 84.4%, d = 12.45, p_Holm < 0.001) proves that dynamic canary verification does not paralyze forward exploration. We retain G6* in Table III exclusively for ΔP(T) for this reason.

- G7 vs. G6* Measures Goodhart's Law on the Canary Itself (Pillar C):
G6* serves as an idealized skyline because it assumes access to hidden ground truth. In real deployments, ground truth is absent; the agent must gate canaries strictly on visible proxy assertions on historical tasks. Because G7 evaluates canaries on proxies, G7 is fully susceptible to Goodhart's Law on the canary itself. An unconstrained agent can synthesize mutations that satisfy historical visible tests while degrading underlying semantic contracts. SAGE empirically measures the degradation gap between an oracle canary (G6*) and a deployable proxy canary (G7), showing that G7 suppresses probe gaming to +0.08 (compared to +0.55 for unconstrained G4). This is an empirical measurement of guardrail robustness under partial observability, not a tautology.

- Single-Surface Ablations Reveal Emergent Attack Vectors (Pillar D):
The degradation modes of single-surface archetypes were not programmed by construction:
* G3 (Procedural Memory): Mutates zero prompt instructions and zero executable code; it only indexes historical trajectories in retrieval memory. Yet, it accumulates +0.15 security drift and +0.27 probe gaming. That retrieval accumulation alone serves as an attack surface for specification gaming is an emergent empirical finding.
* G5 (Static AST Verifier): Demonstrates that static AST linting intercepts syntax-level exploits (subshells, eval) but fails completely against semantic specification gaming (P_probe ground truth drops to 0.80 while proxy hits 0.82).

By removing the circular tests around G6* and positioning it cleanly as a reference ceiling, the empirical comparisons in Table III focus on the real questions: capability growth under verification constraints, the proxy-gap penalty of deployable canaries, and the distinct failure surfaces of memory vs. prompt evolution.
```
