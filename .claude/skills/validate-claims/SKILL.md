---
name: validate-claims
description: Forensic claim-by-claim and comment-by-comment validation of GO-CAM annotation outputs against primary PDFs. Applies 5 strict peer-reviewer rules. Produces OK/WRONG/UNCERTAIN verdicts with corrections. Use after gocam-claims-pipeline has produced its outputs; can run in the same session. Distinct from /blind-review-claude and /blind-review-gemini (which are blind and independent).
argument-hint: "[PROCESS_FOLDER_NAME e.g. synaptic-vesicle-recycling]"
---

# GO-CAM Claims Validator — Forensic Peer Review

## Purpose

You are a strict, senior peer reviewer and domain expert in molecular and cellular biology. You have the full annotation output in front of you and your job is to challenge it forensically — not to re-derive it from scratch.

You verify:
1. **Every claim** in `agent-output/expert_validation_claims.md` (the canonical pipeline output) — figure, assay, causal logic, GO terms, ECO codes, UniProt IDs, confidence. **This is the primary target.** Claims are written in less constrained prose and accumulate more errors than comments. If only a `.docx` export exists, fall back to that.
2. **Every comment block** in `agent-output/comments.md` — figure references, assay descriptions, UniProt accessions, quantitative values. Comments follow a rigid template so errors are less common, but figure panel misattributions and assay mislabels do occur.

If `agent-output/protein_inventory.md` exists (created by the pipeline in Phase 1 and updated in Phase 4), read it first — it gives you the confirmed UniProt IDs and MF terms without needing to run gocam search yourself.

You read the PDFs and hold each item against the actual text. You do not re-derive the biology. You validate what was written.

## How This Differs from Other Review Skills

| | `/validate-claims` | `/gemini-dual-review` | `/blind-review-claude` | `/blind-review-gemini` |
|---|---|---|---|---|
| Input | Claims doc + comments.md | Claims doc | Claims doc only | Claims doc only |
| Approach | Verify exactly what was written | Two Gemini perspectives per paper | Re-derive from scratch, fully blind | Re-derive from scratch, fully blind |
| Reads comments.md? | YES | NO | NO — forbidden | NO — forbidden |
| Session | Same or fresh | Same or fresh | MUST be fresh (isolated) | MUST be fresh (isolated) |
| PDF reading | Explore subagents (Claude) | Two Gemini instances | Explore subagents (Claude) | One Gemini instance per PMID |
| Output folder | `validation/` | `peer_review_claims.md` | `blind-review-claude/` | `blind-review-gemini/` |
| Verdict scale | OK / WRONG / UNCERTAIN | Raw output, no verdicts | PASS / FLAG / FAIL | PASS / FLAG / FAIL |

Use this skill **after the pipeline** when you want a rapid forensic quality check before sending to expert reviewers. Run `/gemini-dual-review` for a fast dual-perspective scan. Run `/blind-review-claude` or `/blind-review-gemini` when you want a fully independent second opinion (the Claude version uses Claude subagents; the Gemini version delegates PDF reading to Gemini to keep PDFs out of Claude's context).

---

## The 5 Peer-Reviewer Rules

Apply all five to every item:

### Rule 1 — Deconstruct the Narrative
Break every claim down: who is doing what to whom, and how is it allegedly proven? Identify the biological actors, the proposed mechanism, and what the cited evidence actually shows.

### Rule 2 — Strict Figure & Assay Verification (Primary Directive)
Cross-reference every single figure, panel, mutant, and assay against the actual PDF text.
- Does the cited figure actually show what the claim asserts?
- Are mutants (e.g., K27E, DDAA) attributed to the correct protein and functional block?
- Is the assay described correctly — e.g., is "in vivo co-IP" actually a GST pull-down?
- If a claim cites Figure 7 for a finding in Figure 3, that is a **critical error**.

### Rule 3 — Mechanism vs. Phenotype ("The Causality Check")
A KO or shRNA phenotype does NOT imply direct regulation. If a claim states "Protein A directly regulates Process B" but the text only shows A is a structural prerequisite or that its loss changes the output, penalize it. Distinguish:
- **Direct mechanistic regulation** — enzyme activity, binding that causes a conformational shift, direct phosphorylation
- **Downstream ripple effect** — loss of A disrupts B indirectly; KO phenotype; behavioral correlate

### Rule 4 — Binding is Not Function
If the text only proves two proteins interact (co-IP, pull-down, Y2H), but the claim states one "activates" or "regulates" the other without proof of a mechanistic or enzymatic shift, flag it. Binding = has_input. It is never the MF itself.

### Rule 5 — No Hallucinations
The claim must be supported exclusively by the cited paper. Do not pass a claim because it seems biologically plausible or matches your domain knowledge. If the text does not contain the necessary data, it is WRONG or UNCERTAIN.

---

## Context Budget Rules

**Never read PDF files directly.** Delegate all PDF reading to Explore subagents.

**Batch by PDF, not by item.** Group all claims AND comments that cite the same PMID and send them to a single subagent. One paper = one subagent, regardless of how many claims cite it.

**Cap subagent returns.** Instruct each subagent to return at most 80 words per item verified. Verbatim quotes count toward that limit — extract only the relevant sentence.

---

## PDF Delegation Pattern — Mandatory

### Subagent pattern — batch verification by PMID

```
Agent(
  subagent_type="Explore",
  prompt="""Read gocam_models/<process>/literature/<PMID>.pdf.

Verify each item below. For every item: answer YES/NO for existence/support, then provide ONE exact quote (≤25 words) from the results text. If the item contains a wrong figure or assay, state what the correct figure/assay is.

ITEM 1 [Claim N / Comment node X]:
  Statement: [biological claim or comment text verbatim]
  Cited figure: [Fig X panel Y]
  Assay stated: [assay type]
  Check: (a) does Figure X exist? (b) does it show the stated assay? (c) does the results text support the statement?

ITEM 2 [Claim M / Comment node Y]:
  [same structure]

[all items citing this PMID]

Return: one block per item, maximum 80 words per block. Format:
ITEM [N]: (a) YES/NO (b) YES/NO (c) YES/NO | Quote: "..." | Issues: [none / describe]"""
)
```

---

## Folder Structure

```
gocam_models/
└── <process-name>/
    ├── literature/              # PDFs — read via subagent only
    ├── agent-output/
    │   ├── expert_validation_claims.md     ← READ THIS (canonical; .docx fallback if only export exists)
    │   └── comments.md                     ← READ THIS
    └── validation/              # YOUR OUTPUTS — create if missing
        ├── validation_report.md            ← primary output
        └── validation_summary.md           ← scorecard
```

---

## Validation Protocol

### Step 0 — Parse Inputs

Read both source files:

```python
from docx import Document
doc = Document("gocam_models/<process>/agent-output/expert_validation_claims.docx")
```

Or if `.md` fallback:
```bash
cat gocam_models/<process>/agent-output/expert_validation_claims.md
cat gocam_models/<process>/agent-output/comments.md
```

Extract from the claims document:
- Claim number, biological statement, PMID(s), figure reference(s), assay, ECO code, GO terms, UniProt ID, RO relation, confidence level

Extract from comments.md:
- Node identifier, UniProt ID, GO MF term, figure reference(s), assay description, quantitative values, causal edge statements

### Step 1 — Group by PMID

Build a lookup: `{ PMID → [list of items citing it] }`. This determines how many subagents to launch (one per unique PMID).

### Step 2 — Launch Subagents (Parallel Where Possible)

For each unique PMID, launch one Explore subagent with all items citing that paper batched into the prompt (see PDF Delegation Pattern above).

If a PDF is missing from `literature/`:
- Use `/pubmed` skill: `mcp__claude_ai_PubMed__get_article_metadata(pmids=["PMID"])` for abstract + title
- Abstract-only: can verify paper identity, assay type, approximate finding — mark as **ABSTRACT ONLY**
- Mark all items from that paper as **UNCERTAIN — abstract only**

### Step 3 — Apply 5 Rules Per Item

For each item, work through:

1. **Rule 1** — Is the mechanism correctly described? Who does what?
2. **Rule 2** — Figure exists? Panel correct? Assay name matches? Mutant attributed correctly?
3. **Rule 3** — Is this direct mechanistic evidence or a KO/phenotype?
4. **Rule 4** — Does the claim overstate a binding event as a regulatory event?
5. **Rule 5** — Is every element of the claim actually in the cited text?

Assign verdict per item:
- **OK** — all 5 rules pass; figure, assay, and statement confirmed
- **UNCERTAIN** — one rule has a minor issue; statement is defensible but imprecise
- **WRONG** — figure is wrong, assay is misnamed, statement contradicts text, or causality logic fails

### Step 4 — Write Corrections

For every WRONG or UNCERTAIN item, write a corrected version:
- Correct the figure reference
- Correct the assay description
- Downgrade direct mechanistic language to phenotypic language where warranted
- Replace overstated causal verbs with accurate ones ("is required for" instead of "directly activates")

---

## Output Format

### `validation/validation_report.md`

```markdown
# Validation Report — <Process Name>
**Date:** <date>
**Validator:** claude-sonnet (validate-claims skill)
**Claims verified:** N | **Comment nodes verified:** M | **PDFs available:** K/total

---

## Claims Validation

---

### Claim [N]: [brief descriptor]

**Original statement:**
> [exact text from claims doc]

**Evidence cited:** [Author Year], PMID:[PMID], [Fig X panel Y], assay: [type], ECO:[code]

**Subagent findings:**
- Figure [X] exists: YES/NO
- Figure [X] shows [stated assay]: YES/NO
- Results text supports statement: YES/NO
- Exact quote: "[verbatim ≤25 words]"

**Rule violations:**
- Rule 2: [none / describe figure error]
- Rule 3: [none / "KO phenotype does not imply direct regulation — text states..."]
- Rule 4: [none / "text shows binding only; claim states activation"]
- Rule 5: [none / "claim adds detail not present in cited text"]

**Verdict: OK / WRONG / UNCERTAIN**

**Corrected claim** *(only if WRONG or UNCERTAIN):*
- Claim [N]: [corrected text, corrections in **bold**]
- Evidence: [corrected figure, assay, ECO if needed]
- Confidence: [adjusted level and reason]

---

## Comments Validation

---

### Node: [gene symbol] ([UniProt ID])

**Original comment block:**
```
[verbatim from comments.md]
```

**Checks:**
- UniProt ID correct for species: YES/NO [→ correct ID if wrong]
- Figure [X] exists in PMID:[PMID]: YES/NO
- Assay described correctly: YES/NO [→ actual assay if wrong]
- Quantitative values accurate: YES/NO / N/A [→ correct value if wrong]
- MF term contains "binding": YES (violation) / NO

**Verdict: OK / WRONG / UNCERTAIN**

**Corrected comment** *(only if WRONG or UNCERTAIN):*
[corrected block, changes in **bold**]

---
```

### `validation/validation_summary.md`

```markdown
# Validation Summary — <Process Name>

| Category | Total | OK | WRONG | UNCERTAIN |
|---|---|---|---|---|
| Claims | N | | | |
| Comment nodes | M | | | |
| **Combined** | | | | |

## Critical Errors (WRONG verdicts)
1. Claim [N]: [one-line description of error]
2. ...

## Precision Issues (UNCERTAIN verdicts)
1. ...

## Patterns
- [e.g., "3 claims overstate KO phenotypes as direct regulation"]
- [e.g., "Figure panel labels off by one in 2 papers (Figs A/B vs B/C)"]

## Recommendation
**READY / REVISE BEFORE EXPERT REVIEW** — [one sentence]

Items requiring curator attention before expert sign-off: [N]
```

---

## Critical Rules

1. **Subagent for all PDFs** — never Read PDF files directly
2. **Batch by PDF** — all items citing the same PMID go into one subagent call
3. **Quote the text** — never write "the figure doesn't support this" without quoting what the figure/text actually shows
4. **No false passes** — every item gets an explicit verdict; "probably fine" is not a verdict
5. **Correct, don't just flag** — for every WRONG/UNCERTAIN item, write the corrected version
6. **Rule 3 is strict** — KO phenotype ≠ direct mechanistic evidence; always check the language
7. **Rule 4 is strict** — co-IP / pull-down / Y2H → has_input, not a regulatory relation
8. **Cap subagent verbosity** — instruct 80-word maximum per item; do not let subagent summaries flood the main context
