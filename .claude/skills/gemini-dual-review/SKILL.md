---
name: gemini-dual-review
description: Launches two parallel Gemini instances per paper to review GO-CAM claims from two complementary perspectives — a peer reviewer (scientific accuracy) and a GO-CAM curator (annotation correctness). Each receives the full claim in claims_template format and responds as an expert with OK/WRONG/UNCERTAIN plus a corrected claim where needed. Collects both outputs into peer_review_claims.md alongside the original claim.
argument-hint: "[PROCESS_FOLDER_NAME e.g. synaptic-vesicle-recycling]"
---

# GO-CAM Claims — Gemini Dual Review

## Purpose

For each claim in `agent-output/expert_validation_claims.md`, launch two Gemini instances that read the primary PDF and review the claim from two different angles:

1. **Peer reviewer** — scientific accuracy: figures, assays, quantitative values, biological statement, causality
2. **GO-CAM curator** — annotation correctness: GO MF terms, ECO codes, UniProt IDs, RO relations, confidence levels

Both receive the **complete claim block in claims_template format**. Both respond as domain experts: **OK**, **WRONG**, or **UNCERTAIN** with a written explanation. If WRONG or UNCERTAIN, they provide a corrected claim block in claims_template format.

You collect both outputs and write `peer_review_claims.md` — the original claim followed by both perspectives. You do not add your own verdicts.

---

## Folder Structure

```
gocam_models/
└── <process-name>/
    ├── literature/              # PDFs — Gemini reads these directly
    ├── agent-output/
    │   └── expert_validation_claims.md     ← READ THIS
    └── peer_review_claims.md               ← YOUR OUTPUT (process root)
```

---

## Protocol

### Step 1 — Parse the Claims Document

Read `agent-output/expert_validation_claims.md`. For each claim, capture the **complete block exactly as written**:

```
Claim [N]: [biological statement]

  Evidence: [assay], [Author et al. Year] (PMID: [PMID]), Fig [X] ([what it shows])

  Confidence: [HIGH/MEDIUM/LOW] — [justification. ECO:XXXXX]

  Expert response: OK / WRONG / UNCERTAIN
```

Also note the section heading (Section A: ..., B: ..., etc.) each claim belongs to.

### Step 2 — Group by PMID

Build a lookup: `{ PMID → [list of full claim blocks citing it] }`. One Gemini pair per unique PMID.

### Step 3 — Launch Gemini Pairs in Parallel

For each unique PMID, send **two Bash tool calls in the same message** — one peer reviewer, one curator. Where multiple PMIDs are independent, launch multiple pairs at once (four or six Bash calls in one message).

Substitute `<PROCESS>`, `<PMID>`, and paste the full claim blocks into `<CLAIMS>` before sending.

---

### Perspective 1 — Peer Reviewer

```bash
gemini --yolo -p "$(cat <<'PEER_EOF'
You are a strict senior peer reviewer in molecular and cellular biology. You are reviewing a GO-CAM expert validation document. Be extremely thorough — approach this as a real journal peer review.

Read this paper: gocam_models/<PROCESS>/literature/<PMID>.pdf

Each claim has this structure:
- Claim text: a plain-English biological statement naming the proteins (HGNC symbols in parentheses) and the mechanism. It must state HOW a protein acts (e.g. "phosphorylates", "disrupts the X-Y complex") and include the functional consequence. Vague language like "regulates" is insufficient.
- Evidence line: assay type(s) | Author et al. Year | PMID | exact figure panel(s), each with a parenthetical describing what that panel shows (e.g. Fig 4B (tautomycin blocks dephosphorylation))
- Confidence line: HIGH / MEDIUM / LOW rating, followed by a written justification that cites specific figure panels and quantitative findings, ending with ECO code(s)
  - HIGH = direct biochemical/enzymatic evidence with purified proteins, OR genetic KO/KI with clear phenotype, OR multiple independent assay types
  - MEDIUM = cellular evidence (co-IP, imaging, pharmacology) without in vitro confirmation; OR evidence from a different species or cell type
  - LOW = inferred, indirect, or single-assay only

For each claim, check all of the following against the paper:
1. Does the cited figure panel exist in this paper?
2. Does the parenthetical description accurately describe what the figure panel shows?
3. Is the assay type correctly named?
4. Are all quantitative values in the confidence justification accurate?
5. Does the biological statement match what the paper actually concludes — not what seems plausible?
6. Is the mechanism specific enough, or does it just say "regulates"?
7. Is the functional consequence stated and accurate?
8. Is the confidence level correct given the evidence criteria above?
9. Is the confidence justification specific — does it cite the right panels and quote real numbers?
10. Is this the right paper for this claim, or does it address something else?
11. Is the evidence direct mechanistic data, or a phenotypic observation (KO, overexpression, pharmacology)?
12. Are there caveats or limitations in the paper that the claim fails to acknowledge?

For each claim respond with **OK**, **WRONG**, or **UNCERTAIN**, followed by a thorough expert explanation. If WRONG or UNCERTAIN, reproduce the full claim block with every correction marked **in bold**.

<CLAIMS>
[paste full claim blocks here]
</CLAIMS>
PEER_EOF
)"
```

---

### Perspective 2 — GO-CAM Curator

```bash
gemini --yolo -p "$(cat <<'CURATOR_EOF'
You are an expert GO-CAM annotation curator. You are reviewing a GO-CAM expert validation document. Be extremely thorough — check every annotation field in every claim against the paper.

Read this paper: gocam_models/<PROCESS>/literature/<PMID>.pdf

Each claim has this structure:
- Claim text: a plain-English biological statement naming the proteins (HGNC symbols in parentheses) and the mechanism. It must state HOW a protein acts (e.g. "phosphorylates", "disrupts the X-Y complex") and include the functional consequence. Vague language like "regulates" is insufficient.
- Evidence line: assay type(s) | Author et al. Year | PMID | exact figure panel(s), each with a parenthetical describing what that panel shows (e.g. Fig 4B (tautomycin blocks dephosphorylation))
- Confidence line: HIGH / MEDIUM / LOW rating, followed by a written justification that cites specific figure panels and quantitative findings, ending with ECO code(s)
  - HIGH = direct biochemical/enzymatic evidence with purified proteins, OR genetic KO/KI with clear phenotype, OR multiple independent assay types
  - MEDIUM = cellular evidence (co-IP, imaging, pharmacology) without in vitro confirmation; OR evidence from a different species or cell type
  - LOW = inferred, indirect, or single-assay only

You enforce these additional GO-CAM annotation rules:
- GO MF terms must NEVER contain "binding" — binding is modelled as has_input, not as MF
- GO MF terms must describe a generalised biochemical activity, never a substrate-specific name (not "syntaxin phosphorylase activity" — use "protein serine/threonine kinase activity")
- ECO codes must match the actual assay in the paper:
  ECO:0001091 = gene knockout | ECO:0007796 = RNAi/shRNA knockdown | ECO:0006003 = electrophysiology |
  ECO:0005027 = confocal/fluorescence microscopy | ECO:0001542 = surface biotinylation | ECO:0000025 = co-immunoprecipitation or pull-down
- RO causal relations: "directly positively/negatively regulates" requires direct mechanistic evidence (enzyme activity, direct binding causing conformational change); "causally upstream of" is for indirect or phenotypic evidence (KO phenotype, pharmacology, overexpression)
- UniProt IDs must match the species studied in this paper

For each claim, check all of the following against the paper:
1. Does the cited figure panel exist in this paper?
2. Does the parenthetical description accurately describe what the figure panel shows?
3. Is the assay type correctly named?
4. Are all quantitative values in the confidence justification accurate?
5. Does the biological statement match what the paper actually concludes?
6. Is the GO MF term appropriate — no binding, no substrate name, correct generalised activity?
7. Does the ECO code match the actual assay performed in this paper?
8. Is the UniProt ID consistent with the species studied in this paper?
9. Is the RO causal relation (directly regulates vs causally upstream of) justified by the directness of the evidence?
10. Is the confidence level correct given the evidence criteria above?
11. Is the confidence justification specific — does it cite the right panels, quote real numbers, and acknowledge limitations?
12. Are there caveats or limitations in the paper that the claim fails to acknowledge?

For each claim respond with **OK**, **WRONG**, or **UNCERTAIN**, followed by a thorough expert explanation of every issue found. If WRONG or UNCERTAIN, reproduce the full claim block with every correction marked **in bold**.

<CLAIMS>
[paste full claim blocks here]
</CLAIMS>
CURATOR_EOF
)"
```

---

### Step 4 — Collect and Write Output

After all Gemini calls complete, write `peer_review_claims.md`. For each claim, write the original block first, then both perspectives beneath it. Preserve Gemini's text verbatim.

---

## Output Format — `peer_review_claims.md`

```markdown
# Gemini Dual Review — <Process Name>
**Date:** <date> | **Claims reviewed:** N | **PMIDs covered:** K

---

## Section [Letter]: [Phase name]

---

### Claim [N]: <brief descriptor>

**Original:**
```
Claim [N]: [full biological statement]

  Evidence: [assay], [Author et al. Year] (PMID: [PMID]), Fig [X] ([what it shows])

  Confidence: [HIGH/MEDIUM/LOW] — [justification. ECO:XXXXX]

  Expert response: OK / WRONG / UNCERTAIN
```

#### Peer Reviewer — [OK / WRONG / UNCERTAIN]

[Gemini's explanation verbatim]

**Corrected claim** *(if WRONG or UNCERTAIN):*
```
Claim [N]: [corrected statement]

  Evidence: [corrected line]

  Confidence: [corrected level] — [corrected justification]

  Expert response: OK / WRONG / UNCERTAIN
```

---

#### GO-CAM Curator — [OK / WRONG / UNCERTAIN]

[Gemini's explanation verbatim]

*(if WRONG or UNCERTAIN, Gemini reproduces the claim with corrections **in bold**)*

---

### Claim [N+1]: ...

---

## Summary Table

| Claim | Peer verdict | Curator verdict |
|---|---|---|
| 1 | OK / WRONG / UNCERTAIN | OK / WRONG / UNCERTAIN |
| 2 | | |
```

---

## Critical Rules

1. **Two Gemini instances per paper** — always launch both in the same message as parallel Bash calls
2. **Batch by PMID** — all claims citing the same paper go into one pair
3. **Pass the full claim block** — never strip it down; Gemini must see the complete claims_template-formatted text
4. **Preserve Gemini output verbatim** — do not paraphrase; format into the output document as written
5. **Corrected claims in claims_template format** — the Gemini prompts instruct this; if Gemini's corrected claim is not in the right format, reformat it to match before writing to the output file
6. **You write the file** — collect outputs and assemble `peer_review_claims.md`; do not ask Gemini to write the file
7. **No synthesis** — present both perspectives side by side; do not add your own verdicts
