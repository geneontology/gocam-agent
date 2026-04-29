# GOCAM-AGENT

Your job is to assist curators with planning, searching, creating, reviewing, and annotating GO-CAMs.

## Skills

Use the following skills:

* /noctua — access the GO-CAM store (barista CLI for model export, creation, editing)
* /gocam-best-practice — annotation guidelines for MF types, complexes, adaptors, sequestering proteins
* /gocam-curator — look up gene/protein annotations (UniProt ID, GO MF/BP/CC terms, SynGO)
* /eco-validator — find the most specific ECO code for any assay type via live OLS4 API search
* /go-cam-user-guide — official GO Consortium workflow for creating new models from scratch
* /drawio — generate a .drawio pathway diagram from a claims document (requires workflow/network_template_draw.drawio)
* /gocam-claims-pipeline — full annotation pipeline: verify claims against PDFs, produce expert validation documents
* /validate-claims — forensic claim-by-claim and comment-by-comment verification; strict peer-reviewer rules; OK/WRONG/UNCERTAIN with corrections; outputs to validation/
* /gemini-dual-review — two parallel Gemini instances per paper (peer reviewer + GO-CAM curator perspectives); raw dual output to peer_review_claims.md; no synthesis verdicts
* /blind-review-claude — independent blind re-evaluation using Claude Explore subagents; PASS/FLAG/FAIL verdicts; outputs to blind-review-claude/; must run in a fresh session
* /blind-review-gemini — independent blind re-evaluation using Gemini (one Gemini per PMID, single perspective); PASS/FLAG/FAIL verdicts; outputs to blind-review-gemini/; must run in a fresh session
* /amigo — search GO bioentities and annotations directly from the GO database; resolves MGI/MOD/ComplexPortal IDs
* /pubmed — fetch full-text articles and metadata from PubMed/PMC when PDFs are missing

When making any kinds of queries you MUST use the barista client (see the /noctua skill). You must never query the triplestore or make direct API calls. If you need help, ask the user.

## Literature-Based Annotation Pipeline

When the user asks you to annotate a GO-CAM model, verify claims against papers, produce comments, or generate a claims document:

1. Invoke the `/gocam-claims-pipeline` skill — it contains the complete pipeline instructions
2. Read `workflow/comments_template.md` — the comment format to follow for every node and edge
3. Read `workflow/claims_template.md` — the claims document format to follow
4. Navigate to the specific process folder (e.g., `gocam_models/ampar-endocytosis/`)
5. Follow the pipeline phases defined in the skill

### What the annotation pipeline produces

All outputs go in the process's `agent-output/` subfolder:
- `expert_validation_claims.md` — claims document for expert review (primary output). A `.docx` is generated only when the curator explicitly asks for an export.
- `comments.md` — verified rdfs:comment blocks for all nodes and edges, ready for the curator to paste into Noctua
- `errors_report.md` — all corrections made, with before/after
- `network_topology.md` — text-based pathway diagram
- `pathway_sketch.drawio` — visual pathway diagram (use /drawio skill; requires workflow/network_template_draw.drawio)

### Key annotation rules

- Never write or modify OWL/TTL files — the curator uploads to Noctua manually
- PDFs in `literature/` are the source of truth — never trust datamined files without PDF verification
- MF must never contain "binding" — binding is modeled as has_input on the node
- Read the OWL/TTL in `noctua/` to understand the current model state, but do not edit those files
- If an `expert_claims.docx` exists in the process folder, use it as your starting framework

## Project Structure

```
workflow/                            # Pipeline instructions and templates (read by skills, not edited per-process)
  annotate_gocam.md                  # Index of pipeline section files (read first; per-phase files referenced from here)
  annotate_gocam_setup.md            # Identity, folder structure, GO-CAM concepts (session start)
  annotate_gocam_rules.md            # 12 critical rules + strict MF rules (session start)
  annotate_gocam_phases_0_2.md       # Phases 0–2: stage detection, inventory, PDF verification
  annotate_gocam_phases_3_6.md       # Phases 3–6: ECO, MF/BP/CC, RO relations, confidence
  annotate_gocam_outputs.md          # Phase 7: output generation
  comments_template.md               # Comment format template
  claims_template.md                 # Claims document format template
  network_template_draw.drawio       # Shape palette template for /drawio skill
gocam_models/                        # Per-process data and outputs (one folder per pathway)
  <process-name>/                    # E.g. ampar-endocytosis
    noctua/                          #   OWL/TTL model files (INPUT ONLY — never write here)
    literature/                      #   PDFs named by PMID (curator places these)
    datamine/                        #   Pipeline extraction outputs (noisy hints)
    agent-output/                    #   Claims pipeline outputs
    validation/                      #   validate-claims outputs (forensic peer review)
    blind-review-claude/             #   /blind-review-claude outputs (independent review, Claude engine)
    blind-review-gemini/             #   /blind-review-gemini outputs (independent review, Gemini engine)
    peer_review_claims.md            #   gemini-dual-review output (dual perspective, no verdicts)
    expert_claims.docx               #   Optional existing curated claims
prompts/                             # Standalone Gemini prompt drafts (orphan; not currently sourced by skills)
gocam-curator/                       # Extraction pipeline (separate tool)
  CLAUDE.md                          #   Its own instructions
  .venv/bin/gocam                    #   CLI for UniProt/QuickGO/SynGO lookups
scripts/                             # Ad-hoc helper scripts and their data dumps
  data/                              #   JSON / text dumps produced by scripts (gitignore candidate)
```

