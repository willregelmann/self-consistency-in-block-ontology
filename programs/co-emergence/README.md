# Co-Emergence of Mass, Signature, Time, and Hilbert Space

**Status:** Draft

Mass, Lorentzian signature, local time, and local Hilbert space are four aspects of one structure. None exists without the others. They co-emerge as the unique cross-level self-consistent configuration of a four-dimensional block manifold with no evolution parameter, no background structure, and no fundamental Hilbert space.

## Paper structure

The paper leads with proved results, then develops the interpretive framework:

- **Section 3 (Lorentzian phases and the entropy excess):** The mathematical core. The Lorentzian self-consistency map produces complex phases locked to magnitudes in the fixed-point wavefunction (~25–34% imaginary content depending on subsystem rank, stable through N=256), absent in the Riemannian case. The phase-induced entropy excess lemma (Rigorous for rank-2 subsystems) proves S_Lor > S_Riem for any non-uniform magnitude profile. A finite toy model confirms composition, Born rule, and imaginary subsystem coherences through N=16, with the full 68% entropy excess arising entirely from phase structure.

- **Section 4 (The co-emergence thesis):** The interpretive framework. Mass requires Lorentzian signature (Wigner); signature provides local time; local time enables local Hilbert space (Page-Wootters); Hilbert space closes the loop via stress-energy. The mass assumption is weakened: the conformal trace anomaly generates effective mass for non-conformally coupled fields (Conjecture 2).

- **Section 5 (The self-consistency hierarchy):** Four-level hierarchy (topological → smooth → metric → effective QM). Level 2 is signature-blind; signature selection operates at the cross-level constraint.

## Relationship to other programs

- **`fixed-point-existence`** — Companion paper. Provides the Level 2 anchor: Banach contraction for massive fields (Rigorous), Starobinsky exact solution for conformal matter (Rigorous), Schauder existence (conditional). Results are cited, not re-derived.

- **`self-consistency-hierarchy`** (DEPRECATED) — Previous version of this paper. The hierarchy framework originated there; the co-emergence thesis emerged from its explorations (B1, C1, signature-mass debate, mass gap debate). The explorations in that program are the research record for this one.

## Key results

| Result | Status | Source |
|--------|--------|--------|
| Phase-induced entropy excess (rank 2) | **Rigorous** | Lemma in paper |
| Toy model: composition, Born rule, interference (N=4–16) | **Rigorous** (numerical) | Toy model exploration |
| ψ* imaginary content ~25–34% (rank-dependent), stable through N=256 | **Rigorous** (numerical) | Scaling/mixed-dims studies |
| S_Lor/S_Riem ≈ 1.68, entirely from phases | **Rigorous** (numerical) | Scaling study |
| Phase-induced entropy excess (general rank) | Conjecture | 20k+ tests, 0 violations |
| Level 2 is signature-blind (massive) | Rigorous | B1 exploration |
| Level 2 is signature-blind (massless) | Rigorous | Massless fixed-point exploration |
| Intersection form cannot force Lorentzian | Rigorous (obstruction) | C1 exploration |
| Self-consistent mass generation (ξ ≠ 1/6) | Sketch | Mass gap exploration |
| Co-emergence thesis | Conjecture | Paper Section 4 |

## Open problems

1. **Mass gap origin.** Where does mass come from? Conjecture 2 reduces the assumption from "massive fields" to "non-conformally coupled fields." Residual question: can ξ ≠ 1/6 be derived from Levels 0–1?

2. **Level 3 formalization.** The Born rule result is kinematic; the open question shifts from algebraic structure (confirmed) to dynamical aspects (unitary evolution, measurement). Reformulating Page-Wootters without a fundamental Hilbert space would promote co-emergence from Conjecture to Sketch.

3. **Level 0 manifold class.** Which 4-manifolds can be both Lorentzian and topologically rich? Closed simply-connected manifolds are obstructed (χ ≥ 3). Alternatives: non-compact (exotic R⁴), manifolds with boundary, non-simply-connected.

4. **Level 1 measure.** Natural measure on Sm(M) without metric input.

5. **Analytical open questions.** Why does imaginary fraction → 0.25? Why S_Lor/S_Riem ≈ 1.68? General rank proof of entropy excess lemma.

## Build

```bash
pdflatex index.tex
```
