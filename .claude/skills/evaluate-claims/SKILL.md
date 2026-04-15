---
name: evaluate-claims
description: Independent blind evaluation of GO-CAM claims documents. Reads an expert_validation_claims.docx (or .md) and verifies every claim against primary PDFs, producing a structured evaluation report. Use after gocam-claims-pipeline has generated its output.
argument-hint: "[PROCESS_FOLDER_NAME e.g. ampar-endocytosis]"
---

# GO-CAM Claims Evaluator — Independent Blind Review

## Purpose

You are an **independent reviewer** performing blind evaluation of GO-CAM annotation claims. You have NOT seen the annotation agent's reasoning, intermediate notes, or drafts. You receive ONLY:

1. The claims document (`agent-output/expert_validation_claims.docx` or `.md`)
2. The primary literature PDFs in `literature/`

You evaluate each claim **from scratch** against the PDFs. You do NOT read `comments.md`, `errors_report.md`, or `network_topology.md` — ever.

**You are a skeptic, not an advocate.** Your job is to find errors, not confirm the annotator's work.

## When to Use

- After `/gocam-claims-pipeline` has produced `expert_validation_claims.docx`
- Before handing the claims document to expert reviewers for sign-off
- When auditing annotation quality

## Pipeline Position

```
gocam-claims-pipeline → expert_validation_claims.docx → [evaluate-claims] → curator → expert review
```

The curator compares the evaluation against the original annotation and resolves discrepancies before expert sign-off.

## Dependencies

| Tool | Purpose |
|---|---|
| OLS MCP server | Independent GO, ECO, CHEBI term verification |
| `/pubmed` skill | Article metadata cross-check for missing PDFs |
| `python-docx` | Reading .docx input (`pip3 install python-docx --break-system-packages` if missing) |

---

## Folder Structure

```
gocam_models/
└── <process-name>/
    ├── literature/              # YOUR ground truth — PDFs
    ├── agent-output/
    │   ├── expert_validation_claims.docx   ← READ THIS
    │   ├── comments.md                     ← DO NOT READ
    │   ├── errors_report.md                ← DO NOT READ
    │   └── network_topology.md             ← DO NOT READ
    └── evaluation/              # YOUR OUTPUT GOES HERE (create if missing)
        ├── evaluation_report.docx
        ├── evaluation_summary.md
        └── discrepancies.md
```

---

## Evaluation Protocol

### Phase 1: Intake

1. Locate `agent-output/expert_validation_claims.docx` (or `.md` fallback)
2. Parse all claims into a structured list: claim number, biological statement, PMID(s), figure(s), ECO code(s), GO term(s), UniProt ID(s), confidence level, RO relation
3. Inventory all PDFs in `literature/`

```python
from docx import Document
doc = Document("agent-output/expert_validation_claims.docx")
# Extract structured claim data from paragraphs
```

### Phase 2: Independent PDF Verification

For EACH claim:

#### 2a. Paper Identity
- Open `literature/<PMID>.pdf`
- Confirm paper exists and matches cited author/year
- If PDF missing: use `/pubmed` skill for metadata; mark claim **UNVERIFIABLE**

#### 2b. Figure Verification
- Navigate to the cited figure
- Does it exist? Does it show what the claim says?
- Write your own description — do not paraphrase the claim

#### 2c. Biological Statement
Read the results section independently. Score as:
- **CONFIRMED** — your reading agrees with the claim
- **PARTIALLY SUPPORTED** — paper supports part of the claim only
- **OVERSTATED** — claim goes beyond what the evidence shows
- **CONTRADICTED** — paper shows something different or opposite
- **UNVERIFIABLE** — PDF not available or figure not found
- **WRONG REFERENCE** — paper does not address this topic

#### 2d. ECO Code
- What assay did the paper actually perform?
- Is the assigned ECO code appropriate?
- Verify term via OLS MCP: `ols-mcp search eco "<assay type>"`

#### 2e. GO Terms
For each GO term in the claim:
- Does the paper demonstrate this specific molecular function/process/component?
- Is any MF term a "binding" term? (GO-CAM rule violation)
- Is any MF term substrate-specific when it should be generic?
- Verify term via OLS MCP: `ols-mcp search go "<term label>"`

#### 2f. Gene Product Identity
Verify UniProt ID is correct for the claimed species:
```bash
curl -s "https://rest.uniprot.org/uniprotkb/<ACCESSION>.json" | \
  python3 -c "import sys,json; d=json.load(sys.stdin); print(d['organism']['scientificName'], [g['geneName']['value'] for g in d.get('genes',[])])"
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

For each gene product, check current GO annotations independently:
```bash
curl -s "https://www.ebi.ac.uk/QuickGO/services/annotation/search?geneProductId=UniProtKB:<ID>&aspect=molecular_function&limit=25"
```

Flag:
- Claims assigning MF terms not in current GO (novel — needs strong evidence)
- Claims missing well-established MF annotations
- NOT annotations that conflict with claims

---

### Phase 5: Output Generation

All outputs to `evaluation/` (create if missing).

#### `evaluation_report.docx` (Primary Output)

Per-claim structured evaluation:
```
EVALUATION REPORT — Independent Blind Review
[Model title] — [Date]

================================================================
CLAIM [N]: [Original biological statement]
----------------------------------------------------------------
Cited: [Author Year], PMID:[PMID], Fig [X]
Assigned ECO: [code] | Confidence: [level]

EVALUATOR FINDING:
  Paper content: [What I actually found in the PDF]
  Figure [X] shows: [My description]

  Biological statement: CONFIRMED / PARTIALLY SUPPORTED / OVERSTATED / CONTRADICTED / UNVERIFIABLE
  ECO code: CORRECT / WRONG → should be [code]
  GO term(s): CORRECT / WRONG → should be [term]
  UniProt ID: CORRECT / WRONG → should be [ID]
  Confidence: AGREE / DISAGREE → my assessment: [level]

  VERDICT: PASS / FLAG / FAIL
  Notes: [specific issues]
================================================================
```

Generate using `python-docx`. Fallback to Markdown if unavailable.

#### `evaluation_summary.md`

```markdown
# Evaluation Summary
**Process**: [name] | **Date**: [date] | **Claims evaluated**: [N] | **PDFs available**: [N]/[N]

## Scorecard
| Verdict | Count | % |
| PASS    |       |   |
| FLAG    |       |   |
| FAIL    |       |   |
| UNVERIFIABLE |  |   |

## Top Issues
1. [Most critical finding]
2. ...

## Recommendation
[APPROVE / REVISE / REJECT] — [one sentence]
```

#### `discrepancies.md`

Tables of every disagreement: biological statement errors, ECO errors, GO term errors, confidence disagreements, missing claims, overclaimed statements.

---

## Critical Rules

1. **BLIND REVIEW** — never read `comments.md`, `errors_report.md`, or `network_topology.md`
2. **PDF is truth** — training knowledge does not count as evidence
3. **No silent passes** — every claim gets an explicit verdict with reasoning
4. **Be specific** — "Figure 3A shows a Western blot of X, not a kinase assay" is useful; "evidence seems weak" is not
5. **Flag novelty, don't penalize it** — new MF not yet in GO needs strong evidence; flag for expert attention
6. **One claim, one verdict** — evaluate exactly what was written

## Verdicts

| Verdict | When |
|---|---|
| **PASS** | Statement confirmed, evidence codes appropriate, GO terms correct |
| **FLAG** | Minor issue (wrong ECO, confidence disagreement, more specific GO term available) |
| **FAIL** | Statement wrong, evidence doesn't support claim, or cited paper is irrelevant |
| **UNVERIFIABLE** | PDF not available |
