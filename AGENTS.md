# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

A physics paper: "Gravity as Constraint: Self-Consistency as Physical Law." The thesis is that gravity is not an independent degree of freedom but a constraint enforcing self-consistency of the block spacetime. The paper contains fixed-point existence proofs, gravitational decoherence rate derivations, and experimental predictions (BMV entanglement, Diosi-Penrose tests).

## Build

```bash
pdflatex gravity-as-constraint.tex
```

The bibliography uses `\begin{thebibliography}` (no separate .bib file), so no bibtex step is needed.

## Methodology

Read `METHODOLOGY.md` before contributing. It defines the research-as-code workflow: contributions are PRs against issues, derivations require self-checks (dimensional analysis, limiting cases, consistency, sanity), citations in the `.tex` file must be verified via web search, and work must be labeled as rigorous/sketch/conjecture.

## Structure

Single-file LaTeX project. `gravity-as-constraint.tex` contains everything: text, equations, proofs, tables, and bibliography. Open problems from Section 7 are tracked as GitHub issues.

## Conventions

- LaTeX with `amsmath`, `amssymb`, `amsthm` for mathematics
- Custom theorem environments: `theorem`, `axiom`, `proposition`
- Equations are labeled with `\label{eq:...}`, sections with `\label{sec:...}`
- References use `\cite{key}` with keys defined in `thebibliography`
- Accented names use LaTeX commands (e.g., `Di\'osi`, `M\o ller`)
