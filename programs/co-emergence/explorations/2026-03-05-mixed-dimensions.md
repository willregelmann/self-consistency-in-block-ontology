# Mixed-Dimensions Exploration: Non-Symmetric Tensor Products

**Date:** 2026-03-05
**Program:** co-emergence
**Status:** Complete — strongly positive
**Script:** `tests/mixed_dimensions.py`

## Motivation

All prior toy model tests used symmetric tensor products `dims=(2,2,...,2)`. This leaves open whether the entropy excess, composition, Born rule, and phase-stripping results are artifacts of the symmetric structure. The paper's falsification section flags this: "a failure at larger N or with non-symmetric tensor product structures would be significant."

Mixed dimensions also probe the general-rank conjecture of the entropy excess lemma: the proof is Rigorous only for `min(d_sub, d_env) = 2` (rank 2). Configurations like `3×4` (rank 3), `4×5` (rank 4), `5×6` (rank 5) directly test the conjectured regime.

## Setup

### Part 1: Bipartite mixed dimensions

12 configurations spanning ranks 2–6:

| dims | rank | N |
|------|------|---|
| (2,2) | 2 | 4 |
| (2,3) | 2 | 6 |
| (2,5) | 2 | 10 |
| (3,3) | 3 | 9 |
| (3,4) | 3 | 12 |
| (3,5) | 3 | 15 |
| (4,4) | 4 | 16 |
| (4,5) | 4 | 20 |
| (5,5) | 5 | 25 |
| (4,6) | 4 | 24 |
| (5,6) | 5 | 30 |
| (6,6) | 6 | 36 |

5 random seeds per config, θ=1, h ~ U[0.5, 1.5], α=0.4, β=0.4.

### Part 2: Multipartite mixed dimensions

6 configurations: (2,2,2), (2,2,3), (2,3,4), (2,2,5), (3,3,4), (2,3,5). Tested composition (Tr_{R2} ρ_R = ρ_{R1}) across all pair-to-single reductions, plus per-subsystem entropy ratios and interference.

### Diagnostics per configuration

- Imaginary fraction of ψ* (after global phase alignment)
- S_lor/S_riem for each subsystem marginal
- S_nophase/S_riem (phase-stripping test)
- Born rule error (5 random unitary bases)
- Destructive interference (20 random bases)
- Composition error (multipartite only)

## Results

### Entropy excess: 120 tests, 0 violations

**S_lor > S_riem for every subsystem of every configuration tested.** This includes ranks 3, 4, 5, and 6 — all beyond the proved rank-2 case.

| rank | S_lor/S_riem | im_frac | n_configs |
|-----:|:-------------|:--------|----------:|
| 2 | 1.703 ± 0.074 | 0.257 ± 0.053 | 15 |
| 3 | 1.679 ± 0.053 | 0.312 ± 0.039 | 15 |
| 4 | 1.682 ± 0.041 | 0.334 ± 0.024 | 15 |
| 5 | 1.685 ± 0.022 | 0.338 ± 0.015 | 10 |
| 6 | 1.688 ± 0.027 | 0.340 ± 0.014 | 5 |

The entropy ratio is remarkably stable across ranks: **~1.68 for all ranks tested.** Variance decreases with rank, consistent with larger systems being more self-averaging.

### Phase-stripping: perfect across all configurations

S_nophase/S_riem = 1.000000 ± 0.000000 across all 120 subsystem tests. The entire entropy excess is explained by the Lorentzian phases, with no exceptions for any rank or asymmetric bipartition.

### Imaginary fraction increases with rank

The ~25% imaginary fraction from the scaling study (which used only rank-2 bipartitions) is not universal:

- rank 2: im_frac ≈ 0.26
- rank 3: im_frac ≈ 0.31
- rank 4–6: im_frac ≈ 0.33–0.34

Higher-rank subsystems retain more imaginary content in the global wavefunction. The convergence toward ~0.34 at higher ranks may reflect a geometric property of the self-consistency map. The Riemannian im_frac is exactly 0 for all configurations (max = 0.00e+00).

### Composition: machine-precision for all mixed structures

All multipartite configurations pass composition to machine precision:

| dims | N | max composition error |
|------|---|----------------------|
| (2,2,2) | 8 | ~10⁻¹⁶ |
| (2,2,3) | 12 | ~10⁻¹⁶ |
| (2,3,4) | 24 | ~10⁻¹⁶ |
| (2,2,5) | 20 | ~10⁻¹⁶ |
| (3,3,4) | 36 | ~10⁻¹⁶ |
| (2,3,5) | 30 | ~10⁻¹⁶ |

Composition Tr_{R2} ρ_R = ρ_{R1} holds regardless of whether subsystem dimensions are equal, coprime, or mixed.

### Born rule: machine-precision for all configurations

Max Born rule error across all tests: ~10⁻¹⁵. No dependence on dimension asymmetry.

### Interference metric: needs refinement

Both Lorentzian and Riemannian states show "destructive interference" (p_quantum(k) < p_incoherent(k) for some k in some bases). This occurs because the definition compares full ρ to diag(ρ) — and even purely real off-diagonal elements (classical correlations from tracing a pure state) redistribute probabilities across rotated bases.

**This is a metric definition issue, not a physics issue.** The interference definition used in the N=8/16 tests may have been more restrictive (e.g., requiring the deficit to exceed a threshold, or defining the incoherent baseline differently). The entropy excess and phase-stripping results — which cleanly distinguish Lorentzian from Riemannian — are unaffected.

**Action needed:** revisit the interference metric in the N=8/16 test code to understand the discrepancy. The per-subsystem entropy ratio is the robust diagnostic.

## What this changes

### For the entropy excess lemma

The general-rank conjecture now has supporting evidence at ranks 2–6, with 120 tests and 0 violations. Combined with the prior 20,000+ random-matrix tests, the conjecture is extremely well-supported numerically. Still no proof for rank > 2.

### For the paper

- The paper currently reports im_frac ≈ 25% — this is correct for rank-2 subsystems but the general value depends on rank (25%–34%). Consider updating to state the rank dependence.
- The S_lor/S_riem ≈ 1.68 ratio is confirmed to be rank-independent, consistent with the analytical result that it depends on θ and h-spread but not dimensions.
- Composition and Born rule are confirmed for mixed dimensions — the paper's claims hold without qualification.
- The interference claim ("absent for all Riemannian ones") may need a more careful definition. See "Interference metric" above.

### Open questions

1. **Why does im_frac increase with rank?** It rises from ~0.26 (rank 2) to ~0.34 (rank 6) and appears to converge. What is the limit as rank → ∞?
2. **General rank proof.** Still open. The mixed-dimension evidence makes it more urgent — the conjecture holds at every rank tested, but only rank 2 is proved.
3. **Interference metric.** Needs a definition that cleanly separates quantum interference (from complex phases) from classical probability redistribution (from real correlations).
