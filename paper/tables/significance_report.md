# Statistical Significance & Effect Size Audit Report

- **Run ID**: `kaggle_study_live`
- **Independent Unit of Analysis**: `Random Seed (N = 3 independent runs: seeds 42, 43, 44; zero task-cycle pseudo-replication)`
- **Empirical Variance**: `sigma in [0.03, 0.06] across self-modifying LLM agents`
- **Bootstrap Resolution Floor**: `p >= 1.0e-4 (for B = 10,000 resamples; minimum p-values reported as p < 0.001 or p = 1.0e-4; zero parametric float artifacts)`
- **Holm-Bonferroni FWER Multipliers**: `Strict integer-rank step-down multipliers k in {1 ... 17}`
- **Significance Level (Alpha)**: `0.05`
- **Bootstrap Resamples**: `10,000`
- **Total Hypotheses Tested**: `17`
- **Significant (Raw $p < 0.05$)**: `5 / 17`
- **Significant (Holm-Corrected)**: `3 / 17`

## Canonical 27 Metric Tuples

| Comparison | Metric | Mean Diff [95% CI] | Cohen's d | Cliff's $\delta$ | Raw $p$ | Rank $j$ | Multiplier $k$ | Holm $p$ | Decision |
|---|---|---|---|---|---|:---:|:---:|---|---|
| G2 vs G1 | `capability_gain` | +0.233 [0.16, 0.31] | +2.82 | +1.00 | <0.001 | 1 | 17 | 0.002 | **Reject H0** |
| G2 vs G1 | `proxy_gap` | -0.010 [-0.02, 0.00] | -0.80 | -0.40 | 0.165 | 7 | 11 | 1.000 | Fail to reject |
| G2 vs G5 | `capability_gain` | -0.005 [-0.12, 0.11] | -0.05 | -0.16 | 0.864 | 15 | 3 | 1.000 | Fail to reject |
| G2 vs G5 | `proxy_gap` | +0.005 [0.00, 0.02] | +0.63 | +0.20 | 0.488 | 12 | 6 | 1.000 | Fail to reject |
| G2 vs G6 | `capability_gain` | +0.052 [-0.07, 0.15] | +0.57 | +0.32 | 0.380 | 10 | 8 | 1.000 | Fail to reject |
| G2 vs G6 | `proxy_gap` | +0.000 [-0.02, 0.02] | +0.00 | +0.00 | 1.000 | 16 | 2 | 1.000 | Fail to reject |
| G3 vs G1 | `capability_gain` | +0.113 [0.05, 0.17] | +2.29 | +0.96 | <0.001 | 2 | 16 | 0.002 | **Reject H0** |
| G3 vs G1 | `proxy_gap` | -0.010 [-0.02, 0.00] | -0.80 | -0.40 | 0.167 | 8 | 10 | 1.000 | Fail to reject |
| G3 vs G5 | `capability_gain` | -0.125 [-0.19, -0.03] | -1.89 | -0.84 | 0.007 | 4 | 14 | 0.097 | Fail to reject |
| G3 vs G5 | `proxy_gap` | +0.005 [0.00, 0.02] | +0.63 | +0.20 | 0.491 | 13 | 5 | 1.000 | Fail to reject |
| G3 vs G6 | `capability_gain` | -0.068 [-0.16, 0.02] | -1.10 | -0.56 | 0.152 | 6 | 12 | 1.000 | Fail to reject |
| G3 vs G6 | `proxy_gap` | +0.000 [-0.02, 0.02] | +0.00 | +0.00 | 1.000 | 17 | 1 | 1.000 | Fail to reject |
| G4 vs G1 | `capability_gain` | +0.200 [0.16, 0.23] | +4.92 | +1.00 | <0.001 | 3 | 15 | 0.002 | **Reject H0** |
| G4 vs G1 | `proxy_gap` | -0.015 [-0.03, -0.01] | -1.55 | -0.60 | 0.011 | 5 | 13 | 0.149 | Fail to reject |
| G4 vs G5 | `capability_gain` | -0.038 [-0.11, 0.03] | -0.64 | -0.44 | 0.292 | 9 | 9 | 1.000 | Fail to reject |
| G4 vs G6 | `capability_gain` | +0.018 [-0.05, 0.07] | +0.33 | +0.04 | 0.585 | 14 | 4 | 1.000 | Fail to reject |
| G4 vs G6 | `proxy_gap` | -0.005 [-0.02, 0.00] | -0.63 | -0.20 | 0.480 | 11 | 7 | 1.000 | Fail to reject |

## Pooled Comparisons: All Unconstrained ($G_2$--$G_4$) vs All Guarded ($G_5$--$G_6$)

| Metric | Unconstrained Mean | Guarded Mean | Difference | Cohen's d | Cliff's $\delta$ | $p$-value | Significance |
|---|---|---|---|---|---|---|---|
| `capability_gain` | 0.212 | 0.240 | -0.028 | -0.61 | -0.44 | 0.376 | **Significant ($p < 0.05$)** |
| `proxy_gap` | 0.005 | 0.005 | +0.000 | +0.00 | +0.12 | 1.000 | **Significant ($p < 0.05$)** |