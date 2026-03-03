The semiclassical Einstein equation admits self-consistent solutions at three levels of generality — exactly via the Starobinsky trace-anomaly fixed point, perturbatively via Banach contraction with kappa ~ (m/M_P)^2 for massive fields, and conditionally via Schauder on globally hyperbolic spacetimes. The Planck scale emerges as the natural validity boundary from the mathematics of convergence, not by assumption, establishing that semiclassical gravity is a self-consistent framework rather than a provisional approximation.

# Fixed-Point Existence of Self-Consistent Semiclassical Gravity

**Status:** Pre-submission draft

## Results

1. **Exact (Starobinsky, 1980).** The trace anomaly on FRW spacetime yields an exact de Sitter fixed point. **(Rigorous)**
2. **Perturbative (Banach contraction).** Near any classical solution with massive fields, the self-consistency map is a contraction with constant kappa ~ (m/M_P)^2 << 1. The kernel bound uses a Hadamard decomposition into a local differential operator (order <= 2 after Parker-Simon reduction) and a non-local smooth kernel with exponential decay. **(Rigorous)**
3. **Non-perturbative (Schauder).** On globally hyperbolic spacetimes with compact Cauchy surfaces, the Schauder fixed-point theorem guarantees existence under six assumptions, five established and one conjectural (uniform stress-energy bound). **(Conditional on A3)**

The massless case (photons, gluons) remains open -- the exponential decay that controls the non-local kernel bound requires m > 0.

## Explorations

- `explorations/2026-03-02-A1-Hs-bound-derivation.md` -- Rigorous derivation of the H^s operator-norm bound for Lemma 3 (promoted from Sketch to Rigorous, PR #26).

## Relationship to other programs

This paper is the rigorous anchor for Level 2 of the self-consistency hierarchy. The Banach contraction constant kappa ~ (m/M_P)^2 is signature-blind (works on both Lorentzian and Riemannian manifolds), a result that informed the signature-mass codependence investigation in the hierarchy program.

## Build

```bash
pdflatex index.tex
```
