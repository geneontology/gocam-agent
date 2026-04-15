---
name: gocam-claims-pipeline
description: Run the full GO-CAM literature-backed annotation pipeline. Reads GO-CAM models (OWL/TTL), verifies all claims against primary research PDFs, and produces expert validation documents. Use when starting or continuing a GO-CAM curation project folder.
argument-hint: "[PROCESS_FOLDER_NAME e.g. ampar-endocytosis]"
---

# GO-CAM Claims Pipeline

**Read `gocam_models/annotate_gocam.md` for all detailed instructions, tables, and templates.**
This skill is the orchestration guide. annotate_gocam.md is the reference.

## Pipeline Flow

```
Agent → expert_validation_claims.docx → Expert review → Curator builds GO-CAM in Noctua
```

You NEVER write to Noctua. You NEVER rely on biological knowledge from prior sessions.

## Tools to Load

| When | Tool |
|---|---|
| Always | `/gocam-curator` skill — `gocam search` for UniProt IDs, GO MF/BP/CC terms |
| Always | `/noctua` skill — barista for model export (read-only) |
| ECO lookup | `/eco-validator` skill — live OLS4 query for specific assay codes |
| Output 5 | `/drawio` skill — pathway diagram (requires `gocam_models/network_template_draw.drawio`) |
| New model | `/go-cam-user-guide` skill — Noctua model creation workflow (curator action) |
| Always | OLS MCP — CHEBI term verification |
| Always | `/pubmed` skill — full text (PMC) or abstract when PDFs are missing |
| Always | `/amigo` skill — resolve MGI/MOD IDs; cross-check GO annotations from GO database |
| After Phase 7 | `/evaluate-claims` skill — optional blind quality review before expert sign-off |

## Phases

### Phase 0 — Novel Topic Initiation (skip if `noctua/` TTL exists)
1. Check for existing GO-CAM: `barista list-models --title` / `--gp`
2. Find full-article primary literature via `/pubmed` skill (no abstracts-only)
3. Extract PMID reading list from datamine if present
4. Ask curator to create minimal model skeleton in Noctua (curator action, not agent)
5. Collect user inputs (protein list, slides, images, expert claims) as orientation only

### Phase 1 — Inventory
1. Locate process folder under `gocam_models/`
2. Export model: `barista export-model --model <id> -f gocam-yaml`
3. Detect evidence format (rdfs:comment vs owl:Axiom) — see annotate_gocam.md
4. List all nodes, edges, gene product IRIs, and PMIDs
5. Cross-reference PMIDs against PDFs in `literature/`; flag gaps
6. Read `expert_claims.docx` if present — use as starting framework

### Phase 2 — PDF Verification (node by node, edge by edge)
- Verify every PMID against the actual PDF
- Verify every figure reference exists and shows what is claimed
- Verify assay descriptions match the paper
- Verify quantitative claims
- Confirm UniProt IDs via `gocam search` — never guess
- See annotate_gocam.md for known PMID errors, UniProt reference table, and `gocam search` invocation

### Phase 3 — ECO Code Verification
- Re-derive every ECO code from the paper — never trust input
- Use `/eco-validator` for any assay not in the annotate_gocam.md reference table
- Multiple ECO codes per edge when a paper uses multiple assay types
- See annotate_gocam.md for the full ECO reference table and broad codes to avoid

### Phase 4 — Molecular Function Verification
- Run `gocam search` for every enabled_by gene before assigning MF
- See annotate_gocam.md for MF correction table and strict MF rules (no binding, no substrate names)
- Verify CHEBI IDs via OLS MCP

### Phase 4b — BP and CC Annotation
- Every node needs `part_of` (BP) and `occurs_in` (CC)
- Use `gocam search` to find the most specific terms with IDA/IMP/IEP evidence

### Phase 5 — RO Relation Verification
- Verify each causal edge uses the correct RO relation
- See annotate_gocam.md for the relation selection table

### Phase 6 — Confidence Assessment
- HIGH / MEDIUM / LOW per edge — see annotate_gocam.md for criteria

### Phase 7 — Output Generation

All outputs to `agent-output/`. Read `gocam_models/comments_template.md` and `gocam_models/claims_template.md` before generating.

| Output | File | Notes |
|---|---|---|
| 1 | `comments.md` | Verified rdfs:comment blocks, paste-ready for curator |
| 2 | `expert_validation_claims.docx` | **Primary output** — goes to expert reviewers |
| 3 | `errors_report.md` | Every correction with before/after |
| 4 | `network_topology.md` | Text-based pathway diagram |
| 5 | `pathway_sketch.drawio` | Use `/drawio` skill; check template exists first |

For Output 2: use `python-docx`. Fallback to `.md` if unavailable.
For Output 5: the template is at `gocam_models/network_template_draw.drawio` — read it before running `/drawio`.

## Critical Rules

1. Never write to Noctua — curator builds the GO-CAM after expert sign-off
2. Every PMID must be verified against the actual PDF
3. Every figure reference must exist in the cited paper
4. Every ECO code must be re-derived from the paper
5. UniProt IDs must be confirmed via `gocam search` — never assumed
6. MF must never contain "binding" or a substrate name
7. CHEBI IDs must be verified against OLS
8. Do not invent biology — absent evidence gets flagged, not fabricated
9. Distinguish direct enzymatic evidence from pharmacological/indirect
10. Every correction must be recorded in `errors_report.md`
