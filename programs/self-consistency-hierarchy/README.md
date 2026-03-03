A self-consistency hierarchy replaces the fundamental postulates of quantum gravity — Hilbert space, evolution parameter, background structure — with four nested geometric constraints on a block 4-manifold, and conjectures that Lorentzian signature, mass, local time, and local Hilbert space co-emerge as the unique cross-level self-consistent structure rather than as independent inputs.

# A Self-Consistency Hierarchy for Timeless Quantum Gravity

**Status:** Draft, mostly Conjecture

## The hierarchy

- **Level 0 (Topological):** PL 4-manifold with topological constraints. The original intersection form approach is obstructed for Lorentzian manifolds (see C1 exploration); the manifold class is under revision.
- **Level 1 (Smooth):** The space of exotic smooth structures Sm(M) is the configuration space. A self-consistency measure mu* on Sm(M) replaces both the wavefunction and the path integral measure.
- **Level 2 (Metric):** The semiclassical Einstein equation as a fixed point. Anchored by the companion paper `fixed-point-existence` (Banach contraction, Rigorous).
- **Level 3 (Effective QM):** Marginalizing mu* over the complement of a subregion produces an effective density matrix. The Hilbert space is derived, not fundamental.

## Central conjecture

Lorentzian signature is not derived from topology alone (the intersection form route fails) or from the SCE alone (the Banach contraction is signature-blind). Instead, signature is selected by the requirement that ALL levels be simultaneously consistent, mediated by mass:

**Mass <-> Lorentzian signature <-> local time <-> local Hilbert space**

These four concepts co-define each other. Physical mass (propagation on a mass shell) requires hyperbolicity (Lorentzian). Mass provides local proper time along timelike geodesics. Local proper time enables the Hilbert space formalism for massive subsystems. Without mass, none of these concepts exist. The Riemannian fixed point exists mathematically but is physically degenerate: the parameter m^2 is present but produces no mass shell, no propagation, no local clocks.

## Explorations

| File | Result |
|------|--------|
| `2026-03-02-research-plan.md` | Phased research plan with dependency graph |
| `2026-03-02-B1-signature-from-massive-fields.md` | **Negative.** Level 2 does not distinguish signatures. |
| `2026-03-02-C1-signature-bridge.md` | **Negative.** Intersection form cannot force Lorentzian signature; Euler characteristic obstruction. |
| `2026-03-02-signature-mass-codependence.md` | **Synthesis.** Three-position debate on signature-mass codependence. Joint fixed-point conjecture survives; OS reconstruction killed as mechanism. |
| `position-1-os-reconstruction.md` | Debate position: OS reconstruction path |
| `2026-03-02-position2-os-critique.md` | Debate position: adversarial critique of OS |
| `2026-03-02-position3-co-emergence.md` | Debate position: co-emergence via joint fixed point |

## Open problems (priority order)

1. **Mass gap origin.** Where does mass come from in the hierarchy? If from exotic smooth structures (Asselmeyer-Maluga program), needs verification.
2. **Signature selection principle.** Conjecture: nontrivial SCE fixed points only for Lorentzian + m > 0. Needs rigorous analysis of the Riemannian case.
3. **Level 0 manifold class.** Which 4-manifolds can be both Lorentzian and topologically rich?
4. **Measure on smooth structures.** Natural measure on Sm(M) without metric input.
5. **Marginalization conjecture.** Does restricting mu* to a subregion produce a density matrix?

## Build

```bash
pdflatex index.tex
```
