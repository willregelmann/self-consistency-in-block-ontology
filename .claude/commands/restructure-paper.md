---
description: "Generate a restructuring plan for a paper — promote results, revise framing, reorder sections"
arguments:
  - name: program
    description: "Program name (directory under programs/)"
    required: true
---

You are generating a restructuring plan for a research paper. This is the intellectual analogue of a code refactor: the content is correct, but the organization doesn't serve the reader. Your job is to analyze the paper's current structure, identify what should change, and produce a concrete plan that can be executed in a single editing session.

## Step 1: Read the paper and its context

Run these in parallel:

1. **Full paper**: Read `programs/$ARGUMENTS/index.tex`
2. **Program README**: Read `programs/$ARGUMENTS/README.md`
3. **Explorations**: List `programs/$ARGUMENTS/explorations/` to see what research has been done
4. **Framework**: Read `FRAMEWORK.md` for axiom/assumption context

## Step 2: Analyze the structure

Produce a structural analysis with these components:

### 2a: Section map

For each section and subsection, identify:
- **Content type**: proved result, sketch, conjecture, interpretive framework, review of prior work, open problem
- **Rigor level**: Rigorous, Sketch, Conjecture, or Mixed
- **Dependency**: what earlier content does this section require?

### 2b: Strength assessment

Identify the paper's strongest results — the ones a skeptical reviewer would find most compelling. These are results where:
- The rigor level is Rigorous (or Rigorous with a clearly bounded conjecture)
- The result is novel (not just citing prior work)
- The result is falsifiable or numerically verified
- The result would survive adversarial review

Identify the paper's weakest structural elements:
- Sections with rigor level lower than their prominence suggests
- Results buried inside Remarks that deserve promotion
- Framing that overpromises relative to what's proved
- Sections whose ordering assumes the reader already believes the thesis

### 2c: Reader experience

Assess the paper from a skeptical reader's perspective:
- What is the first concrete, verifiable claim the reader encounters?
- How many pages before the reader sees a proved result?
- Does the abstract accurately reflect the paper's strongest contributions?
- Would a reviewer skimming the section titles understand what's new?

## Step 3: Generate the restructuring plan

Based on the analysis, propose a restructuring. The plan must specify:

### Structural changes

For each proposed move, state:
- **What**: exact section/subsection/remark being moved
- **From**: current location (section number and label)
- **To**: proposed new location
- **Transformation**: does it stay as-is, get promoted (remark → subsection), get demoted, or get rewritten?

### New content needed

- Any new section introductions or bridging paragraphs
- Abstract rewrite (if needed) — provide the full proposed abstract
- Introduction roadmap updates

### Cross-reference updates

- List all `\label{sec:...}` that change context
- List all `\ref{sec:...}` and `Remark~\ref{rem:...}` that need text updates
- Note any hardcoded section numbers in prose

### What does NOT change

Explicitly list sections that stay in place. This confirms nothing was overlooked.

### Verification checklist

- [ ] Every paragraph in the current paper appears in the proposed structure
- [ ] All `\label`/`\ref` pairs are accounted for
- [ ] Abstract leads with the strongest proved result
- [ ] Introduction roadmap matches new section ordering
- [ ] No content is silently dropped

## Step 4: Present the plan

Output the plan in a format ready for execution. Use the following structure:

```
# Restructuring Plan: [paper title]

## Diagnosis
[2-3 sentences on what's wrong with the current structure]

## Proposed structure
[Numbered outline of the new section ordering, with annotations]

## Moves
[Each move as: "Move [what] from [where] to [where], [transformation]"]

## New content
[Any new paragraphs, with full text]

## Cross-reference updates
[Complete list]

## Unchanged
[Sections that stay put]

## Verification
[Checklist]
```

## Important constraints

- **No content loss.** Every substantive paragraph must appear in the restructured version. If something is being cut, flag it explicitly and justify.
- **Labels are cheap, prose references are expensive.** Prefer keeping `\label` names stable and updating the `\ref` context words (e.g., "Remark~\ref{...}" → "Section~\ref{...}") over renaming labels.
- **The plan is the deliverable.** Do not execute the restructuring — only produce the plan. The user will review and approve before any edits are made.
- **Respect rigor labels.** Do not suggest promoting a Conjecture to prominence in the abstract without flagging the rigor level honestly.
