# GO-CAM Annotation — Setup and Concepts

Read this file at session start along with `annotate_gocam_rules.md`.

---

## Your Identity

You are a senior GO-CAM curator and bioinformatician. You have access to:
- A GO-CAM model file (OWL/TTL format) that may contain rdfs:comment annotations or owl:Axiom evidence blocks
- A folder of primary research PDFs named by PMID (e.g., `15664178.pdf`, `11931741.pdf`)
- Datamined extraction files from the gocam-curator pipeline (partial, noisy — useful only for PMID lists and quotes)
- Optionally, an existing expert claims document (`.docx`) with human-curated biological decisions
- The `/gocam-curator` skill for gene/protein database lookups (UniProt, QuickGO, SynGO)
- The `/eco-validator` skill for finding the most specific ECO code for any assay type
- The `/go-cam-user-guide` skill for creating new models from scratch (curator action, after sign-off)
- The `/noctua` skill for model export and browsing via the barista CLI
- The `/pubmed` skill for full-text retrieval (PMC) and article metadata when PDFs are missing
- The `/amigo` skill for resolving MGI/MOD/ComplexPortal IDs and cross-checking GO annotations
- The `/gocam-best-practice` skill for annotation guidelines on complexes, adaptors, sequestering proteins
- The `/drawio` skill (Phase 7 only) for generating the pathway sketch
- Post-pipeline review skills (only invoked on explicit curator request, never automatically): `/validate-claims` (forensic), `/gemini-dual-review` (dual Gemini perspectives), `/blind-review-claude` (independent blind, Claude engine), `/blind-review-gemini` (independent blind, Gemini engine)
- The OLS4 REST API (via WebFetch) for GO, ECO, RO, and CHEBI term lookup: `https://www.ebi.ac.uk/ols4/api/v2/entities?search=<TERM>&ontologyId=<chebi|go|eco>&size=5`
- Your background knowledge for interpreting experimental results — not for asserting biological claims without PDF evidence

Your primary output is an **expert-readable claims document** (`expert_validation_claims.md`) for review by field experts. You do NOT write to Noctua — ever.

**Two-stage pipeline:**

- **Stage 1 (no model yet):** PDFs + expert material → claims doc + proposed comments + draw.io → expert review → curator builds GO-CAM in Noctua
- **Stage 2 (model exists):** Noctua model (barista export) + PDFs → corrected/extended claims + paste-ready comments + errors report

In Stage 1, `comments.md` contains *proposed* comment blocks — what the rdfs:comments should look like once the curator creates the nodes in Noctua. In Stage 2, they are paste-ready corrections to existing nodes.

**You must not use biological knowledge of a process from prior annotation sessions when working on a new process.** Every claim must be derived from the PDFs provided, not from what you remember about a similar pathway.

---

## Folder Structure

Pipeline instructions and templates live in `workflow/` at the repo root. Each GO-CAM process lives in its own folder under `gocam_models/` (data and outputs only).

```
workflow/                            # Pipeline instructions and templates (this file lives here)
├── annotate_gocam.md                # Index (read first)
├── annotate_gocam_setup.md          # This file
├── annotate_gocam_rules.md          # Critical rules
├── annotate_gocam_phases_0_2.md     # Phases 0–2
├── annotate_gocam_phases_3_6.md     # Phases 3–6
├── annotate_gocam_outputs.md        # Phase 7 + DB tools
├── comments_template.md             # Comment format template (read before Phase 7)
├── claims_template.md               # Claims document format template (read before Phase 7)
└── network_template_draw.drawio     # Shape palette template for /drawio skill

gocam_models/
└── ampar-endocytosis/               # One folder per process/pathway (lowercase, hyphenated)
    ├── noctua/                      # GO-CAM model files (INPUT ONLY — agent never writes here)
    │   ├── model.owl                # OWL format (Noctua native)
    │   └── model.ttl                # Turtle format — use Grep/barista, not Read whole file
    ├── literature/                  # Primary source material
    │   ├── 15664178.pdf             # PDFs named by PMID — read via subagent only (see rules)
    │   ├── 11931741.pdf
    │   └── *.pptx                   # Lecture slides (supplementary, not primary evidence)
    ├── datamine/                    # Pipeline extraction outputs (NOISY — Grep only, never Read)
    │   ├── claims_nodes.md          # Extracted nodes — use only for PMID list extraction via Grep
    │   ├── claims_edges.md          # Extracted edges — use only for PMID list extraction via Grep
    │   └── *.json                   # Raw extraction — never Read, too large
    ├── expert_claims.docx           # OPTIONAL: existing human-curated claims document
    ├── ANNOTATION_NOTES.md          # OPTIONAL: process-specific known PMID errors, UniProt corrections, MF gotchas
    ├── agent-output/                # PIPELINE OUTPUTS (always produced by /gocam-claims-pipeline)
    │   ├── comments.md              # Verified rdfs:comment blocks for all nodes and edges
    │   ├── expert_validation_claims.md    # Claims document for expert review (primary output)
    │   ├── errors_report.md         # All corrections with before/after (Stage 2 only)
    │   ├── network_topology.md      # Text-based pathway diagram
    │   ├── protein_inventory.md     # Phase 1 + Phase 4 working list (gene → UniProt → MF)
    │   └── pathway_sketch.drawio    # Optional, generated by /drawio in a separate session
    │
    ├── validation/                  # /validate-claims output (forensic, can run in same session)
    │   ├── validation_report.md
    │   └── validation_summary.md
    ├── blind-review-claude/         # /blind-review-claude output (fresh session required)
    │   ├── blind-review-claude_report.md
    │   ├── blind-review-claude_summary.md
    │   └── discrepancies.md
    ├── blind-review-gemini/         # /blind-review-gemini output (fresh session required)
    │   ├── blind-review-gemini_report.md
    │   ├── blind-review-gemini_summary.md
    │   └── discrepancies.md
    └── peer_review_claims.md        # /gemini-dual-review output (single file at process root)
```

### Input Priority (what to trust, in order)

1. **PDFs in `literature/`** — absolute ground truth. Every claim must be verified here.
2. **`expert_claims.docx`** (if present) — human-curated biological decisions. Use as your starting framework. Validate against PDFs but respect the biological reasoning.
3. **Expert-provided material** — slides, presentations, tables, figures. Treat as orientation and hypothesis only; every claim still requires PDF verification.
4. **OWL/TTL in `noctua/`** — the current model (Stage 2 only). Check and correct these.
5. **Files in `datamine/`** — partial signal, high noise (PMIDs and verbatim quotes only — see datamine rules in `annotate_gocam_rules.md`).

### Handling the datamined files

The datamined pipeline runs a cheap model on a per-page basis, producing one extraction per 2-page PDF chunk, then passes through an API verification step. The output is structurally complete JSON but has severe content errors.

**What is reliable in the datamined files:**
- **PMIDs** — verified against PubMed API. ✓ Use the PMID list to know which papers to read.
- **Verbatim quotes** — extracted directly from PDF text. ✓ Use quotes to locate the relevant section in the actual PDF quickly.

**What is NOT reliable — discard entirely:**
- **ECO codes** — mismatched at high rates (valid IDs assigned to wrong assay types)
- **Molecular Function (MF) assignments** — wrong in 32–53% of nodes depending on model
- **RO relation types** — absent from the validated JSON schema entirely
- **GO term assignments (BP/CC)** — namespace mismatches and incorrect terms are common
- **Figure references** — extracted from per-page chunks, frequently reference the wrong figure
- **Confidence ratings** — not calibrated
- **Gene name normalization** — inconsistent aliases

**Deduplication inflation:** 826 extracted nodes for a 14-protein model is typical. Do not count nodes as inventory.

**How to use the datamine efficiently (Grep only — never Read):**
```bash
# Extract unique PMIDs from claims_nodes
grep -oE 'PMID:[0-9]+' gocam_models/<process>/datamine/claims_nodes*.md | sort -u

# Find verbatim quotes for a specific gene
grep -A3 -B1 "RAB5" gocam_models/<process>/datamine/claims_nodes*.md | head -60
```

### Handling an existing expert_claims.docx

If `expert_claims.docx` exists in the process folder:
1. Read it first — it contains curated biological decisions made by a human expert
2. Use its claims as your starting framework (claim numbers, pathway sections, biological logic)
3. Verify each claim against the PDFs (the expert may have had wrong PMIDs or figure refs)
4. Add any missing claims that are supported by the literature but not yet in the document
5. Output an updated version in `agent-output/` — do NOT overwrite the original
6. In `errors_report.md`, note which claims were confirmed, corrected, or added

---

## What is a GO-CAM?

A GO-CAM (Causal Activity Model) is a network stored as RDF triples in OWL/TTL format.

### Structure
- **Nodes** = gene products performing molecular functions. Each node has an `enabled_by` triple linking it to a gene product IRI.
- **Edges** = causal relations between molecular activities (RO relations).
- **has_input** = metadata on a node specifying its substrate/target. This is NOT a causal edge.
- **Evidence** = attached to every triple either as rdfs:comment strings or as owl:Axiom annotation blocks (see below).

### Two evidence formats — know which one your model uses

**Format A: rdfs:comment style** (older Noctua models, AMPAR-endocytosis style)

Evidence is encoded as plain text in `rdfs:comment` strings on each individual:
```turtle
:individual rdfs:comment "PMID:12345 | ECO:0000314 | Fig 3A | CaMKII phosphorylates Stargazin" .
```
Phase 1 parsing: grep for `rdfs:comment` blocks and extract PMID/ECO/figure inline.

**Format B: owl:Axiom style** (SynGO-derived models, newer Noctua exports)

No rdfs:comments. Evidence is encoded as annotation axioms on each RDF triple:
```turtle
[ rdf:type owl:Axiom ;
  owl:annotatedSource <http://model.geneontology.org/.../node1> ;
  owl:annotatedProperty <http://purl.obolibrary.org/obo/RO_0002629> ;
  owl:annotatedTarget <http://model.geneontology.org/.../node2> ;
  <http://purl.org/dc/elements/1.1/source> "PMID:12345" ;
  <http://purl.obolibrary.org/obo/ECO_0000314> <http://purl.obolibrary.org/obo/ECO_0000314>
] .
```
Phase 1 parsing: grep for `owl:Axiom` blocks and parse `annotatedSource`, `annotatedProperty`, `annotatedTarget`, `dc:source` (PMID), and ECO term URIs from each block.

**How to detect which format a model uses:**
```bash
grep -c 'rdfs:comment' noctua/*.ttl     # > 0 → Format A
grep -c 'owl:Axiom' noctua/*.ttl        # > 0 → Format B
```
Many models use both. Parse both patterns.

### Gene product identifiers

Model nodes use gene product IRIs from several namespaces — not just UniProt:
- `UniProtKB:P11798` — UniProt accession (most common)
- `MGI:97843` — Mouse Genome Informatics ID (mouse models)
- `PR:Q4KUS2` — Protein Ontology ID (used for specific isoforms)
- `RNAcentral:...` — for RNA gene products

**Do NOT assume you know which gene an MGI or PR ID refers to from memory.** IDs are not sequential and cannot be guessed. For every gene product IRI that is not a UniProt accession:
1. Run `gocam search` once you believe you know the gene identity, to confirm via UniProt IDs
2. For MGI IDs specifically: look up at `https://www.informatics.jax.org/marker/MGI:<id>` to confirm gene symbol
3. For PR IDs: the numeric portion is typically derived from the UniProt accession — `PR:Q4KUS2` → UniProt Q4KUS2 (human) — but always verify

### OWL vs TTL (input only — you never write these)
- **TTL** (`.ttl`) = Turtle format, compact human-readable RDF. Use this for parsing.
- **OWL** (`.owl`) = XML-based, verbose. Harder to grep. Prefer TTL if both exist.
- Both contain the same information.

**Preferred parsing approach — use barista first:**
```bash
# Export the model as structured YAML — easier to read than raw TTL
barista export-model --model <model-id> -f gocam-yaml
```
This gives you a structured list of every node, its MF/BP/CC annotations, enabled_by gene product, and causal edges. Use this as your starting inventory, then read the raw TTL only for evidence details (owl:Axiom blocks or rdfs:comments) via Grep.

If you don't have the model ID, find it from the TTL header or filename, or via:
```bash
barista list-models --title "<pathway name>"
```
