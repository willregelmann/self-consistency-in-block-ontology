# AGENTS.md

This file provides guidance to Claude Code (claude.ai/code) when working with this repository.

## Project

A research program developing a geometric block universe framework for quantum gravity. Papers are organized into programs (each with its own directory) and live at varying stages of completion.

## Programs

Each program has its own directory under `programs/` with a `README.md` describing its status, results, and relationship to other programs. Read the relevant README before starting work on a program.

## Repository structure

```
programs/                          — Each program has its own directory
  <program-name>/
    index.tex                      — The paper
    explorations/                  — Research investigations for this program
FRAMEWORK.md                       — Axioms, requirements, and hidden-assumption warnings
METHODOLOGY.md                     — Research-as-code workflow (read before contributing)
```

## Build

Each paper compiles independently:

```bash
pdflatex programs/<program-name>/index.tex
```

The bibliography uses `\begin{thebibliography}` (no separate .bib file), so no bibtex step is needed.

## Methodology

Read `METHODOLOGY.md` before contributing. It defines:

- The research-as-code workflow: contributions are PRs against issues, explorations are structured investigations in each program's `explorations/` directory
- Rigor standards and lifecycle: Conjecture → Sketch → Rigorous, with explicit demotion paths
- Citation discipline: paper-grade citations must be verified via web search; exploratory references must be flagged as unverified
- Adversarial review modes: verification (check the math) and stress testing (actively try to break the result)
- Agent team patterns: when to use teams vs. subagents, standard roles, team size guidance

## Conventions

- LaTeX with `amsmath`, `amssymb`, `amsthm` for mathematics
- Custom theorem environments: `theorem`, `axiom`, `proposition`, `lemma`, `conjecture`, `definition`, `remark`
- All results labeled: **(Rigorous)**, **(Sketch)**, or **(Conjecture)**
- Equations labeled `\label{eq:...}`, sections `\label{sec:...}`
- References use `\cite{key}` with keys defined in `thebibliography`
- Accented names use LaTeX commands (e.g., `Di\'osi`, `M\o ller`)
- Date format: Month YYYY
- Authors: Will Regelmann, Claude (Anthropic)

## Before starting work

1. Read `METHODOLOGY.md` — understand the contribution workflow and rigor requirements.
2. Read the program's `explorations/` directory if working on a topic that has been previously investigated.
3. Read the current state of the paper (`programs/<name>/index.tex`).
4. Check open GitHub issues for the relevant program before opening a new one.
