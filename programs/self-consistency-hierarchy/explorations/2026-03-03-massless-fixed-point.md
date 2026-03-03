# Exploration: Massless Fixed Points of the SCE

**Date:** 2026-03-03
**Type:** Research investigation
**Outcome:** The Starobinsky de Sitter solution is a massless self-consistent fixed point. It is signature-blind (the round S⁴ is the Riemannian analogue). This confirms that Level 2 self-consistency does not distinguish signatures for ANY field content — massive or massless. Signature selection must operate at the cross-level constraint.

---

## Question

Does the SCE have a fixed point for massless conformally coupled fields? If so, does it distinguish metric signatures?

## Answer

**Yes, and no.**

### The Starobinsky de Sitter solution is massless and self-consistent (Rigorous)

The SCE on FRW spacetime with conformal matter admits an exact de Sitter solution (Starobinsky 1980). The mechanism is the trace anomaly: ⟨T^μ_μ⟩ = aE₄ + cW² gives a nonzero stress-energy even for massless fields. On de Sitter (conformally flat, so W = 0), the full stress-energy is ⟨T_μν⟩ = ρ_eff g_μν by SO(1,4) symmetry (Bunch-Davies 1978). Self-consistency is exact for the full tensor, not just the trace.

This is a self-consistent Level 2 fixed point with m = 0.

**Caveat:** "Conformal matter" here means fields whose classical action is conformally invariant but whose quantum trace anomaly is nonzero — spin-1/2 fermions, spin-1 gauge bosons, or non-minimally coupled scalars. A single conformally coupled scalar (ξ = 1/6, m = 0) has zero trace anomaly in 4D; the Starobinsky mechanism requires multiple fields or fields of higher spin.

### The massless fixed point is signature-blind (Rigorous)

The round 4-sphere S⁴ is a self-consistent Riemannian solution of the SCE with conformal matter, by exactly the same symmetry argument:

- S⁴ is conformally flat (W = 0), maximally symmetric (SO(5))
- ⟨T_μν⟩ = ρ_eff g_μν by SO(5) symmetry
- The self-consistency condition is the same algebraic equation for the radius

The 4-sphere is the Euclidean section of de Sitter (the Hartle-Hawking instanton). Both are self-consistent. Level 2 does not distinguish signatures for massless fields, just as B1 showed it does not distinguish signatures for massive fields.

### The massless fixed point does not support Level 3 (Sketch)

De Sitter with only conformal massless matter has:

- A well-defined Lorentzian metric ✓
- Timelike geodesics (the metric is Lorentzian) ✓
- **No massive particles** ✗
- **No local clocks** (no proper time along massive worldlines — there are no massive objects) ✗
- **No decoherence, no classicality, no effective QM** ✗

The Starobinsky solution is a self-consistent geometry in equilibrium with quantum vacuum fluctuations. It is consistent at Level 2 but empty at Level 3.

### Stability

Within FRW: the Starobinsky de Sitter is a stable attractor (Rigorous). Anisotropic perturbations isotropize (Sketch — strong evidence from R² gravity). General perturbative stability is open.

For the Banach contraction: fails for m = 0. The non-local kernel decays algebraically (not exponentially), and the Hilbert-Schmidt bound diverges. The Schauder theorem might establish existence without the contraction property, but gives existence without uniqueness. Multiple massless fixed points near a given classical background are possible (Conjecture).

## Implications

### Level 2 is completely signature-blind

This is now established for all field content:

| | Massive (Banach) | Massless (Starobinsky) |
|---|---|---|
| Lorentzian fixed point | Exists (Rigorous) | Exists (Rigorous) |
| Riemannian fixed point | Exists (B1 result) | Exists (S⁴, Rigorous) |
| Signature sensitivity | None | None |
| Level 3 support | Yes | No |

Signature selection does not happen at Level 2 — not for massive fields, not for massless fields, not perturbatively, not exactly. If signature is selected, it is selected by cross-level consistency: Levels 0-1-2-3 simultaneously.

### The co-emergence thesis is sharpened

The refined conjecture: among all self-consistent fixed points of the SCE (Level 2), only those with Lorentzian signature AND massive field content support Level 3 (effective QM, local Hilbert space, local time). The Starobinsky/S⁴ solutions are both Level 2 consistent and both Level 3 empty.

Mass is what separates "geometrically consistent" from "physically inhabited."

### The Starobinsky solution as inflationary background

In standard cosmology, the Starobinsky de Sitter is the inflationary phase that precedes the matter-dominated universe. It is physically relevant not as the final state but as the initial state from which massive excitations emerge (via reheating). In the hierarchy's language: the Starobinsky fixed point is where Level 2 first becomes self-consistent; the transition to massive field content is where Level 3 turns on. This temporal description must be handled carefully per FRAMEWORK.md — the block satisfies all constraints simultaneously, not sequentially.
