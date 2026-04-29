---
name: gocam-curator
description: Use whenever you need to look up gene/protein annotations (UniProt ID, GO MF/BP/CC terms, SynGO annotations, ECO evidence codes) or run the gocam-curator extraction pipeline. Provides the search command and pipeline commands for the gocam-curator CLI tool.
---

# GO-CAM Curator Tool

A Python CLI (`gocam`) for database lookups, entity extraction, GO/ECO mapping, and expert validation document generation. No LLM is involved in lookups — all database queries are pure REST API calls.

## Invocation

```bash
# Always invoke via the venv in gocam-agent:
cd /Users/jobberkhout/Projects/gocam-agent/gocam-curator
.venv/bin/gocam <command> [options]
```

The venv's editable install points to `~/Projects/gocam-curator/src` — the user's original source. Changes there are picked up immediately.

---

## `gocam search` — The Core Lookup Tool

**Use this command during every GO-CAM annotation session** whenever you need to:
- Confirm a gene's UniProt ID for a given species
- Verify that a GO MF term is the established annotation for a protein (not assumed from domain knowledge)
- Find what GO MF/BP/CC terms are already curated for a gene in UniProt + QuickGO
- Check if SynGO has annotations for a synaptic gene

```bash
.venv/bin/gocam search <GENE_SYMBOL> --species mouse
```

Species options: `mouse` (default, taxon:10090), `human` (9606), `rat` (10116), `fly`, `worm`, `zebrafish`, `yeast`

### Examples

```bash
.venv/bin/gocam search Rab3a --species mouse
.venv/bin/gocam search Syt1 --species mouse
.venv/bin/gocam search SNAP25 --species mouse
.venv/bin/gocam search Stxbp1 --species mouse
```

### What the output contains

- **UniProt ID** — confirmed accession for that gene + species
- **Protein name and function summary** (UniProt)
- **GO annotations table** — all MF, BP, CC annotations with evidence codes (IDA, IMP, IPI, ISO, IEA, etc.)
- **SynGO annotations** where present

### How to read the MF annotations

Prefer annotations with experimental evidence:
- `IDA` (inferred from direct assay) — strongest
- `IMP` (inferred from mutant phenotype)
- `IPI` (inferred from physical interaction)
- `ISO`, `ISS` (inferred by similarity) — weaker, use with caution
- `IEA` (electronic annotation) — do not rely on for MF verification

### Where results are saved

Every search automatically saves to:
- `gocam-curator/searches/<GENE>.md` — human-readable
- `gocam-curator/searches/<GENE>.json` — full data for programmatic use

---

## When to Run `gocam search` During Annotation

### Phase 3 — MF verification (mandatory)

For **every** `enabled_by` node in the model:

1. Run `gocam search <gene> --species mouse`
2. Compare the GO MF term used in the model against the returned MF annotations
3. If the model's MF term does not appear in the search results with IDA/IMP evidence: flag it in `errors_report.md`
4. Use the confirmed UniProt ID (not the MGI ID) when writing node comments

This replaces relying on domain knowledge for MF term correctness. The search result is the ground truth.

### Before writing node comments

Run the search to get the confirmed UniProt accession. Node comment format requires `UniProt: <ID>` — never guess this.

### When encountering an unfamiliar gene product

Run the search immediately. Do not proceed based on assumed identity.

---

## Pipeline Commands (Phases 2–5)

These are used when running the full extraction pipeline from input files (papers, slides, cartoons). They are separate from the annotation pipeline in `annotate_gocam.md`.

| Command | Phase | Input | Output |
|---|---|---|---|
| `gocam init <name>` | Setup | — | `processes/<name>/` workspace |
| `gocam extract <file>` | 2 | .txt/.pdf/.png/.pptx | `extractions/*.json` |
| `gocam extract-all` | 2 | all files in `input/` | `extractions/*.json` |
| `gocam validate` | 4b | `extractions/` | `validation/validated_claims.json` |
| `gocam narrative` | 5 | `validation/` | `narratives/claims_*.md` |
| `gocam interpret` | 6 | `validation/` | `interpretation/suggestions.md` |
| `gocam status` | — | all processes | Rich table summary |
| `gocam enrich <process>` | — | process name | new PubMed literature extracted |

### Key design rules (enforced in all pipeline prompts)

- **No binding as MF**: binding terms are never molecular functions — they become `has_input` edges
- **All GO IDs unverified by default**: LLM suggestions are marked unverified until `gocam validate` checks them against QuickGO/UniProt/EBI
- **Extraction ≠ translation**: Phase 2 extracts what text/images say; Phase 4 maps that to GO terms. These are intentionally separate steps to prevent GO ID hallucination

---

## External APIs Used (no authentication required)

```
QuickGO  — GO term verification
  GET https://www.ebi.ac.uk/QuickGO/services/ontology/go/terms/{GO_ID}

UniProt  — protein + GO annotation lookup
  GET https://rest.uniprot.org/uniprotkb/search?query=gene:{SYMBOL}+organism_id:{TAXON}

OLS/EBI  — ECO code verification
  GET https://www.ebi.ac.uk/ols4/api/ontologies/eco/terms?iri=...

SynGO    — synaptic gene annotation
  (queried automatically by gocam search for synaptic genes)
```

---

## Troubleshooting

**`ModuleNotFoundError` when running gocam:**
The venv editable install points to `~/Projects/gocam-curator/src`. If the original project has been moved or the install broken:
```bash
cd /Users/jobberkhout/Projects/gocam-agent/gocam-curator
.venv/bin/pip install -e /Users/jobberkhout/Projects/gocam-curator
```

**Search returns no results for a gene:**
Try alternate capitalizations (`RAB3A`, `Rab3a`, `rab3a`) or use the human ortholog with `--species human` to confirm the gene exists, then retry with `--species mouse`.

**`gocam search` not found:**
Run from the `gocam-agent/gocam-curator/` directory, or use the full path:
```bash
/Users/jobberkhout/Projects/gocam-agent/gocam-curator/.venv/bin/gocam search Syt1
```
