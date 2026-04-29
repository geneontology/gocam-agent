# GO-CAM Annotation — Phases 0, 1, and 2

Read this file before starting Phase 0. Also read `annotate_gocam_rules.md` and `annotate_gocam_setup.md` first if you haven't already.

---

## PDF Reading — Mandatory Subagent Delegation

**Never use the `Read` tool directly on PDF files.** PDF binary content expands to 2–15 MB per file in the context window. Reading 20+ PDFs sequentially fills the context and causes autocompact thrashing within a single session.

**Rule: All PDF reading must be delegated to an Explore subagent. The main agent receives only structured text summaries (~1–5 KB per PDF).**

### Subagent pattern — inventory pass (Phase 1, batch mode)

Launch one subagent per PDF, in parallel where possible. Keep returns lean — quantitative results are collected in Phase 2 targeted passes, not here.

```
Agent(
  subagent_type="Explore",
  prompt="""Read gocam_models/<process>/literature/<PMID>.pdf. Extract ONLY:
1. Title, first author, year, journal (one line)
2. Gene products mentioned: symbol, organism, brief role (one line each)
3. Molecular activities: which protein does what, which figure cited (one line each)
4. Causal relationships: A → B, mechanism, figure reference (one line each)
5. Assay types used: list each assay name only (no descriptions)

Return as structured bullet points. Maximum 400 words total.
Do NOT include: quantitative values, figure descriptions, methods details, abstract text."""
)
```

### Subagent pattern — claim verification (Phase 2, targeted mode)

**Batch by PDF, not by claim.** Group all claims that cite the same PMID and verify them in a single subagent call. Never launch one subagent per claim — a paper cited 5 times should produce exactly 1 subagent, not 5.

```
Agent(
  subagent_type="Explore",
  prompt="""Read gocam_models/<process>/literature/<PMID>.pdf. Verify ALL of the following claims:

CLAIM 1: [biological claim] | Figure: [Fig X] | Assay: [assay type]
CLAIM 2: [biological claim] | Figure: [Fig Y] | Assay: [assay type]
CLAIM 3: [biological claim] | Figure: [Fig Z] | Assay: [assay type]
[add all claims citing this PMID]

For each claim answer:
1. Does the cited figure exist? YES/NO
2. Does it show the stated assay? YES/NO
3. Does the results text support the claim? YES/NO + one exact quote (≤30 words)
4. Quantitative values if any (exact numbers only)

Format: one block per claim. Maximum 60 words per claim block."""
)
```

The PDF binary never enters the main context window. The subagent returns only structured findings.

---

## Phase 0: Determine Stage and Collect Inputs

### 0a. Confirm or create the process folder

If the curator is starting a brand-new project, the folder may not exist yet. Confirm the layout (and create it if needed) before doing anything else:

```bash
PROCESS=<process>   # lowercase, hyphenated, e.g. ampar-endocytosis
mkdir -p gocam_models/$PROCESS/{literature,noctua,datamine,agent-output}
ls gocam_models/$PROCESS/
```

Curator (human) actions before the pipeline can run:
- Place primary research PDFs in `gocam_models/$PROCESS/literature/`, named `<PMID>.pdf`
- (Stage 2 only) drop the OWL/TTL model export into `gocam_models/$PROCESS/noctua/`
- (Optional) place a curated `expert_claims.docx` at `gocam_models/$PROCESS/`
- (Optional) place process-specific known errors / UniProt corrections in `gocam_models/$PROCESS/ANNOTATION_NOTES.md`

If `literature/` is empty, do not proceed past Phase 0 — ask the curator to add PDFs first, or use `/pubmed` to build a PMID reading list for them to download.

### 0b. Determine the stage

Check whether `noctua/` contains a model file:

```bash
ls gocam_models/<process>/noctua/*.{ttl,owl} 2>/dev/null && echo "Stage 2" || echo "Stage 1"
```

---

### Stage 1 — No Noctua model (starting from scratch)

There is no model yet. You will produce the claims document, proposed comments, and draw.io purely from the literature. The curator builds the GO-CAM in Noctua only after expert sign-off on your output.

**0a. Check if a related GO-CAM already exists in the store** (optional but worthwhile)

```bash
barista list-models --title "<pathway keyword>"
barista list-models --gp UniProtKB:<key_protein_accession>
```

If a relevant model exists, export it and switch to Stage 2.

**0b. Identify your inputs**

Check what is available in the process folder:
- `literature/*.pdf` — primary PDFs (required before annotation can begin)
- `expert_claims.docx` — curated claims from the domain expert (use as biological framework)
- Slides, presentations, tables, figures delivered by the expert — orientation only

Use only **full articles** — abstracts are insufficient for GO-CAM annotation. If PDFs are missing, use `/pubmed` to find the PMIDs, then give the curator the list:

```
mcp__claude_ai_PubMed__search_articles(query="<pathway> <species> molecular mechanism", max_results=20)
```

**PDF acquisition is a curator (human) action.** Name each file `<PMID>.pdf` and place it in `literature/`. Do not proceed with annotation until PDFs are in place.

**0c. Orient from expert material**

Read `expert_claims.docx`, slides, tables, or any provided figures to build an initial hypothesis of:
- Which gene products are involved
- What activities they perform
- What causal relationships exist

Treat all of this as a *hypothesis to be verified* against PDFs — not as evidence.

---

### Stage 2 — Noctua model exists (extending or revising)

**0a. Export the current model**

```bash
barista list-models --title "<pathway keyword>"   # find model ID
barista export-model --model <id> -f gocam-yaml > /tmp/model_export.yaml
wc -l /tmp/model_export.yaml                      # check size before reading
```

Read the export in sections — do not Read the whole file at once if it exceeds 150 lines.

**0b. Collect inputs**

- PDFs in `literature/` — verify all PMIDs cited in the model have a corresponding PDF
- `expert_claims.docx` if present — use as additional framework
- Datamine PMID list (Grep only — never Read the files):
  ```bash
  grep -oE 'PMID:[0-9]+' gocam_models/<process>/datamine/claims_nodes*.md | sort -u
  ```

---

## Phase 1: Inventory

### Stage 1 (no model):

Build the protein/activity inventory from PDFs and expert material directly.

1. **Delegate each PDF to a subagent** (see PDF Delegation Pattern above) — launch in parallel for all PDFs in `literature/`
2. Collect structured summaries from each subagent
3. Extract: gene products, molecular activities, causal relationships, evidence (PMID + figure)
4. Build your working inventory as a list of: [protein, one-sentence role from text, causal edges, evidence per edge]
5. Note any gaps — proteins mentioned without mechanistic evidence, or claimed relationships without a primary reference
6. **Save the protein inventory to `agent-output/protein_inventory.md`** — this file is updated in Phase 4 with confirmed UniProt IDs and GO terms:

```markdown
# Protein Inventory — <process name>
(Created Phase 1 — updated Phase 4)

| Gene symbol | Role from text (one sentence) | PMIDs | Phase 4 UniProt | Phase 4 MF |
|---|---|---|---|---|
| Syt1 | Calcium sensor that triggers SV fusion by binding membranes | 18504299, 12743108 | — | — |
| Rab5 | GTPase that marks early endosomes and controls SV sorting | 19965435 | — | — |
```

Do not run `gocam search` in Phase 1. UniProt IDs and MF verification happen in Phase 4.

### Stage 2 (model exists):

1. Identify the process folder (e.g., `gocam_models/ampar-endocytosis/`)
2. Export the model via barista for a clean inventory (preferred):
   ```bash
   barista export-model --model <model-id> -f gocam-yaml
   ```
3. Detect which evidence format the TTL uses (rdfs:comment vs owl:Axiom):
   ```bash
   echo "rdfs:comment count: $(grep -c 'rdfs:comment' gocam_models/<process>/noctua/*.ttl 2>/dev/null)"
   echo "owl:Axiom count:    $(grep -c 'owl:Axiom'    gocam_models/<process>/noctua/*.ttl 2>/dev/null)"
   ```
4. Extract all nodes, their enabled_by gene product IRIs, and their MF/BP/CC annotations.
5. Extract all causal edges with their RO relation types.
6. Extract all PMIDs from the evidence — via Grep, not Read:
   ```bash
   PROCESS="gocam_models/ampar-endocytosis"
   # PMIDs in rdfs:comment style
   grep -oE '"PMID: ?[0-9]+"' "$PROCESS/noctua/"*.ttl 2>/dev/null \
     | tr -d '"' | sed 's/PMID: /PMID:/' | sort -u
   # PMIDs in OWL format
   grep -oE 'PMID: ?[0-9]+' "$PROCESS/noctua/"*.owl 2>/dev/null | sort -u
   ```
7. Cross-reference PMIDs against available PDFs in `literature/`:
   ```bash
   ls "$PROCESS/literature/"*.pdf | sed 's/.*\///' | sed 's/\.pdf//'
   ```
8. Flag any PMIDs cited in the model that have no corresponding PDF.
9. If `expert_claims.docx` exists, read it and use it as the starting framework.

---

## Phase 2: PDF Verification (Batched by PDF)

Group all items (nodes, edges, claims) that cite the same PMID and send them to a single subagent (see PDF Delegation Pattern above — batch pattern). Never launch one subagent per claim. The subagent reads the PDF once and verifies all items citing it. You never Read the PDF yourself.

### 2a. Verify PMIDs
- Confirm the paper title and authors match what the comment/axiom claims
- If PMID is wrong, find the correct one

**If no PDF is available for a cited PMID:** Use the `/pubmed` skill. First try full text (PMC open-access), then fall back to metadata. **When using `get_full_text_article`, extract only the relevant sections (Results, Methods) in your subagent prompt — do not dump the entire article into the main context.**

```
mcp__claude_ai_PubMed__convert_article_ids(pmids=["12345"], target_id_type="pmcid")
mcp__claude_ai_PubMed__get_full_text_article(pmc_ids=["PMC..."])   # if PMC ID found
mcp__claude_ai_PubMed__get_article_metadata(pmids=["12345"])       # fallback: abstract only
```

Full text confirms all claims. Abstract-only confirms at minimum: title, authors, year, journal, assay type. Mark abstract-only claims as "PDF not available — abstract only" in `errors_report.md` (Stage 2) or as a note in the relevant comment block (Stage 1).

**Process-specific PMID errors:** Check `gocam_models/<process>/ANNOTATION_NOTES.md` if it exists — it contains known PMID errors, confirmed UniProt IDs, and MF corrections for that specific process. Do not use notes from another process folder.

### 2b. Verify Figure References
- For each figure cited (e.g., "Fig 4A"), confirm that figure exists in the paper
- Confirm the figure shows what the comment claims it shows
- If the comment says "Fig 4F" but the relevant data is actually in "Fig 4B", correct it

### 2c. Verify Assay Descriptions
- Confirm the assay described in the comment matches what the paper actually did
- Example: if comment says "GST pull-down" but the figure shows "co-IP", correct it

### 2d. Verify Claims/Notes
- Confirm quantitative claims (e.g., "Kd = 15.7 μM", "4-fold increase", "p < 0.001")
- Flag any claim that is not supported by the cited figure

### 2e. Verify UniProt IDs (Stage 2 only)
- Stage 1: UniProt IDs have not been assigned yet — they are confirmed in Phase 4. Skip this step for Stage 1.
- Stage 2: Verify that every UniProt ID in the existing model matches the correct species. The model organism is Mus musculus (NCBITaxon:10090) unless stated otherwise.
- **Use `gocam search` to confirm UniProt IDs** — do not guess from memory:
  ```bash
  cd gocam-curator
  .venv/bin/gocam search <GENE_SYMBOL> --species mouse
  ```
- **For MGI IDs or other MOD IDs** — use the `/amigo` skill:
  ```bash
  uv run noctua amigo search-bioentities -t <GENE_SYMBOL> --taxon NCBITaxon:10090
  ```
- Process-specific confirmed UniProt IDs: check `gocam_models/<process>/ANNOTATION_NOTES.md`

---

## Phase 2 Checkpoint — Save Verified Inventory

After completing Phase 2, **update `agent-output/protein_inventory.md`** with any corrections or additions found during PDF verification (corrected PMID attributions, newly identified proteins, removed misattributions). This keeps the inventory current before Phase 3.

The pipeline continues directly to Phase 3 in the same session. If you need to stop here and resume later, the saved `protein_inventory.md` is your re-entry point — begin the next session by reading it before proceeding to Phase 3.

