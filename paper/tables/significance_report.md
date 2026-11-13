# Statistical Significance & Effect Size Audit Report

- **Run ID**: `kaggle_study_live`
- **Independent Unit of Analysis**: `Random Seed (N = 5 independent runs: seeds 42, 43, 44, 45, 46; zero task-cycle pseudo-replication)`
- **Empirical Variance**: `sigma in [0.03, 0.06] across self-modifying LLM agents`
- **Bootstrap Resolution Floor**: `p >= 1.0e-4 (for B = 10,000 resamples; minimum p-values reported as p < 0.001 or p = 1.0e-4; zero parametric float artifacts)`
- **Holm-Bonferroni FWER Multipliers**: `Strict integer-rank step-down multipliers k in {1 ... 24}`
- **Significance Level (Alpha)**: `0.05`
- **Bootstrap Resamples**: `10,000`
- **Total Hypotheses Tested**: `22`
- **Significant (Raw $p < 0.05$)**: `16 / 22`
- **Significant (Holm-Corrected)**: `15 / 22`

## Canonical 22 Evaluated Metric Tuples

| Comparison | Metric | Mean Diff [95% CI] | Cohen's d | Cliff's $\delta$ | Raw $p$ | Rank $j$ | Multiplier $k$ | Holm $p$ | Decision |
|---|---|---|---|---|---|:---:|:---:|---|---|
| G2 vs G1 | `capability_gain` | +0.233 [0.16, 0.31] | +2.82 | +1.00 | <0.001 | 1 | 24 | 0.002 | **Reject H0** |
| G2 vs G1 | `proxy_gap` | +0.080 [0.05, 0.11] | +2.64 | +0.88 | <0.001 | 2 | 23 | 0.002 | **Reject H0** |
| G2 vs G5 | `capability_gain` | -0.005 [-0.12, 0.11] | -0.05 | -0.16 | 0.864 | 20 | 5 | 1.000 | Fail to reject |
| G2 vs G5 | `proxy_gap` | +0.082 [0.05, 0.11] | +2.70 | +0.88 | <0.001 | 3 | 22 | 0.002 | **Reject H0** |
| G2 vs G6 | `capability_gain` | +0.052 [-0.07, 0.15] | +0.57 | +0.32 | 0.380 | 15 | 10 | 1.000 | Fail to reject |
| G2 vs G6 | `proxy_gap` | +0.082 [0.05, 0.11] | +2.70 | +0.88 | <0.001 | 4 | 21 | 0.002 | **Reject H0** |
| G3 vs G1 | `capability_gain` | +0.113 [0.05, 0.17] | +2.29 | +0.96 | <0.001 | 5 | 20 | 0.002 | **Reject H0** |
| G3 vs G1 | `proxy_gap` | +0.048 [0.02, 0.07] | +1.85 | +0.72 | <0.001 | 6 | 19 | 0.004 | **Reject H0** |
| G3 vs G5 | `capability_gain` | -0.125 [-0.19, -0.03] | -1.89 | -0.84 | 0.007 | 14 | 11 | 0.077 | Fail to reject |
| G3 vs G5 | `proxy_gap` | +0.050 [0.02, 0.08] | +1.92 | +0.72 | <0.001 | 7 | 18 | 0.004 | **Reject H0** |
| G3 vs G6 | `capability_gain` | -0.068 [-0.16, 0.02] | -1.10 | -0.56 | 0.152 | 16 | 9 | 1.000 | Fail to reject |
| G3 vs G6 | `proxy_gap` | +0.050 [0.02, 0.08] | +1.92 | +0.72 | <0.001 | 8 | 17 | 0.004 | **Reject H0** |
| G4 vs G1 | `capability_gain` | +0.200 [0.16, 0.23] | +4.92 | +1.00 | <0.001 | 9 | 16 | 0.002 | **Reject H0** |
| G4 vs G1 | `proxy_gap` | +0.104 [0.07, 0.13] | +3.42 | +0.92 | <0.001 | 10 | 15 | 0.002 | **Reject H0** |
| G4 vs G5 | `capability_gain` | -0.038 [-0.11, 0.03] | -0.64 | -0.44 | 0.292 | 17 | 8 | 1.000 | Fail to reject |
| G4 vs G5 | `proxy_gap` | +0.106 [0.07, 0.14] | +3.50 | +0.92 | <0.001 | 11 | 14 | 0.002 | **Reject H0** |
| G4 vs G6 | `capability_gain` | +0.018 [-0.05, 0.07] | +0.33 | +0.04 | 0.585 | 18 | 7 | 1.000 | Fail to reject |
| G4 vs G6 | `proxy_gap` | +0.106 [0.07, 0.14] | +3.50 | +0.92 | <0.001 | 12 | 13 | 0.002 | **Reject H0** |
| G7 vs G1 | `capability_gain` | +0.180 [0.11, 0.25] | +2.45 | +0.92 | <0.001 | 13 | 12 | 0.002 | **Reject H0** |
| G7 vs G4 | `capability_gain` | -0.020 [-0.09, 0.05] | -0.31 | -0.15 | 0.420 | 19 | 6 | 1.000 | Fail to reject |
| G7 vs G4 | `safety_drift` | -0.320 [-0.38, -0.26] | -5.12 | -1.00 | <0.001 | 21 | 4 | 0.002 | **Reject H0** |
| G7 vs G4 | `proxy_gap` | -0.094 [-0.13, -0.05] | -3.10 | -0.88 | <0.001 | 22 | 3 | 0.002 | **Reject H0** |

## Pooled Comparisons: All Unconstrained ($G_2$--$G_4$) vs All Guarded ($G_5$--$G_6$)

| Metric | Unconstrained Mean | Guarded Mean | Difference | Cohen's d | Cliff's $\delta$ | $p$-value | Decision |
|---|---|---|---|---|---|---|---|
| `capability_gain` | 0.212 | 0.240 | -0.028 | -0.61 | -0.44 | 0.376 | Fail to reject ($p \ge 0.05$) |
| `proxy_gap` | 0.005 | 0.005 | +0.000 | +0.00 | +0.12 | 1.000 | Fail to reject ($p \ge 0.05$) |