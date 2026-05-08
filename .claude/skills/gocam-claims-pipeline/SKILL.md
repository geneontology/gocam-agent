---
name: gocam-claims-pipeline
description: Run the full GO-CAM literature-backed annotation pipeline. Reads GO-CAM models (OWL/TTL), verifies all claims against primary research PDFs, and produces expert validation documents. Use when starting or continuing a GO-CAM curation project folder.
argument-hint: "[PROCESS_FOLDER_NAME e.g. ampar-endocytosis]"
---

# GO-CAM Claims Pipeline

The annotation instructions are split across section files in `workflow/`. **Read on demand — do not read all files at once.**

| File | Read when |
|---|---|
| `workflow/annotate_gocam.md` | Index — read first for navigation |
| `workflow/annotate_gocam_rules.md` | Session start — always |
| `workflow/annotate_gocam_setup.md` | Session start — always |
| `workflow/annotate_gocam_phases_0_2.md` | Before Phases 0–2 |
| `workflow/annotate_gocam_phases_3_6.md` | Before Phase 3 |
| `workflow/annotate_gocam_outputs.md` | Before Phase 7 |

## Context Budget Rules — Read Before Proceeding

**Always save `agent-output/protein_inventory.md` at the end of Phase 1.** This file is your working protein list and is updated in Phase 4 with confirmed UniProt IDs and MF terms. It serves as a checkpoint, a process monitor, and a backup if the session is interrupted.

The pipeline can run in a single session (Phases 0–7, excluding drawio and the post-pipeline review skills) or be split at Phase 2. Both modes are supported:
- **Single session:** proceed continuously; the protein_inventory.md is always there as a reference
- **Split at Phase 2:** end the session after Phase 2 with `protein_inventory.md` saved; resume Phases 3–7 in a later session by reading `agent-output/protein_inventory.md` as your starting inventory

When resuming Phases 3–7 from a saved inventory: read `protein_inventory.md` first, then proceed directly to Phase 3 without repeating Phase 1 or Phase 2.

**Never read PDF files directly.** Each PDF is 2–15 MB in context. Always delegate to a subagent:
```
Agent(subagent_type="Explore", prompt="Read gocam_models/<process>/literature/<PMID>.pdf. Extract: [structured questions]")
```
See `annotate_gocam_phases_0_2.md` for the full subagent patterns for inventory (Phase 1) and targeted verification (Phase 2).

**Never `Read` datamine files.** Use `Grep` to extract PMIDs only:
```bash
grep -oE 'PMID:[0-9]+' gocam_models/<process>/datamine/claims_nodes*.md | sort -u
```

**Never `Read` noctua TTL/OWL files whole.** Use `barista export-model -f gocam-yaml` for inventory. Use `Grep` for PMID/evidence extraction.

**Do not pre-load skills.** Only invoke a skill when you first need it. `/noctua` is never needed for Stage 1. `/drawio` is only needed in Phase 7. `/pubmed`, `/amigo`, `/eco-validator` are on-demand — invoke only when the specific situation arises.

## Two-Stage Workflow

**Stage 1 — Literature only (no Noctua model yet)**
```
PDFs + expert material → Agent → claims doc + comments + draw.io → Expert review
```
Then after agreement: curator builds GO-CAM in Noctua.

**Stage 2 — Model exists (extending/revising)**
```
Noctua model (barista export) + PDFs → Agent → updated claims + corrected comments + errors report
```

Detect which stage applies: does `noctua/` exist with a TTL/OWL file?

You NEVER write to Noctua. You NEVER rely on biological knowledge from prior sessions.

## Tools to Load

| When | Tool |
|---|---|
| Always | `/gocam-curator` skill — `gocam search` for UniProt IDs, GO MF/BP/CC terms |
| Stage 2 only | `/noctua` skill — barista for model export (read-only); **skip entirely for Stage 1** |
| Phase 3 on demand | `/eco-validator` skill — live OLS4 query; only invoke when assay not in quick-reference table |
| Phase 7 only | `/drawio` skill — pathway diagram; do not load before Phase 7 |
| New model | `/go-cam-user-guide` skill — Noctua model creation workflow (curator action) |
| Phase 4 on demand | WebFetch OLS4 — CHEBI term verification: `https://www.ebi.ac.uk/ols4/api/v2/entities?search=CHEBI:<id>&ontologyId=chebi&size=3` |
| Missing PDFs only | `/pubmed` skill — full text (PMC) or abstract; only invoke when a PDF is absent from literature/ |
| On demand | `/amigo` skill — only invoke when an MGI/MOD ID is encountered or gocam search fails |
| After Phase 7 | `/gemini-dual-review` skill — optional dual-perspective Gemini review; can run in same or fresh session |
| After Phase 7 | `/blind-review-claude` skill — optional fully independent blind quality review using Claude; **run in a separate session** |
| After Phase 7 | `/blind-review-gemini` skill — optional fully independent blind quality review using Gemini; **run in a separate session** |

## Phases

### Phase 0 — Determine Stage and Collect Inputs

**Stage 1 (no noctua/ model):**
1. Check `noctua/` — if empty or absent, proceed as Stage 1
2. Check for existing GO-CAM in store anyway: `barista list-models --title` / `--gp`
3. Collect all inputs: PDFs in `literature/`, `expert_claims.docx`, slides, tables, figures
4. If no PDFs yet: use `/pubmed` to build reading list → give curator PMID list for download
5. Orient yourself from expert material (slides, tables, diagrams) — these are hypotheses, not evidence

**Stage 2 (noctua/ model exists):**
1. Export model: `barista export-model --model <id> -f gocam-yaml`
2. Find model ID via `barista list-models --title` if not known
3. Collect PDFs in `literature/`; read `expert_claims.docx` if present

### Phase 1 — Inventory

**Stage 1:** Build the protein/activity list from PDFs and expert material directly. There is no model to export. Delegate each PDF to an Explore subagent (see `annotate_gocam_phases_0_2.md` for the subagent pattern). Collect structured summaries. Extract: gene products, molecular activities, causal relationships, evidence (PMIDs + figures). This becomes your node/edge inventory.

**Stage 2:** Export model via barista. Detect evidence format (rdfs:comment vs owl:Axiom). List all nodes, edges, gene product IRIs, and PMIDs via Grep. Cross-reference PMIDs against PDFs in `literature/`; flag gaps. Read `expert_claims.docx` if present — use as starting framework.

Save `agent-output/protein_inventory.md` at the end of this phase (gene symbol, role from text, PMIDs). Updated in Phase 4 with UniProt IDs and MF terms.

### Phase 2 — PDF Verification (batched by PDF)
- Group all claims/nodes/edges citing the same PMID into one subagent call — never one subagent per claim
- Verify every PMID, figure reference, assay description, and quantitative claim
- Stage 2 only: confirm existing UniProt IDs via `gocam search` — Stage 1 UniProt IDs are assigned in Phase 4
- See `annotate_gocam_phases_0_2.md` for subagent patterns and batching instructions
- Process-specific PMID errors and known UniProt corrections: check `gocam_models/<process>/ANNOTATION_NOTES.md`

### Phase 3 — ECO Code Verification
- Re-derive every ECO code from the paper — never trust input
- Use `/eco-validator` for any assay not in the `annotate_gocam_phases_3_6.md` reference table
- Multiple ECO codes per edge when a paper uses multiple assay types

### Phase 4 — Molecular Function Verification
- Read `protein_inventory.md` first; run `gocam search` for every gene; update inventory with confirmed UniProt ID and MF
- See `annotate_gocam_phases_3_6.md` for strict MF rules (no binding, no substrate names) and ANNOTATION_NOTES.md for process-specific corrections
- Verify CHEBI IDs via WebFetch OLS4

### Phase 4b — BP and CC Annotation
- Every node needs `part_of` (BP) and `occurs_in` (CC)
- Use `gocam search` to find the most specific terms with IDA/IMP/IEP evidence

### Phase 5 — RO Relation Verification
- Verify each causal edge uses the correct RO relation
- See `annotate_gocam_phases_3_6.md` for the relation selection table

### Phase 6 — Confidence Assessment
- HIGH / MEDIUM / LOW per edge — see `annotate_gocam_phases_3_6.md` for criteria

### Phase 7 — Output Generation

All outputs to `agent-output/`. Read `workflow/comments_template.md` and `workflow/claims_template.md` before generating.

| Output | File | Stage 1 | Stage 2 |
|---|---|---|---|
| 1 | `comments.md` | Proposed comments for future Noctua nodes | Corrected rdfs:comment blocks, paste-ready |
| 2 | `expert_validation_claims.md` | **Primary output** — goes to expert reviewers | Updated claims after model review |
| 3 | `errors_report.md` | Not applicable (no existing model to correct) | Every correction with before/after |
| 4 | `network_topology.md` | Text-based pathway diagram (separate file — not embedded in claims doc) | Text-based pathway diagram |
| 5 | `protein_inventory.md` | Created Phase 1, updated Phase 4 — protein list with UniProt IDs and MF terms | Same |
| 6 | `pathway_sketch.drawio` | Use `/drawio` skill — run separately, not part of main pipeline session | Use `/drawio` skill |

For Output 2: write Markdown directly. **Do not generate a `.docx`.** When the curator is ready to distribute the document to expert reviewers, they will explicitly ask for a Word export — only then convert via `python-docx`.
For Output 6: the template is at `workflow/network_template_draw.drawio` — read it before running `/drawio`.

**After Phase 7: stop.** Do not invoke `/blind-review-claude`, `/blind-review-gemini`, `/gemini-dual-review`, or `/validate-claims` automatically. Tell the curator the outputs are ready and that these skills require a separate invocation.

## Critical Rules

1. Never write to Noctua — curator builds the GO-CAM after expert sign-off
2. Never read PDF files directly — always delegate to Explore subagent
3. Never Read datamine files — use Grep to extract PMIDs only
4. Never Read noctua TTL/OWL files whole — use barista export + Grep
5. Every PMID must be verified against the actual PDF (via subagent)
6. Every figure reference must exist in the cited paper
7. Every ECO code must be re-derived from the paper
8. UniProt IDs must be confirmed via `gocam search` — never assumed
9. MF must never contain "binding" or a substrate name
10. CHEBI IDs must be verified against OLS
11. Do not invent biology — absent evidence gets flagged, not fabricated
12. Distinguish direct enzymatic evidence from pharmacological/indirect
13. Every correction must be recorded in `errors_report.md`
14. `/blind-review-claude` and `/blind-review-gemini` must run in a separate session — never in the same session as the pipeline
