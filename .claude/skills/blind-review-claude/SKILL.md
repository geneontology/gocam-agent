---
name: blind-review-claude
description: Independent blind evaluation of GO-CAM claims documents using Claude Explore subagents to read the PDFs. Reads expert_validation_claims.md and verifies every claim against primary PDFs from scratch, producing a structured evaluation report. Use after gocam-claims-pipeline has generated its output. Always run in a fresh session — never in the same session as the pipeline. For a Gemini-powered alternative, see /blind-review-gemini.
argument-hint: "[PROCESS_FOLDER_NAME e.g. ampar-endocytosis]"
---

# GO-CAM Claims — Independent Blind Review (Claude engine)

## Purpose

You are an **independent reviewer** performing blind evaluation of GO-CAM annotation claims. You have NOT seen the annotation agent's reasoning, intermediate notes, or drafts. You receive ONLY:

1. The claims document (`agent-output/expert_validation_claims.md`)
2. The primary literature PDFs in `literature/`

You evaluate each claim **from scratch** against the PDFs. You do NOT read `comments.md`, `errors_report.md`, or `network_topology.md` — ever.

**You are a skeptic, not an advocate.** Your job is to find errors, not confirm the annotator's work.

## Session Isolation — MANDATORY

**This skill must run in a fresh session, separate from the `gocam-claims-pipeline` session.**

Starting fresh guarantees:
- No shared context with the annotation agent's reasoning
- No inherited assumptions about which claims are correct
- Genuine independence of the evaluation

If you find yourself in the same session that ran the pipeline, stop and ask the user to start a new session before continuing.

## When to Use

- After `/gocam-claims-pipeline` has produced `expert_validation_claims.md`
- Before handing the claims document to expert reviewers for sign-off
- When auditing annotation quality independently of `/validate-claims`

## Pipeline Position

```
gocam-claims-pipeline → expert_validation_claims.md → [NEW SESSION] → blind-review-claude → curator → expert review
```

The curator compares the blind-review-claude output against the original annotation and resolves discrepancies before expert sign-off. For an independent Gemini-engine alternative, run `/blind-review-gemini` instead (or in addition).

## Context Budget Rules

**Never read PDF files directly.** Each PDF is 2–15 MB in context. Always delegate to a subagent. The evaluator reads many PDFs — failing to use subagents will thrash the context window.

See PDF Delegation Pattern below.

## Dependencies

| Tool | Purpose |
|---|---|
| OLS4 REST API (WebFetch) | GO, ECO, CHEBI term verification: `https://www.ebi.ac.uk/ols4/api/v2/entities?search=<ID>&ontologyId=<go|eco|chebi>&size=3` |
| `/gocam-curator` skill | UniProt ID + GO MF/BP/CC verification via `gocam search` |
| `/amigo` skill | Independent GO annotation cross-check via `bioentity-annotations` |
| `/pubmed` skill | Article metadata cross-check for missing PDFs |

---

## Folder Structure

```
gocam_models/
└── <process-name>/
    ├── literature/              # YOUR ground truth — PDFs (read via subagent only)
    ├── agent-output/
    │   ├── expert_validation_claims.md     ← READ THIS
    │   ├── comments.md                     ← DO NOT READ
    │   ├── errors_report.md                ← DO NOT READ
    │   └── network_topology.md             ← DO NOT READ
    └── blind-review-claude/            # YOUR OUTPUT GOES HERE (create if missing)
        ├── blind-review-claude_report.md
        ├── blind-review-claude_summary.md
        └── discrepancies.md
```

---

## PDF Delegation Pattern — Mandatory

**Never use the `Read` tool on PDF files.** Delegate all PDF reading to Explore subagents.

### Subagent pattern — per-claim verification

For each claim being evaluated, launch a targeted subagent:

```
Agent(
  subagent_type="Explore",
  prompt="""Read gocam_models/<process>/literature/<PMID>.pdf.

I am independently evaluating this claim:
Claim: [exact biological claim text]
Cited figure: [Fig X panel Y]
Assay type stated: [assay]

As an independent evaluator, check:
1. Does Figure [X][Y] exist in this paper?
2. What does Figure [X][Y] actually show? Describe it in your own words.
3. Does the results section support [specific biological claim]? Quote the relevant passage.
4. Is the stated assay type correct?
5. Are there quantitative results? Quote exact numbers.
6. Does the paper state any caveats or limitations relevant to this claim?
7. Is this the right paper for this claim, or does it address a different topic?

Return: answer to each question with exact quotes from the paper. Do not paraphrase the claim back to me — tell me what the paper says independently."""
)
```

### Subagent pattern — paper identity check

For each PMID, confirm paper identity independently:

```
Agent(
  subagent_type="Explore",
  prompt="""Read gocam_models/<process>/literature/<PMID>.pdf.
Return: title, first author, year, journal, and a 2-sentence summary of the main finding.
Do not return raw text."""
)
```

---

## Evaluation Protocol

### Phase 1: Intake

1. Locate `agent-output/expert_validation_claims.md`
2. Parse all claims into a structured list: claim number, biological statement, PMID(s), figure(s), ECO code(s), GO term(s), UniProt ID(s), confidence level, RO relation
3. Inventory all PDFs in `literature/`

### Phase 2: Independent PDF Verification

For EACH claim, launch a targeted subagent (see PDF Delegation Pattern above). Do not read PDFs yourself.

#### 2a. Paper Identity
- Confirm paper exists and matches cited author/year
- If PDF missing: use `/pubmed` skill for metadata; mark claim **UNVERIFIABLE**

#### 2b. Figure Verification
- Does the cited figure exist?
- Does it show what the claim says?
- Write your own description — do not paraphrase the claim

#### 2c. Biological Statement
Read the results section independently via subagent. Score as:
- **CONFIRMED** — your reading agrees with the claim
- **PARTIALLY SUPPORTED** — paper supports part of the claim only
- **OVERSTATED** — claim goes beyond what the evidence shows
- **CONTRADICTED** — paper shows something different or opposite
- **UNVERIFIABLE** — PDF not available or figure not found
- **WRONG REFERENCE** — paper does not address this topic

#### 2d. ECO Code
- What assay did the paper actually perform?
- Is the assigned ECO code appropriate?
- Verify ECO term via WebFetch OLS4: `https://www.ebi.ac.uk/ols4/api/v2/entities?search=<ECO_ID>&ontologyId=eco&size=3`

#### 2e. GO Terms
For each GO term in the claim:
- Does the paper demonstrate this specific molecular function/process/component?
- Is any MF term a "binding" term? (GO-CAM rule violation)
- Is any MF term substrate-specific when it should be generic?
- Verify GO term via WebFetch OLS4: `https://www.ebi.ac.uk/ols4/api/v2/entities?search=<GO_ID>&ontologyId=go&size=3`

#### 2f. Gene Product Identity
Verify UniProt ID and species using the `/gocam-curator` skill:
```bash
cd gocam-curator
.venv/bin/gocam search <GENE_SYMBOL> --species mouse
```

#### 2g. RO Relation (for edge claims)
- Does evidence support direct or indirect relationship?
- Is the direction correct?
- Is "directly positively regulates" justified, or should it be "causally upstream of"?

#### 2h. Confidence Re-assessment
Assign your own confidence independently:
- **HIGH** — strong, direct evidence found in PDF
- **MEDIUM** — evidence is indirect, different species, or single-assay
- **LOW** — weak or tangential evidence
- **UNSUPPORTED** — no evidence found in cited paper

---

### Phase 3: Cross-Claim Consistency

After evaluating individual claims:
1. Contradictory claims — does claim N contradict claim M?
2. Causal gaps — are there missing links in the pathway?
3. Species mixing — are all gene products from the same organism?
4. Orphan gene products — mentioned but not in any claim?

---

### Phase 4: Independent GO Annotation Check

For each gene product, check current GO annotations:
```bash
cd gocam-curator
.venv/bin/gocam search <GENE_SYMBOL> --species mouse
```

Flag:
- Claims assigning MF terms not in current GO (novel — needs strong evidence)
- Claims missing well-established MF annotations with IDA/IMP evidence
- NOT annotations that conflict with claims

---

### Phase 5: Output Generation

All outputs to `blind-review-claude/` (create if missing).

#### `blind-review-claude/blind-review-claude_report.md` (Primary Output)

Per-claim structured evaluation:
```markdown
# Blind Review Report — <Process Name>
**Date:** <date> | **Reviewer:** Claude (blind-review-claude skill)
**Claims evaluated:** N | **PDFs available:** N/N

---

## Claim [N]: [Original biological statement]

**Cited:** [Author Year], PMID:[PMID], Fig [X] | ECO: [code] | Confidence: [level]

**Paper content:** [What I actually found in the PDF]
**Figure [X] shows:** [My description]

- Biological statement: CONFIRMED / PARTIALLY SUPPORTED / OVERSTATED / CONTRADICTED / UNVERIFIABLE
- ECO code: CORRECT / WRONG → should be [code]
- GO term(s): CORRECT / WRONG → should be [term]
- UniProt ID: CORRECT / WRONG → should be [ID]
- Confidence: AGREE / DISAGREE → my assessment: [level]

**VERDICT: PASS / FLAG / FAIL**
**Notes:** [specific issues]

---
```

#### `blind-review-claude/blind-review-claude_summary.md`

```markdown
# Blind Review Summary
**Process:** [name] | **Date:** [date] | **Claims evaluated:** [N] | **PDFs available:** [N]/[N]

## Scorecard
| Verdict | Count | % |
|---|---|---|
| PASS | | |
| FLAG | | |
| FAIL | | |
| UNVERIFIABLE | | |

## Top Issues
1. [Most critical finding]
2. ...

## Recommendation
[APPROVE / REVISE / REJECT] — [one sentence]
```

#### `blind-review-claude/discrepancies.md`

Tables of every disagreement: biological statement errors, ECO errors, GO term errors, confidence disagreements, missing claims, overclaimed statements.

---

## Critical Rules

1. **FRESH SESSION** — never run in the same session as `gocam-claims-pipeline`
2. **BLIND REVIEW** — never read `comments.md`, `errors_report.md`, or `network_topology.md`
3. **SUBAGENT FOR ALL PDFs** — never Read PDF files directly; delegate to Explore subagent
4. **PDF is truth** — training knowledge does not count as evidence
5. **No silent passes** — every claim gets an explicit verdict with reasoning
6. **Be specific** — "Figure 3A shows a Western blot of X, not a kinase assay" is useful; "evidence seems weak" is not
7. **Flag novelty, don't penalize it** — new MF not yet in GO needs strong evidence; flag for expert attention
8. **One claim, one verdict** — evaluate exactly what was written

## Verdicts

| Verdict | When |
|---|---|
| **PASS** | Statement confirmed, evidence codes appropriate, GO terms correct |
| **FLAG** | Minor issue (wrong ECO, confidence disagreement, more specific GO term available) |
| **FAIL** | Statement wrong, evidence doesn't support claim, or cited paper is irrelevant |
| **UNVERIFIABLE** | PDF not available |
