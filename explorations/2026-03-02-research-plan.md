# Research Plan: Formalizing the Self-Consistency Hierarchy

**Date:** 2026-03-02
**Branch:** wdw-timeless-block
**Type:** Planning artifact
**Outcome:** Phased research plan with dependency graph, deliverables, and kill conditions

---

## Context

The self-consistency hierarchy paper (`src/self-consistency-hierarchy.tex`) proposes a four-level framework for timeless quantum gravity. Nearly all claims are labeled Conjecture. The companion paper (`src/fixed-point-existence.tex`) provides the only rigorous anchor, at Level 2. This plan maps every open problem into a prioritized sequence with dependencies, tractability assessments, and concrete deliverables.

The plan is organized by *dependency and risk*, not by level number. We attack the most tractable problem first (Level 2 completion), then the most dangerous (the signature bridge), then the problems that depend on those results (Levels 1 and 3).

---

## Dependency Graph

```
                    ┌─────────────────────────────┐
                    │  A1: H^s operator-norm bound │  (issue #20)
                    │  Level 2 — Rigorous upgrade  │
                    └──────────────┬───────────────┘
                                   │
                    ┌──────────────▼───────────────┐
                    │  A2: Uniform stress-energy    │  (see issue table below)
                    │  bound (A3 extension)         │
                    │  Level 2 — general case       │
                    └──────────────┬───────────────┘
                                   │
          ┌────────────────────────┼────────────────────────┐
          │                        │                        │
┌─────────▼──────────┐  ┌─────────▼──────────┐  ┌─────────▼──────────┐
│ B1: Lorentzian sig │  │ C1: Signature      │  │                    │
│ from massive fields│  │ bridge (topology   │  │                    │
│ Level 2            │  │ → metric)          │  │                    │
│ (issue #6)         │  │ Level 0 ↔ Level 2  │  │                    │
│                    │  │ (see issue table below)        │  │                    │
└─────────┬──────────┘  └─────────┬──────────┘  │                    │
          │                       │              │                    │
          └───────────┬───────────┘              │                    │
                      │                          │                    │
           ┌──────────▼──────────┐    ┌──────────▼──────────┐        │
           │ GATE: Is Level 0   │    │ D1: Natural measure  │        │
           │ viable?            │    │ on Sm(M)             │        │
           │ (Phase 2 verdict)  │    │ Level 1              │        │
           └──────────┬─────────┘    │ (see issue table below)          │        │
                      │              └──────────┬───────────┘        │
                      │                         │                    │
                      │              ┌──────────▼───────────┐        │
                      │              │ D2: Banach contraction│        │
                      │              │ on smooth-structure   │        │
                      │              │ measures              │        │
                      │              │ Level 1 → Level 2    │        │
                      │              │ (see issue table below)          │        │
                      │              └──────────┬───────────┘        │
                      │                         │                    │
                      └────────────┬────────────┘                    │
                                   │                                 │
                        ┌──────────▼──────────┐           ┌──────────▼──────────┐
                        │ E1: Marginalization │           │ E2: Macroscopic     │
                        │ conjecture toy model│           │ definiteness        │
                        │ Level 3             │           │ Level 3             │
                        │ (see issue table below)         │           │ (issue #4)          │
                        └─────────────────────┘           └─────────────────────┘
```

### Dependency summary

| Problem | Depends on | Blocks |
|---------|-----------|--------|
| A1: H^s bound | — | A2, B1, C1, D1 (all downstream) |
| A2: Uniform stress-energy | A1 | D2 (as input to contraction estimate) |
| B1: Lorentzian from massive fields | A1 (uses Banach machinery) | Gate decision |
| C1: Signature bridge | — (pure topology/geometry) | Gate decision |
| D1: Measure on Sm(M) | Gate (Level 0 viable) | D2, E1 |
| D2: Banach on smooth structures | A2, D1 | E1 |
| E1: Marginalization toy model | D1 (need measure to marginalize) | E2 |
| E2: Macroscopic definiteness | E1 | — |

B1 and C1 are independent of each other and can run in parallel. A1 is the only problem with no upstream dependency and the clearest path to completion.

---

## Phase 1: Metric-Level Completion (Level 2)

**Goal:** Promote the perturbative Banach contraction from Sketch to Rigorous.
**Upstream dependencies:** None.
**Estimated tractability:** High — the path is documented in issue #20.

### Problem A1: Rigorous H^s operator-norm bound (issue #20)

The perturbative Banach contraction (Section 4 of `fixed-point-existence.tex`) requires:

$$\left\|\frac{\delta\langle\hat{T}_{\mu\nu}\rangle_{\mathrm{ren}}}{\delta g}\right\|_{H^s \to H^{s-2}} < \infty$$

uniformly over the compact set $K_\rho$. The paper has a motivated scaling estimate $\kappa \sim (m/M_P)^2$ but flags it as insufficient for rigorous application of Banach's theorem.

**Concrete path** (from issue #20):
1. Express $\delta\langle\hat{T}_{\mu\nu}\rangle_{\mathrm{ren}}/\delta g$ as the retarded stress-energy two-point function.
2. Use the Källén-Lehmann spectral representation (massive case) to bound the kernel — spectral gap above $4m^2$ gives polynomial suppression at high $k$.
3. Translate momentum-space bound to $H^s \to H^{s-2}$ operator norm.
4. Confirm uniformity over $K_\rho$ via compactness and continuity from assumption (A2).

**Deliverable:** PR upgrading Section 4 of `fixed-point-existence.tex` from Sketch to Rigorous.

**Rigor target:** Rigorous (this is the point — close the gap).

### Problem A2: Uniform stress-energy bound (A3 extension)

The Schauder argument (Section 5) requires assumption (A3): uniform bound on $\langle\hat{T}_{\mu\nu}\rangle_{\mathrm{ren}}$ over $K_\rho$. This is established for FRW spacetimes (Pinamonti-Siemssen 2015). The general case requires controlling the state-dependent part of the Hadamard renormalization uniformly.

**Deliverable:** New issue documenting the gap. PR extending the bound if tractable, or documenting the obstruction if not.

**Rigor target:** Sketch → Rigorous for FRW; Conjecture → Sketch for general case.

### Kill condition

None — Level 2 problems have well-defined mathematical content and clear paths. Failure here would mean the specific technical approach (Källén-Lehmann, etc.) doesn't work, not that the result is wrong. Alternative approaches exist.

---

## Phase 2: Signature Bridge (Level 0 ↔ Level 2) — Critical Gate

**Goal:** Determine whether Lorentzian signature can be derived rather than assumed.
**Upstream dependencies:** Soft dependency on Phase 1 (B1 uses Banach machinery).
**Estimated tractability:** Unknown — this is the most uncertain phase.

This phase runs two independent investigations in parallel. Either one succeeding is sufficient; both failing triggers the kill condition.

### Problem C1: Intersection-form-to-signature bridge (see issue table below)

**The question:** Does an indefinite intersection form with signature $(1,n-1)$ on a smooth 4-manifold imply that compatible metrics must be Lorentzian?

This is a pure mathematics question in 4-manifold topology and Lorentzian geometry. The intersection form is a global invariant on $H_2$; the metric signature is local (tangent bundle). Connecting them requires a theorem that, to our knowledge, does not exist.

**Candidate approach:** An indefinite form with signature $(1,3)$ may be the only form compatible with an oriented smooth 4-manifold admitting a global timelike vector field. The Hirzebruch signature theorem $\sigma(\mathcal{M}) = \frac{1}{3}p_1(\mathcal{M})$ connects intersection form signature to the Pontryagin class, which constrains the tangent bundle. Whether this chain reaches metric signature is open.

**Deliverable:** Exploration documenting the mathematical investigation. If positive: validates the topological approach. If negative: documents what fails and what alternatives exist.

### Problem B1: Lorentzian signature from massive field content (issue #6)

**The question:** Does the self-consistency fixed point of the SCE *require* Lorentzian signature when the field content includes massive fields?

This is independent of Level 0 topology. It asks whether the Banach contraction at Level 2 simply fails on a Riemannian manifold — i.e., whether the metric-level self-consistency itself forces the signature.

**Candidate approach:** On a Riemannian manifold, there are no mass shells, no particle content, no propagating degrees of freedom in the usual sense. The stress-energy expectation value is fundamentally different. The question is whether $\mathcal{F}(g) = g$ has no solution when $g$ is Riemannian and the field content is massive.

**Deliverable:** Exploration or PR contributing to the signature discussion.

### Gate decision

After Phase 2, one of three outcomes:

1. **C1 succeeds:** Level 0 topological framework validated. Proceed with confidence to Phases 3–4.
2. **C1 fails but B1 succeeds:** Lorentzian signature derived at Level 2, not Level 0. Revise the hierarchy — Level 0 selects the PL manifold but does not determine the signature. The signature enters at the metric level. This weakens the topological program but does not kill it.
3. **Both fail:** The hierarchy cannot derive Lorentzian signature. The paper must retreat to "signature assumed" and flag this as the primary open problem. Level 0 is substantially revised.

### Kill condition

Both C1 and B1 produce negative results (not just "no progress" — actual counterexamples or no-go arguments). This forces the paper to:
- Weaken Conjecture 5 (signature emergence) to an explicit open problem without a proposed mechanism.
- Revise Section 6 to state that signature is assumed, not derived.
- Evaluate whether the hierarchy adds value over standard approaches if it cannot derive signature.

---

## Phase 3: Level 1 Measure Theory (Smooth Structures)

**Goal:** Define the self-consistency measure $\mu^*$ on $\mathrm{Sm}(\mathcal{M})$.
**Upstream dependencies:** Phase 2 gate (need Level 0 viable). Phase 1 partial (need Banach results as input to D2).
**Estimated tractability:** Low to medium — requires substantial original mathematics.

### Problem D1: Natural measure on smooth structures (see issue table below)

**The question:** Define a measure $\mu$ on $\mathrm{Sm}(\mathcal{M})$ that is:
1. Defined without reference to a metric (avoiding circularity with Level 2).
2. Compatible with the self-consistency condition $\mathcal{F}(\mu) = \mu$.
3. Invariant under orientation-preserving diffeomorphisms.

**Candidate approaches:**
- **Donaldson-Witten invariants** as weights. The Donaldson polynomial invariants $\gamma_d(S)$ assign integers to smooth structures via the moduli space of anti-self-dual connections. These are diffeomorphism invariants defined without a metric (they use a metric in intermediate steps but the result is metric-independent).
- **Seiberg-Witten invariants** as an alternative weighting. SW invariants are more computationally tractable and provide similar information.
- **Moduli space volume.** If $\mathrm{Sm}(\mathcal{M})$ can be given a natural topology (it has a partial order via cobordism), a measure might arise from the topology itself.

**Literature survey needed:** Existing constructions of measures on moduli spaces of gauge-equivalent structures, particularly in the context of topological QFTs. This is the most research-intensive sub-problem.

**Deliverable:** Literature survey exploration + new issue. If a candidate measure is identified: paper section or standalone paper.

### Problem D2: Banach contraction on smooth-structure measures (see issue table below)

**The question:** Given a measure on $\mathrm{Sm}(\mathcal{M})$, does the self-consistency map $\mathcal{F}$ on measures have a contraction estimate analogous to $\kappa \sim (m/M_P)^2$ at the metric level?

This extends the companion paper's Level 2 result to Level 1. The contraction would be in a suitable metric on the space of measures (e.g., Wasserstein distance, total variation).

**Depends on:** D1 (need the measure to be defined), A1/A2 (need the metric-level contraction as an ingredient).

**Deliverable:** New issue. Mathematical investigation yielding either a contraction estimate or identification of where the contraction breaks down.

### Kill condition

No natural measure on $\mathrm{Sm}(\mathcal{M})$ can be defined without metric input. The circularity — needing a metric to define the measure that determines the metric — is unresolvable. If this happens:
- Level 1 collapses to a formal construct (mathematically stated but not computable).
- The hierarchy loses its claim to replace the path integral measure problem — it has merely relocated the problem from metrics to smooth structures.
- Evaluate whether the Level 2 fixed-point result alone (companion paper) is sufficient to motivate the framework without a working Level 1.

---

## Phase 4: QM Emergence (Level 3)

**Goal:** Demonstrate that marginalization of the self-consistency measure produces quantum statistics.
**Upstream dependencies:** Phase 3 (need the measure to marginalize).
**Estimated tractability:** Medium for toy model; low for full theory.

### Problem E1: Marginalization conjecture — toy model (see issue table below)

**The question:** In a finite-dimensional analogue of the hierarchy, does marginalizing a self-consistent measure over the complement of a subregion produce an effective density matrix?

**Toy model specification:**
- Replace $\mathrm{Sm}(\mathcal{M})$ with a finite set of discrete "smooth structures" (e.g., simplicial complexes on a fixed triangulation).
- Define a self-consistency map $\mathcal{F}$ on probability distributions over this finite set.
- Find the fixed point $\mu^* = \mathcal{F}(\mu^*)$ (guaranteed by Brouwer's theorem in finite dimensions).
- Marginalize $\mu^*$ to a subregion.
- Check whether the marginal has the structure of a density matrix: positive, trace-one, with eigenvalues interpretable as probabilities.

This is achievable with existing tools. The toy model does not prove the full conjecture but demonstrates the mechanism in a controlled setting.

**Deliverable:** Paper section or standalone paper presenting the toy model. If it works: proof of concept for Level 3. If it fails: diagnostic of what goes wrong.

### Problem E2: Macroscopic definiteness (issue #4)

**The question:** Does measure concentration in the self-consistent measure produce effective decoherence in subregion marginals?

This requires E1 (the marginalization mechanism) plus understanding of how the global measure concentrates. The argument would parallel the derivation of classical behavior from quantum decoherence, but here the "decoherence" emerges from the measure structure rather than from environment-induced superselection.

**Deliverable:** Extension of E1 analysis to include concentration phenomena. Likely a section of the same paper.

### Kill condition

Even the finite-dimensional toy model fails to produce quantum-like statistics from marginalization. Specifically: the marginal of the self-consistent measure does not approximate a density matrix, or the statistics it produces are classical (commutative) rather than quantum (non-commutative). If this happens:
- Level 3 needs a different mechanism for QM emergence.
- The Hilbert-space-is-derived thesis survives (it follows from the argument in Section 2 of the hierarchy paper, independent of the marginalization mechanism), but the specific marginalization proposal fails.
- Investigate whether Page-Wootters conditioning provides an alternative Level 3 mechanism within the hierarchy.

---

## Cross-Cutting Concerns

### Citation verification backlog

The hierarchy paper has five citations marked `[VERIFY before final draft]`:
- Freedman (1982): J. Differential Geometry 17, 357
- Donaldson (1983): J. Differential Geometry 18, 279
- Taubes (1987): J. Differential Geometry 25, 363
- Smale (1961): Ann. Math. 74, 391
- Hirzebruch (1966): Topological Methods in Algebraic Geometry, Springer

These must be verified via web search before any PR promoting the paper beyond DRAFT status. This is a blocking requirement per METHODOLOGY.md citation discipline.

### Consistency check: WdW companion paper

The hierarchy paper references `\cite{wdw_paper}` — the Wheeler-DeWitt diagnostic paper. This paper was written and then deleted from the repository. The reference must either be:
1. Restored (re-add the paper), or
2. Removed (integrate the WdW diagnostic into the hierarchy paper itself), or
3. Converted to an internal note (cite the exploration instead).

This should be resolved before the hierarchy paper leaves DRAFT status.

### Framework axiom stress test

Before any phase produces a PR to the hierarchy paper, the PR should be stress-tested against every FRAMEWORK.md hidden-assumption warning:
- Does time evolution sneak back in? (The self-consistency map $\mathcal{F}$ is iterative — is the iteration sneaking in temporal structure?)
- Is metric signature taken for granted? (Phases 2+ directly address this.)
- Is dimensionality taken for granted? (The paper addresses this in Section 4, but the argument is Sketch.)
- Is there a smuggled background? (The PL manifold is a fixed input to Level 0.)
- Is observer-dependent language used? (Level 3 introduces "laboratory" and "subsystem.")

---

## New GitHub Issues to Open

| # | Title | Level | Blocks | Blocked by |
|---|-------|-------|--------|------------|
| #21 | Signature bridge: intersection form to metric signature | 0 ↔ 2 | D1 | — |
| #22 | Natural measure on smooth structures Sm(M) | 1 | D2, E1 | Phase 2 gate |
| #23 | Marginalization conjecture: finite-dimensional toy model | 3 | E2 | D1 |
| #24 | Banach contraction on smooth-structure measures | 1 → 2 | E1 | A1, D1 |
| #25 | Uniform stress-energy bound: extension beyond FRW | 2 | D2 | A1 |

Existing issues that map to this plan:
- **#20** → A1 (H^s bound)
- **#6** → B1 (Lorentzian signature from massive fields)
- **#4** → E2 (macroscopic definiteness)

---

## Summary Timeline

| Phase | Problems | Depends on | Delivers | Risk |
|-------|----------|-----------|----------|------|
| 1 | A1, A2 | — | Rigorous Banach contraction | Low |
| 2 | B1, C1 (parallel) | A1 (soft) | Signature verdict | High — potentially fatal |
| 3 | D1, D2 | Phase 2 gate, A1/A2 | Level 1 measure | Medium-high |
| 4 | E1, E2 | D1 | QM emergence toy model | Medium |

The plan is sequential in phases but parallel within phases. Phase 1 is immediate work. Phase 2 is the critical gate — its outcome determines whether the topological program survives. Phases 3 and 4 are contingent on Phase 2 success.
