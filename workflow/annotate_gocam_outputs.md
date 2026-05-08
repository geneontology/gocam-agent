# GO-CAM Annotation — Phase 7: Outputs

Read this file before starting Phase 7. Also read `workflow/comments_template.md` and `workflow/claims_template.md` before generating any output files.

---

## Phase 7: Output Generation

All outputs go in the `agent-output/` subfolder of the process directory. Never write or modify files in `noctua/`. Never overwrite the root `expert_claims.docx`.

---

### Output 1: Comments File (`agent-output/comments.md`)

**Stage 1 (no model yet):** Produce *proposed* comment blocks for every node and edge you identified from the literature. These are what the rdfs:comments should look like once the curator creates the corresponding nodes and edges in Noctua. Mark each block with `[PROPOSED — curator creates this node/edge in Noctua]`.

**Stage 2 (model exists):** Produce verified/corrected rdfs:comment blocks, ready for the curator to copy-paste into the Noctua interface. One block per node, one block per edge.
- For nodes/edges with existing evidence: provide the corrected/verified version.
- For nodes/edges lacking evidence: provide new comment blocks noting the gap.
- For nodes/edges supported by literature but not yet in the model: include the comment block marked `[NOT YET IN MODEL — curator must create this node/edge in Noctua first]`.

---

### Output 2: Expert Validation Claims Document (`agent-output/expert_validation_claims.md`)

**This is the primary output of the pipeline.** It goes to domain experts for review before any GO-CAM editing happens.

Write this as a Markdown file (see `claims_template.md` for exact format):

```
Expert Validation Document
[Model title] — [Species]

Section [Letter]: [Pathway phase name]

Claim [N]: [Plain English biological statement]
  Evidence: [assay type], [Author et al. Year] (PMID: [PMID]), Fig [X]
  Confidence: HIGH/MEDIUM/LOW — [justification]
  Expert response: OK / WRONG / UNCERTAIN
```

Format claims by pathway phase (e.g., "Basal state", "LTD initiation", "Release from anchors", "Endocytic zone recruitment", "Cargo recognition").

Write this file directly using the Write tool. Do **not** generate a Word document — the curator will request a `.docx` export separately when the document is ready for distribution.

---

### Output 3: Errors Report (`agent-output/errors_report.md`)

**Stage 1:** Not applicable — there is no existing model to correct. Skip this output.

**Stage 2:** List every correction made:

```markdown
## PMID Corrections
| Comment | Old PMID | New PMID | Reason |
|---|---|---|---|

## Figure Corrections
| Comment | Old Fig | New Fig | What paper actually shows |
|---|---|---|---|

## UniProt Corrections
| Gene | Old UniProt | New UniProt | Reason |
|---|---|---|---|

## ECO Code Corrections
| Edge/Node | Old ECO | New ECO | Actual assay |
|---|---|---|---|

## MF Corrections
| Node | Old MF | New MF | Reason |
|---|---|---|---|

## Missing Evidence (edges/nodes with no ECO or PMID in model)
| Edge/Node | Relation | Status | Suggested PMID | Suggested ECO |
|---|---|---|---|---|

## CHEBI ID Issues
| Node | CHEBI ID | Claimed identity | Verified identity | Issue |
|---|---|---|---|---|

## Confidence Changes
| Claim | Old | New | Reason |
|---|---|---|---|

## Expert Claims Validation (if expert_claims.docx was present)
| Claim # | Status | Notes |
|---|---|---|
| 1 | CONFIRMED | All PMIDs, figures, and claims verified against PDFs |
| 2 | CORRECTED | PMID was wrong — fixed from 17346965 to 17329211 |
| 3 | ADDED | New claim not in original document — supported by PMID:XXXXX |

## Unverifiable Claims (PDF not available)
| Claim | PMID | PubMed metadata retrieved? | Status |
|---|---|---|---|
```

---

### Output 4: Network Topology Summary (`agent-output/network_topology.md`)

Text-based pathway diagram:

```
NMDAR → Ca2+ → Calcineurin → PP1 → ⊣ CACNG2 (release from PSD-95 trap)
NMDAR → Ca2+ → Calcineurin → PICK1-AP2 binding ↑
NMDAR → Ca2+ → PICK1-GluA2 binding ↑ (direct)
NMDAR → Ca2+ → ⊣ NSF (reduce PICK1 stripping)
ATAD1 → ⊣ GRIP1-GluA2 (release anchor)
IQSEC1 → ARF6 → PI(4,5)P2 → AP2 clustering
HPCA → AP2-GluA2 bridge
PICK1 delivers cargo → AP2 → AMPAR endocytosis
```

Include a node inventory table and edge summary table (with evidence status per edge).

---

### Output 5: Protein Inventory (`agent-output/protein_inventory.md`)

Already created in Phase 1 and updated in Phase 4. By Phase 7 it should contain, per gene: gene symbol, role from text, PMIDs, confirmed UniProt ID, MF term. No additional work in Phase 7 — just confirm it exists and is up to date.

---

### Output 6: Pathway Diagram (`agent-output/pathway_sketch.drawio`) — Optional, separate session

**Do not generate this output as part of the main pipeline session.** Run it in a separate session using the `/drawio` skill after the curator has reviewed and approved the claims document.

To generate: start a new session, invoke `/drawio <process>`, read `.claude/skills/drawio/SKILL.md` for the full specification, and read `workflow/network_template_draw.drawio` to copy the Shape Palette page verbatim.

**What to build (summary):**
- 3-page `.drawio` file: Shape Palette (copied verbatim from template page 1) + Canvas + empty Canvas 2
- Proteins → blue rounded rectangles; small molecules → yellow ellipses; complexes → green dashed rectangles; processes → pink clouds
- Positive regulation → green arrows; negative regulation → red arrows; upstream context → grey dashed arrows
- Each edge gets a numbered claim badge (blue = HIGH, grey = MEDIUM, light grey = LOW) matching claim numbers in `expert_validation_claims.md`
- Layout: left-to-right signal flow, grouped by pathway phase, nodes ≥ 100px apart
- Title cell: `[Pathway Name] — [Species] | GO-CAM [model ID]`

All XML style strings, badge formats, and assembly pseudocode are in `.claude/skills/drawio/SKILL.md`.

---

## Final Output Consistency Checklist

Before marking the pipeline complete, verify:

**Stage 1 (no model):**
- [ ] Every protein/activity identified from PDFs has a proposed comment block in `comments.md`, marked `[PROPOSED]`
- [ ] Every claim in `expert_validation_claims.md` is traceable to a proposed comment block in `comments.md`
- [ ] `network_topology.md` accounts for all causal edges identified from literature
- [ ] `protein_inventory.md` is complete with Phase 4 UniProt IDs and MF terms filled in
- [ ] All PMIDs in `comments.md` are in normalized format `PMID:XXXXXXX` (no spaces after colon) and are clickable hyperlinks
- [ ] All UniProt IDs were confirmed via `gocam search`, not assumed from memory

**Stage 2 (model exists — additional checks):**
- [ ] Every `enabled_by` node in the TTL has a comment block in `comments.md`
- [ ] Every causal edge in the TTL has a comment block in `comments.md`
- [ ] `errors_report.md` has an entry for every discrepancy found across phases 2–6 (no silent fixes)
- [ ] All CHEBI IDs were verified via `gocam search` or OLS lookup

---

## After the Pipeline — What the Curator Does Next

The pipeline is now complete. **Stop here.** Do not run any further skills or evaluations in this session.

Tell the curator:

> "All outputs are in `agent-output/`. Optional follow-up review skills are available:
> - `/validate-claims <process>` — forensic claim-by-claim and comment-by-comment check; OK/WRONG/UNCERTAIN with corrections; can run in the same or a fresh session
> - `/gemini-dual-review <process>` — two parallel Gemini instances per paper (peer reviewer + GO-CAM curator); raw dual output to peer_review_claims.md; no verdicts
> - `/blind-review-claude <process>` — fully independent blind re-evaluation from scratch using Claude Explore subagents; PASS/FLAG/FAIL verdicts; **must run in a completely fresh session** (not this one)
> - `/blind-review-gemini <process>` — fully independent blind re-evaluation using Gemini (PDFs read by Gemini, not Claude); PASS/FLAG/FAIL verdicts; **must run in a completely fresh session**
>
> Neither step runs automatically. Start a new session and invoke the skill you want.
>
> When `expert_validation_claims.md` is ready for distribution to expert reviewers, the curator will say **'generate the Word document'** — only then should you produce the `.docx` export using `python3` + `python-docx`."

---

## Database Lookup Tools

### Gene/protein annotation lookups — primary tool: `/gocam-curator` skill

```bash
# Confirmed UniProt ID + all GO MF/BP/CC annotations + SynGO annotations
cd gocam-curator
.venv/bin/gocam search <GENE_SYMBOL> --species mouse
```

Use for:
- UniProt ID confirmation (required before every node comment)
- MF term verification (compare model term against IDA/IMP-evidenced GO annotations)
- BP term selection for `part_of` annotations
- CC term selection for `occurs_in` annotations
- SynGO annotation check for synaptic genes

**This is your primary GO term lookup tool.** For any gene product, run `gocam search` before assigning MF, BP, or CC terms.

### CHEBI term lookup — WebFetch against OLS4 REST API

Look up CHEBI IDs to confirm small molecule identity. A common error is a PI(4,5)P₂ node annotated with the CHEBI ID for DAG or another lipid.

```
WebFetch: https://www.ebi.ac.uk/ols4/api/v2/entities?search=CHEBI:<id>&ontologyId=chebi&size=3
```

Parse the `label` field from the first result and confirm it matches the expected molecule (e.g., CHEBI:29108 → "calcium(2+)"). If the label does not match the biological context, flag in `errors_report.md`.

### Full text and metadata for missing PDFs — use the `/pubmed` skill

See the `/pubmed` skill for the full two-step workflow (PMID → PMCID → full text). Use full text when available (PMC open-access); fall back to `get_article_metadata(pmids=["XXXXXXX"])` for abstract only.

**When using `get_full_text_article`:** do not dump the entire article text. Instruct your subagent to extract only the specific sections needed (Results, Methods for the relevant figures) and discard the rest. Mark abstract-only claims as "PDF not available — abstract only" in `errors_report.md`.
