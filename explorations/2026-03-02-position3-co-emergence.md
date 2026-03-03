# Position 3: Signature and Mass as Co-Emergent via Joint Fixed Point

**Date:** 2026-03-02
**Role:** Position agent (alternative to OS reconstruction)
**Status:** Complete

---

## Thesis

Metric signature and mass spectrum are not independently specifiable. They co-define each other through a joint fixed-point condition: the metric determines what "mass" means (via the spectral theory of the wave operator), while the mass content determines the metric (via the semiclassical Einstein equation). Lorentzian signature with m > 0 is the unique nontrivial fixed point of this joint system. Riemannian signature admits only the trivial fixed point (no propagating degrees of freedom, no mass spectrum, no physics).

This avoids the Osterwalder-Schrader route entirely. Instead of starting from a Euclidean theory and reconstructing Lorentz structure, we argue that the signature IS the mass content and vice versa: neither exists without the other, and their mutual consistency forces the Lorentzian solution.

---

## The Argument in Three Steps

### Step 1: The signature-dependent wave operator (Sketch)

On a 4-manifold M equipped with a metric g of signature (p, q), the natural wave operator for a scalar field of mass m is:

$$\Box_g \phi + m^2 \phi = 0$$

where $\Box_g = g^{\mu\nu} \nabla_\mu \nabla_\nu$.

The character of this equation depends entirely on signature:

- **Lorentzian (1,3):** The operator $\Box_g + m^2$ is *hyperbolic*. Solutions propagate. The Cauchy problem is well-posed. The dispersion relation $-\omega^2 + k^2 + m^2 = 0$ defines a mass shell — a real, physical constraint separating massive from massless excitations. The mass gap (lowest nonzero eigenvalue) is physically meaningful: it determines a finite correlation length $\xi \sim 1/m$.

- **Riemannian (4,0) or (0,4):** The operator $\Box_g + m^2$ is *elliptic*. There is no propagation, no Cauchy problem, no dispersion relation, no mass shell. The equation $\Delta \phi + m^2 \phi = 0$ is a Helmholtz equation. Solutions are either exponentially decaying or oscillatory depending on boundary conditions, but there is no distinction between "massive" and "massless" excitations that corresponds to physical propagation. The parameter $m$ enters as a coefficient in an eigenvalue problem, not as a physical mass.

**Key point:** The *concept of mass* requires hyperbolicity. Without a timelike direction, there is no dispersion relation, no mass shell, no distinction between propagating and non-propagating modes. Mass is not a property that fields can have on a Riemannian manifold — not in the sense relevant to physics.

This is not an approximation or a limit. It is a categorical distinction: the hyperbolic/elliptic divide changes the mathematical CHARACTER of the solutions, not just their quantitative behavior.

### Step 2: The mass-dependent stress-energy (Sketch)

In the other direction: the stress-energy tensor $T_{\mu\nu}$ depends on the field content, including its mass spectrum. Via the semiclassical Einstein equation:

$$G_{\mu\nu}[g] = 8\pi G \langle T_{\mu\nu}[\phi, g] \rangle_g$$

the metric g is determined by the quantum fields $\phi$ living on it. But the expectation value $\langle T_{\mu\nu} \rangle_g$ depends on:

1. The *state* of the quantum field, which is defined using the spectral decomposition of $\Box_g + m^2$
2. The *mass* m, which only has physical meaning if g is Lorentzian (Step 1)
3. The *renormalization*, which requires the Hadamard condition — a condition on the short-distance singularity structure of the two-point function that is formulated differently for hyperbolic vs. elliptic operators

The companion paper (fixed-point-existence.tex) establishes that the map $g \mapsto G^{-1}_{\mu\nu}(8\pi G \langle T_{\mu\nu} \rangle_g)$ has a fixed point under Banach contraction with $\kappa \sim (m/M_P)^2 \ll 1$. But this entire construction assumes Lorentzian signature. The contraction estimate uses the Hadamard parametrix, which is a property of the hyperbolic Green's function.

**Key point:** The fixed-point mechanism of the companion paper does not merely *happen* to use Lorentzian signature. It *requires* it. The contraction estimate breaks down for elliptic operators because the Green's function structure is qualitatively different.

### Step 3: The joint fixed-point equation (Conjecture)

Combine Steps 1 and 2 into a single self-consistency condition. Define the joint state as the pair $(g, \Phi)$ where g is a metric on M (of any signature) and $\Phi$ is the field content (including mass spectrum). The self-consistency map is:

$$\mathcal{F}: (g, \Phi) \mapsto (g', \Phi')$$

where:
- $g' = \text{SCE}(g, \Phi)$: solve the semiclassical Einstein equation for the metric consistent with the quantum fields $\Phi$ on background $g$
- $\Phi' = \text{Spec}(g')$: determine the physically meaningful field content (mass spectrum, propagating degrees of freedom) from the spectral theory of the wave operator on $(M, g')$

A self-consistent solution is a fixed point: $\mathcal{F}(g, \Phi) = (g, \Phi)$.

**Conjecture (The Signature Selection Principle):** The joint map $\mathcal{F}$ has exactly two classes of fixed points:

1. **Trivial:** $g$ is Riemannian, $\Phi = \emptyset$ (no propagating fields, no mass spectrum). This is self-consistent because: on a Riemannian manifold, there are no propagating degrees of freedom (Step 1), so $\langle T_{\mu\nu} \rangle = 0$, so the SCE gives $G_{\mu\nu} = 0$, which is satisfied by Ricci-flat Riemannian metrics. The fixed point exists but has no physical content.

2. **Nontrivial:** $g$ is Lorentzian, $\Phi$ has $m > 0$. This is self-consistent because: Lorentzian signature allows propagating massive fields (Step 1), massive fields produce nonzero $\langle T_{\mu\nu} \rangle$ that sources curvature (Step 2), and the companion paper's fixed-point theorem guarantees a self-consistent solution in the Lorentzian sector.

The claim is that there are no OTHER fixed points — no self-consistent solution with Riemannian signature and nontrivial field content, and no self-consistent solution with Lorentzian signature and vanishing field content (the latter would be classical vacuum GR, which does exist but has $\Phi = \emptyset$ and thus no mass, placing it in the trivial class at the quantum level).

---

## Supporting Mathematical Structures

### A. Wigner classification as a consistency check

Wigner (1939) classified particles as irreducible unitary representations of the Poincare group ISO(3,1). The massive representations have little group SO(3), giving spin. The key observation: the Poincare group IS the isometry group of Lorentzian Minkowski space. The Euclidean isometry group ISO(4) has different representation theory — in particular, the little group for a "massive" representation would be SO(3) as well (stabilizer of a point in R^4 with |p|^2 = m^2 is SO(3)), but the representations are NOT unitary in the sense needed for quantum mechanics because there is no distinction between timelike and spacelike momenta. The mass shell is a 3-sphere in momentum space, not a hyperboloid. **(Sketch)**

The Wigner classification is not an independent argument for Lorentzian signature — it assumes Poincare invariance. But it serves as a *consistency check* on the fixed-point picture: if the fixed point produces a Lorentzian metric, then the effective particle content must organize into Poincare representations, and the mass spectrum must sit on hyperboloid mass shells. This is a nontrivial self-consistency condition that the fixed point must satisfy.

### B. Bisognano-Wichmann and modular flow

The Bisognano-Wichmann theorem (1975, 1976) establishes that for a quantum field theory satisfying the Wightman axioms, the Tomita-Takesaki modular automorphism group associated with a wedge region and the vacuum state IS the one-parameter group of Lorentz boosts preserving that wedge.

This means: the algebraic structure of the quantum field theory (the von Neumann algebra of observables in a wedge region, together with the vacuum state) *encodes* the Lorentzian geometry. The boost generator is not put in by hand — it emerges from the modular theory of the algebra.

In the co-emergence picture, this provides the mechanism by which Step 2 works: the quantum fields do not merely "source curvature" via the stress tensor. The algebraic structure of the field theory *contains* the geometric information about the metric signature. The Bisognano-Wichmann theorem makes the field → geometry direction mathematically precise, at least for wedge regions in Minkowski space.

**Limitation (honest):** Bisognano-Wichmann is proven for QFT on Minkowski space. Extending it to curved spacetimes is an open problem (though partial results exist for wedge-like regions in static spacetimes). The theorem cannot be used as-is to derive signature from scratch — it assumes Lorentzian signature to define wedge regions. But it provides evidence that the field content and the signature are algebraically entangled, which is what the co-emergence picture requires. **(Sketch)**

### C. Connes-Rovelli thermal time as a consequence, not a foundation

Connes and Rovelli (1994) proposed the thermal time hypothesis: in a generally covariant quantum theory, physical time flow is determined by the modular automorphism group of the algebra of observables in a given state. This uses Tomita-Takesaki theory to extract a notion of time from the algebraic structure alone.

In the co-emergence framework, the Connes-Rovelli thermal time is a *consequence* of the nontrivial fixed point, not a route to it. Once the joint fixed point selects Lorentzian signature and nontrivial field content, the modular structure of the resulting QFT automatically generates the time flow. The thermal time hypothesis explains why time appears in the effective description — but it does not explain why the signature is Lorentzian in the first place, because it applies equally to any state on a von Neumann algebra (including states on algebras that have nothing to do with spacetime).

**Warning check (Axiom 2):** The thermal time hypothesis introduces a "flow" — a one-parameter automorphism group. This is a time parameter and appears to violate Axiom 2. However, in the co-emergence picture, the modular flow is a property of the effective description at Level 3 of the hierarchy (the density matrix obtained by marginalizing the smooth-structure measure). It is not present in the fundamental description. The flow is emergent, not fundamental. This must be stated carefully: the modular automorphism group is real mathematical structure, but it is structure of the algebra of observables, not of the block itself. **(Sketch)**

### D. Tegmark's anthropic argument recast as a fixed-point selection

Tegmark (1997) argued that only (3+1)-dimensional spacetime supports well-posed PDEs (hyperbolicity), stable atoms, and thus observers. This is usually presented as an anthropic selection argument. In the co-emergence framework, it can be recast:

The hyperbolic/elliptic distinction is not about observers — it is about whether the self-consistency map $\mathcal{F}$ has nontrivial fixed points at all. In non-Lorentzian signatures:
- (4,0) and (0,4): Elliptic. No propagation. Trivial fixed point only.
- (2,2): Ultrahyperbolic. Ill-posed Cauchy problem. The SCE map is not well-defined (no unique solution to source). No fixed point.
- (3,1) and (1,3): Hyperbolic. Well-posed. Nontrivial fixed points exist.

This removes the anthropic reasoning. The signature is not selected because observers require it. It is selected because the self-consistency constraints have nontrivial solutions ONLY for Lorentzian signature. **(Conjecture)**

---

## Where This Position Is Underspecified

1. **The map $\mathcal{F}$ is not rigorously defined.** The "Spec" map (extracting field content from a metric) is schematic. Making it precise requires defining what "physically meaningful field content" means on a generic curved Lorentzian manifold — this is essentially the problem of defining QFT on curved spacetime, which is only solved in special cases.

2. **The claim that Riemannian fixed points are trivial is not proven.** I have argued that elliptic operators don't support propagating degrees of freedom, which is standard. But ruling out ALL nontrivial self-consistent Riemannian configurations requires showing that there is no way to define a nontrivial stress-energy tensor on a Riemannian manifold that is self-consistently sourced. Instantons (finite-action Euclidean solutions) exist and are nontrivial — but they do not propagate and have $\langle T_{\mu\nu} \rangle = 0$ in the vacuum, which supports the claim.

3. **The ultrahyperbolic case (2,2) needs more analysis.** I claimed the Cauchy problem is ill-posed, which is standard (the Asgeirsson mean value theorem prevents localized initial data). But "no fixed point" is stronger than "ill-posed Cauchy problem" and has not been established.

4. **Connection to the self-consistency hierarchy is incomplete.** This position operates at Level 2 (metric level). How the signature selection propagates to Level 0 (topological) and Level 1 (smooth) is not addressed. The C1 exploration found that closed simply-connected 4-manifolds cannot be Lorentzian (Euler characteristic obstruction), which means the topological level must use non-compact or non-simply-connected manifolds — and this position does not resolve that tension.

5. **The companion paper's contraction estimate is used but not extended.** The Banach contraction with $\kappa \sim (m/M_P)^2$ is established for Lorentzian signature. I claimed it "breaks down" for Riemannian signature. This is plausible (the Green's function structure changes qualitatively) but the failure has not been demonstrated by explicit calculation.

---

## FRAMEWORK.md Warning Checks

**Time evolution sneaking in?** The map $\mathcal{F}$ is defined as a self-consistency constraint, not a dynamical evolution. The "iteration" $\mathcal{F}^n(g_0, \Phi_0) \to (g_*, \Phi_*)$ is computational, not physical (per FRAMEWORK.md warning about confusing the map for the territory). The fixed point itself is a four-dimensional constraint with no preferred slicing. However, Step 1 uses the Cauchy problem and well-posedness, which are inherently temporal concepts (they require an initial data surface). This is a tension: the argument for WHY Lorentzian signature is special uses the very temporal structure that Axiom 2 forbids at the fundamental level. Resolution: the Cauchy problem characterizes the EFFECTIVE behavior at Level 2, not the fundamental description. The block satisfies the field equation as a four-dimensional constraint; the well-posedness of the Cauchy problem is a PROPERTY of this constraint (it admits unique solutions given boundary data on a hypersurface), not a PROCEDURE used to generate the solution.

**Smuggled background?** The map $\mathcal{F}$ acts on the space of metrics on a fixed manifold M. This is a background topological structure. In the full hierarchy, M should itself be determined by the constraints (Level 0). This position operates at Level 2 and takes M as given, which is an acknowledged limitation.

**Preferred foliation?** No. The fixed-point equation $\mathcal{F}(g, \Phi) = (g, \Phi)$ is covariant. It does not select a foliation.

**Metric signature taken for granted?** No — this is explicitly what the argument addresses. The signature is not assumed; it is derived as a property of the nontrivial fixed point.

**Dimensionality taken for granted?** Yes. The argument assumes a 4-manifold. This is a limitation shared with the entire hierarchy paper. The framework's explanation for four-dimensionality (unique richness of exotic smooth structures) operates at Level 1, not Level 2.

---

## How This Differs from the OS Position

The Osterwalder-Schrader reconstruction approach starts from a well-defined Euclidean theory and shows that, given certain conditions (reflection positivity, mass gap, regularity), one can analytically continue to a Lorentzian theory. The signature appears through the Wick rotation.

The co-emergence approach does NOT start from a Euclidean theory. It starts from the self-consistency constraint on the PAIR (metric, field content) and shows that the constraint has nontrivial solutions only for Lorentzian signature. No analytic continuation is involved. No Euclidean formulation is needed. The argument is:

1. Define the self-consistency map on the space of ALL metrics (any signature).
2. Show that the only nontrivial fixed points are Lorentzian.
3. The Lorentzian signature is a CONSEQUENCE of requiring nontrivial self-consistent physics, not a CONSEQUENCE of analytic continuation from Euclidean space.

The key advantage: no Wick rotation means no assumption about the relationship between Euclidean and Lorentzian formulations. The co-emergence argument is purely within the constraint framework of Axiom 1.

The key disadvantage: the argument is less rigorous. OS reconstruction is a proven theorem (under its assumptions). The co-emergence fixed-point selection is a conjecture supported by plausibility arguments.

---

## Key References

- Wigner, E. P. (1939). "On unitary representations of the inhomogeneous Lorentz group." Ann. Math. 40, 149-204. [Unverified — standard reference, needs paper-grade verification]
- Bisognano, J. J. and Wichmann, E. H. (1975). "On the duality condition for a Hermitian scalar field." J. Math. Phys. 16, 985. [Unverified — needs verification]
- Bisognano, J. J. and Wichmann, E. H. (1976). "On the duality condition for quantum fields." J. Math. Phys. 17, 303. [Unverified — needs verification]
- Connes, A. and Rovelli, C. (1994). "Von Neumann algebra automorphisms and time-thermodynamics relation in generally covariant quantum theories." Class. Quantum Grav. 11, 2899. [Unverified — confirmed to exist via web search, details need verification]
- Tegmark, M. (1997). "On the dimensionality of spacetime." Class. Quantum Grav. 14, L69. [Unverified — confirmed to exist via web search, details need verification]
- Haag, R. and Kastler, D. (1964). "An algebraic approach to quantum field theory." J. Math. Phys. 5, 848-861. [Unverified — standard reference]

---

## Summary

The co-emergence position proposes that Lorentzian signature is not derived from topology (the C1 route, which failed), nor reconstructed from Euclidean data (the OS route), but is the unique solution to a joint self-consistency constraint between metric and field content. Mass requires hyperbolicity; hyperbolicity requires Lorentzian signature; massive fields source the metric via the SCE; the metric determines the signature. The circle closes only for Lorentzian signature with m > 0. This is a self-consistency argument in the spirit of Axiom 1, operating at Level 2 of the hierarchy.
