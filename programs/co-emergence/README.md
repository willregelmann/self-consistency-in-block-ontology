# Co-Emergence of Mass, Signature, Time, and Hilbert Space

**Status:** Draft

Mass, Lorentzian signature, local time, and local Hilbert space are four aspects of one structure. None exists without the others. They co-emerge as the unique cross-level self-consistent configuration of a four-dimensional block manifold with no evolution parameter, no background structure, and no fundamental Hilbert space.

## Thesis

The semiclassical Einstein equation is signature-blind: self-consistent solutions exist for both Lorentzian and Riemannian metrics, for both massive and massless fields. Signature selection does not operate at the metric level. It operates at the cross-level constraint: only Lorentzian metrics with massive field content support the full four-level hierarchy — because mass provides local proper time (via timelike geodesics), which provides local Hilbert space (via the Page-Wootters mechanism), which provides the quantum stress-energy that sources gravity. Without mass, the chain breaks and the hierarchy collapses to a geometrically consistent but physically empty configuration.

## Relationship to other programs

- **`fixed-point-existence`** — Companion paper. Provides the Level 2 anchor: Banach contraction for massive fields (Rigorous), Starobinsky exact solution for conformal matter (Rigorous), Schauder existence (conditional). Results are cited, not re-derived.

- **`self-consistency-hierarchy`** (DEPRECATED) — Previous version of this paper. The hierarchy framework originated there; the co-emergence thesis emerged from its explorations (B1, C1, signature-mass debate, mass gap debate). The explorations in that program are the research record for this one.

## Key results established in explorations

| Result | Status | Source |
|--------|--------|--------|
| Level 2 is signature-blind (massive) | Rigorous | B1 exploration |
| Level 2 is signature-blind (massless) | Rigorous | Massless fixed-point exploration |
| Intersection form cannot force Lorentzian | Rigorous (obstruction) | C1 exploration |
| OS reconstruction killed as mechanism | Established | Signature-mass debate |
| Co-emergence thesis | Sketch | Mass-signature-time-Hilbert exploration |
| Mass is constrained input | Sketch | Mass gap debate synthesis |
| Cross-level selection requires mass for Level 3 | Conjecture | Co-emergence exploration |

## Open problems

1. **Mass gap origin.** The single deepest open problem. Where does mass come from? If from exotic smooth structures (Asselmeyer-Maluga), needs verification. If from self-consistency selection, needs formalization. Currently: mass is constrained input with conjectural path to derivation.

2. **Level 3 formalization.** Make "local Hilbert space requires local time requires mass" mathematically precise. Candidate tool: Page-Wootters mechanism adapted to show that conditioning on a massive clock subsystem requires hyperbolicity.

3. **Level 0 manifold class.** Which 4-manifolds can be both Lorentzian and topologically rich? Closed simply-connected manifolds are obstructed (chi >= 3). Alternatives: non-compact (exotic R^4), manifolds with boundary, non-simply-connected.

4. **Level 1 measure.** Natural measure on Sm(M) without metric input.

## Build

```bash
pdflatex index.tex
```
