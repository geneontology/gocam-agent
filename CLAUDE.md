# GOCAM-AGENT

Your job is to assist curators with planning, searching, creating, reviewing, and annotating GO-CAMs.

## Skills

Use the following skills:

* /noctua — access the GO-CAM store (barista CLI for model export, creation, editing)
* /gocam-best-practice — annotation guidelines for MF types, complexes, adaptors, sequestering proteins
* /gocam-curator — look up gene/protein annotations (UniProt ID, GO MF/BP/CC terms, SynGO)
* /eco-validator — find the most specific ECO code for any assay type via live OLS4 API search
* /go-cam-user-guide — official GO Consortium workflow for creating new models from scratch
* /drawio — generate a .drawio pathway diagram from a claims document (requires gocam_models/network_template_draw.drawio)
* /gocam-claims-pipeline — full annotation pipeline: verify claims against PDFs, produce expert validation documents
* /evaluate-claims — independent blind review of a claims document; produces PASS/FLAG/FAIL verdicts per claim
* /amigo — search GO bioentities and annotations directly from the GO database; resolves MGI/MOD/ComplexPortal IDs
* /pubmed — fetch full-text articles and metadata from PubMed/PMC when PDFs are missing

When making any kinds of queries you MUST use the barista client (see the /noctua skill). You must never query the triplestore or make direct API calls. If you need help, ask the user.

## Literature-Based Annotation Pipeline

When the user asks you to annotate a GO-CAM model, verify claims against papers, produce comments, or generate a claims document:

1. Invoke the `/gocam-claims-pipeline` skill — it contains the complete pipeline instructions
2. Read `gocam_models/comments_template.md` — the comment format to follow for every node and edge
3. Read `gocam_models/claims_template.md` — the claims document format to follow
4. Navigate to the specific process folder (e.g., `gocam_models/ampar-endocytosis/`)
5. Follow the pipeline phases defined in the skill

### What the annotation pipeline produces

All outputs go in the process's `agent-output/` subfolder:
- `expert_validation_claims.docx` — claims document for expert review (primary output)
- `comments.md` — verified rdfs:comment blocks for all nodes and edges, ready for the curator to paste into Noctua
- `errors_report.md` — all corrections made, with before/after
- `network_topology.md` — text-based pathway diagram
- `pathway_sketch.drawio` — visual pathway diagram (use /drawio skill; requires gocam_models/network_template_draw.drawio)

### Key annotation rules

- Never write or modify OWL/TTL files — the curator uploads to Noctua manually
- PDFs in `literature/` are the source of truth — never trust datamined files without PDF verification
- MF must never contain "binding" — binding is modeled as has_input on the node
- Read the OWL/TTL in `noctua/` to understand the current model state, but do not edit those files
- If an `expert_claims.docx` exists in the process folder, use it as your starting framework

## Project Structure

```
gocam_models/                        # Active workspace for annotation
  annotate_gocam.md                  # Annotation pipeline instructions (detailed reference)
  comments_template.md               # Comment format template
  claims_template.md                 # Claims document format template
  network_template_draw.drawio       # Shape palette template for /drawio skill
  <process-name>/                    # One folder per pathway (e.g. ampar-endocytosis)
    noctua/                          #   OWL/TTL model files (INPUT ONLY — never write here)
    literature/                      #   PDFs named by PMID (curator places these)
    datamine/                        #   Pipeline extraction outputs (noisy hints)
    agent-output/                    #   Claims pipeline outputs
    evaluation/                      #   evaluate-claims outputs (blind review)
    expert_claims.docx               #   Optional existing curated claims
gocam-curator/                       # Extraction pipeline (separate tool)
  CLAUDE.md                          #   Its own instructions
  .venv/bin/gocam                    #   CLI for UniProt/QuickGO/SynGO lookups
```

