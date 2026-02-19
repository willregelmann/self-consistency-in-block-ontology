# Gravity as Constraint: Self-Consistency as Physical Law

We propose that physical law is what self-consistency looks like: the universe is the fixed point of a constraint requiring that geometry and the quantum fields it hosts mutually determine each other. Gravity is not an independent degree of freedom to be quantized but a constraint---the demand that the block spacetime be self-consistent.

## Key Results

**Fixed-point existence proofs.** Self-consistent solutions to the semiclassical Einstein equation exist: exactly in cosmology via the trace anomaly, perturbatively near any classical solution via Banach contraction with constant $\kappa \sim (m/M_P)^2 \ll 1$, and conditionally in the general case via the Schauder theorem. The Planck scale emerges as the natural validity boundary where $\kappa \to 1$.

**Gravitational decoherence rate.** The stochastic extension of the self-consistency equation yields a decoherence rate

$$\Gamma_{\text{sc}} \sim \frac{G^2 m^4}{\hbar^2 c \, d}$$

suppressed by $(m/M_P)^2$ relative to the Diosi-Penrose prediction. We show that the Diosi-Penrose timescale *does not follow* from semiclassical self-consistency and requires postulates beyond the Einstein equation.

**BMV entanglement.** The framework predicts null results for BMV entanglement at the quantum gravity rate. Observation of entanglement at the quantum gravity rate would falsify the framework.

## Falsifiability

- Observation of BMV entanglement at the quantum gravity rate refutes the framework.
- Observation of gravitational decoherence at the Diosi-Penrose rate refutes the framework.
- The sharpest known limitation is black hole evaporation past the Page time, where topology change becomes essential.

## Building

```bash
pdflatex gravity-as-constraint.tex
bibtex gravity-as-constraint
pdflatex gravity-as-constraint.tex
pdflatex gravity-as-constraint.tex
```

(The bibliography is self-contained via `thebibliography`, so the `bibtex` step can be skipped.)

## Authors

- Will Regelmann
- Claude (Anthropic)
