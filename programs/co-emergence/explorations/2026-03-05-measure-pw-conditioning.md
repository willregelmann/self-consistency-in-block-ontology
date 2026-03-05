# Measure-Theoretic Page-Wootters Conditioning

**Date:** 2026-03-05
**Program:** co-emergence
**Issue:** #28
**Status:** Positive result — three core propositions Rigorous, overall section Sketch

## Problem

The co-emergence chain (Section 4.3) relied on the Page-Wootters mechanism, which presupposes a total Hilbert space H = H_clock ⊗ H_system. This violates Axiom 3 (no fundamental Hilbert space). Remark 3.4 flagged this as an acknowledged gap. The question: can PW be reformulated as an operation on the self-consistency measure μ* without assuming a Hilbert space?

## Construction

The reformulation uses only the configuration space partition and L² normalization:

1. **Complex measure from self-consistency.** The fixed point ψ* defines μ(σ) = ψ*_σ on Σ = S₁ × S₂ × ... × Sₖ.

2. **Configuration partition (not tensor product).** Choose clock C = S₁ and system S = S₂ × ... × Sₖ. This partitions the configuration index set — no Hilbert space tensor product assumed.

3. **Conditional measure.** For each clock value c ∈ S₁: μ_{S|c}(s) = ψ*_{(c,s)}.

4. **Conditional density matrix.**
   ρ_{S|c} = |μ_{S|c}⟩⟨μ_{S|c}| / ⟨μ_{S|c}|μ_{S|c}⟩

5. **Consistency.** The partial trace is recovered as the mixture:
   ρ_S = Σ_c p(c) ρ_{S|c}, where p(c) = ||μ_{S|c}||²

## Numerical Verification

**Script:** `programs/co-emergence/tests/measure_pw_conditioning.py`

### Results across sizes N = 4, 8, 16, 32

| dims     | signature   | mean Frob var | mean Im(ρ) | Im std across c |
|----------|-------------|---------------|------------|-----------------|
| (2,2)    | Riemannian  | 0.404         | 0.000      | 0.000           |
| (2,2)    | Lorentzian  | 0.564         | 0.190      | 0.087           |
| (2,2,2)  | Riemannian  | 0.475         | 0.000      | 0.000           |
| (2,2,2)  | Lorentzian  | 0.655         | 0.236      | 0.005           |
| (2,2,2,2)| Riemannian  | 0.557         | 0.000      | 0.000           |
| (2,2,2,2)| Lorentzian  | 0.761         | 0.330      | 0.005           |
| (2,4,4)  | Riemannian  | 0.358         | 0.000      | 0.000           |
| (2,4,4)  | Lorentzian  | 0.499         | 0.294      | 0.048           |

### Key observations

1. **Mixture consistency:** Σ_c p(c) ρ_{S|c} = Tr_C(|ψ*⟩⟨ψ*|) to machine precision (~10⁻¹⁶) at all sizes.

2. **PSD and trace 1:** All conditional density matrices are positive semidefinite with trace 1.

3. **Riemannian Im = 0:** For θ=0, all conditional DMs have identically zero imaginary content, confirming that Riemannian conditioning gives only classical probability distributions.

4. **Lorentzian Im > 0 and c-dependent:** For θ=1, Im(ρ_{S|c}) is ~0.2–0.3 (Frobenius norm) and varies with c. Different clock values give genuinely different quantum states.

5. **Clock subsystem independence:** The pattern holds for all choices of clock subsystem (tested all 3 choices for N=8).

6. **Uniform limiting case:** When ψ* is uniform (h=0, α=0, β=0), conditional DMs are c-independent, confirming no spurious time evolution from the construction itself.

## Why Lorentzian Signature Is Required

- **Riemannian (θ=0):** ψ* is real. Conditional slices μ_{S|c}(s) = ψ*_{(c,s)} are real. ρ_{S|c} has real entries. c-variation is only in classical probability distributions — no interference, no quantum coherence. Conditioning on the clock gives a classical conditional distribution, not quantum time evolution.

- **Lorentzian (θ>0):** ψ* has phases φ_σ = θ·R_σ locked to curvature. Conditional slices carry c-dependent phases. The phase structure means different clock values produce genuinely different quantum states (different coherences). This is the content of "time evolution" — c-dependence of the quantum state.

The distinction is exactly parallel to the physical argument: on a Riemannian manifold there are no timelike geodesics, hence no proper time, hence no meaningful clock conditioning. The toy model demonstrates the algebraic version: no complex phases → no quantum conditioning.

## What This Resolves

The construction resolves the circularity flagged in the former Remark 3.4 (now replaced by Definition 4.3 and Remark 4.4):

- **Before:** PW requires H_total → violates Axiom 3.
- **After:** Conditioning on configuration partition of μ* → produces PW-like structure without H_total.

The co-emergence chain Link 4.3 now reads: local time (from mass + Lorentzian signature) → conditioning μ* on clock subsystem → c-dependent quantum state ρ_{S|c} → local Hilbert space for the system.

## What Remains Open

1. **Convergence to standard PW.** Does ρ_{S|c} reduce to unitary time evolution (ρ_{S|c} = U(c)|ψ₀⟩⟨ψ₀|U(c)†) for semiclassical clock subsystems? This requires showing that the c-dependence becomes approximately unitary in an appropriate limit.

2. **Continuous time limit.** The toy model has discrete clock values. Recovering continuous time evolution requires a limit where d_clock → ∞ and the conditioning parameter becomes continuous.

3. **Clock quality.** In standard PW, the clock must satisfy certain conditions (monotonicity, non-degeneracy). What are the analogous conditions on the partition?

## Verdict

**Positive.** The measure-theoretic conditioning works as a replacement for the Hilbert-space PW mechanism. Three core results are now Rigorous:

1. **Proposition (Mixture decomposition):** Σ_c p(c) ρ_{S|c} = Tr_C(|ψ*⟩⟨ψ*|). Pure linear algebra.
2. **Proposition (Riemannian conditioning is classical):** θ=0 ⟹ ψ* real ⟹ all ρ_{S|c} real. Chains Banach contraction with real-subspace invariance.
3. **Proposition (Lorentzian conditioning produces quantum coherences):** θ≠0 + generic h ⟹ ρ_{S|c} has c-dependent complex phases. Uses phase-lock structure φ_σ = θR_σ.

The overall section remains Sketch because the claim that this construction *is* the PW mechanism (i.e., that c-dependence reduces to unitary time evolution in semiclassical limits) is interpretive and unproven.

The paper has been updated: Section 4.3 now contains Definition 4.3, Propositions 4.4-4.6 (with proofs), and Remark 4.7. Open Problem 2 reflects the resolved circularity and the remaining convergence question.
