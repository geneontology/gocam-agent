# GO-CAM Annotation — Phases 3, 4, 4b, 5, and 6

Read this file before starting Phase 3. Assumes Phases 0–2 are complete.

---

## Phase 3: ECO Code Verification

The datamine assigns ECO codes that are valid ontology terms but systematically mismatched to actual assays. Every ECO code must be re-derived from the paper.

**For any assay not in the table below, or to find a more specific term:** use the `/eco-validator` skill, which queries the full ECO ontology (3355 terms) live via the OLS4 REST API. Never use a broad parent code when a more specific child exists.

**Codes that are too broad and must NOT be used as a final assignment:**
- `ECO:0000314` (direct assay evidence used in manual assertion) — always has a more specific child
- `ECO:0000006` (experimental evidence) — maximally generic, meaningless
- `ECO:0000302` (author statement used in manual assertion) — only for review citations, never primary data

**Reference table — common assays:**

| Assay type | ECO code | ECO label |
|---|---|---|
| In vitro enzymatic assay (kinase, phosphatase, GEF, ATPase) | ECO:0000005 | enzymatic activity assay evidence |
| GST pull-down / affinity precipitation | ECO:0000025 | pull-down evidence |
| Co-immunoprecipitation | ECO:0000085 | immunoprecipitation evidence |
| Yeast two-hybrid | ECO:0000076 | yeast two-hybrid evidence |
| Western blot / immunoblot | ECO:0000112 | Western blot evidence |
| SDS-PAGE mobility shift / EMSA | ECO:0001807 | electrophoretic mobility shift assay evidence |
| Loss-of-function point mutant | ECO:0006054 | loss-of-function mutant phenotypic evidence |
| Gain-of-function / constitutively active mutant | ECO:0006055 | gain-of-function mutant phenotypic evidence |
| Genetic rescue / transgenic rescue | ECO:0007014 | rescue experiment evidence |
| Knockout mouse (germline or conditional) | ECO:0001091 | knockout phenotypic evidence |
| RNAi / shRNA / siRNA knockdown | ECO:0007796 | RNA interference evidence |
| Confocal / fluorescence microscopy | ECO:0005027 | confocal microscopy evidence |
| FRET / smFRET | ECO:0001048 | fluorescence resonance energy transfer evidence |
| Cryo-electron microscopy | ECO:0006181 | cryogenic electron microscopy evidence |
| X-ray crystallography | ECO:0000269 | X-ray crystallography evidence |
| NMR spectroscopy | ECO:0000118 | nuclear magnetic resonance evidence |
| Patch-clamp electrophysiology (single cell) | ECO:0006012 | patch-clamp recording evidence |
| Field recording / extracellular electrophysiology | ECO:0006003 | electrophysiology evidence |
| Surface plasmon resonance (SPR / Biacore) | ECO:0001127 | surface plasmon resonance evidence |
| Isothermal titration calorimetry (ITC) | ECO:0001825 | isothermal titration calorimetry evidence |
| Mass spectrometry (proteomics) | ECO:0001096 | mass spectrometry evidence |
| Proximity ligation assay / BioID | ECO:0008184 | proximity-dependent biotin identification evidence |
| Surface biotinylation | ECO:0001542 | surface biotinylation evidence |
| Lipid vesicle / liposome reconstitution assay | ECO:0005589 | reconstitution evidence |
| Antibody feeding / receptor internalization assay | ECO:0005031 | cell-based assay evidence |
| Metabolic labeling (³²P, ³H, ¹⁴C) | ECO:0001019 | radioactive tracer evidence |
| Review / secondary literature citation | ECO:0000302 | author statement used in manual assertion |
| Assay type unknown (fallback only) | ECO:0000314 | direct assay evidence used in manual assertion |

**Multiple ECO codes per edge:** If one paper uses multiple assay types to support a single claim, assign one ECO code per assay. This is correct and preferred over a single broad code.

**Handling edges with no evidence at all:** Some models (especially SynGO-derived) have causal edges where the owl:Axiom block exists but contains no ECO code and no PMID. For these:
1. Flag prominently in `errors_report.md` under "Missing Evidence"
2. Search the literature for the canonical paper supporting this edge and suggest the PMID + ECO code
3. In `comments.md`, write the comment block with `PMID: NONE (missing — suggested: PMID:XXXXX)` and `ECO: NONE (missing — suggested: ECO:XXXXXXX)`
4. Mark the claim as MEDIUM or LOW confidence (no verified evidence in model)

---

## Phase 4: Molecular Function Verification

**Start by reading `agent-output/protein_inventory.md`** (created in Phase 1). This is your working protein list with roles from text. You will update it here with confirmed UniProt IDs and MF terms as you work through each gene.

For each node, **run `gocam search`** — do not rely on domain knowledge alone. See the `/gocam-curator` skill for full usage instructions.

```bash
# From repo root, then cd gocam-curator/
.venv/bin/gocam search <GENE_SYMBOL> --species mouse
```

This returns the confirmed UniProt ID and all curated GO MF annotations with evidence codes. After each search:
1. Use the UniProt ID in node comments
2. **Update the Phase 4 columns in `protein_inventory.md`** with the confirmed UniProt ID and best MF term (IDA/IMP evidence preferred)
3. If the proposed MF from Phase 1 is absent from search results with IDA/IMP evidence, flag it in `errors_report.md` (Stage 2) or note it in the comment block (Stage 1)

For an independent cross-check, or when `gocam search` returns no results, use the `/amigo` skill:
```bash
uv run noctua amigo bioentity-annotations UniProtKB:<ID> -a F -e IDA -e IMP -l 100
```

Then apply these strict rules (also in `annotate_gocam_rules.md`):

1. **NEVER use "binding" as an MF**. Binding is an interaction (has_input edge), not a function.
2. **MF must be substrate-independent**. No "stargazin phosphatase activity" — use "protein serine/threonine phosphatase activity" with has_input: CACNG2.
3. **Check that the MF matches the protein's actual biochemical activity**, not its partners' activities.

**Process-specific MF corrections:** Check `gocam_models/<process>/ANNOTATION_NOTES.md` if it exists — it lists known MF errors and corrections for that process. For any gene not covered, derive the MF from `gocam search` results using IDA/IMP-evidenced terms only.

**CHEBI ID verification for small molecules:** When a model node uses a CHEBI ID, verify it via WebFetch against the OLS4 REST API:
```
WebFetch: https://www.ebi.ac.uk/ols4/api/v2/entities?search=CHEBI:<id>&ontologyId=chebi&size=3
```
Check that the returned `label` matches the expected molecule. A common error is a PI(4,5)P₂ node annotated with the CHEBI ID for DAG. Flag mismatches in `errors_report.md`.

**Annotation guidelines for special protein types:** If the gene product is a **complex, molecular adaptor, sequestering protein, or transcription factor**, invoke the `/gocam-best-practice` skill before assigning its MF. It contains specific annotation guidelines for these types that differ from generic enzyme annotations.

---

## Phase 4b: BP and CC Annotation Using gocam search

Every activity node in a valid GO-CAM must have:
- `part_of` → a Biological Process term (BFO:0000050)
- `occurs_in` → a Cellular Component term (BFO:0000066)

**Use `gocam search` to find the appropriate BP and CC terms for each gene product:**

```bash
.venv/bin/gocam search <GENE_SYMBOL> --species mouse
```

The output includes all curated GO BP and CC annotations with evidence codes. Use these to select the most specific terms:
- For `part_of`: prefer BP terms with IDA/IMP evidence, e.g., "synaptic vesicle exocytosis" (GO:0016079) rather than "vesicle-mediated transport" (GO:0016192)
- For `occurs_in`: prefer CC terms with IDA/IEP evidence, e.g., "active zone" (GO:0048786) rather than "synapse" (GO:0045202)

Record any BP/CC assignments that could not be confirmed by `gocam search` results in `errors_report.md` (Stage 2) or as a note in the relevant comment block (Stage 1 — no errors_report exists yet).

---

## Phase 5: Relation Ontology Verification

For each edge, verify the RO relation type is appropriate:

| Biological situation | Correct RO relation |
|---|---|
| Enzyme directly phosphorylates/dephosphorylates target | directly positively/negatively regulates |
| ATPase disassembles a protein complex | directly negatively regulates |
| Scaffold protein enables interaction (no catalysis) | constitutively upstream of |
| Endocytic adaptor recruits cargo to clathrin pits | constitutively upstream of |
| Cargo adaptor delivers substrate to machinery | provides input for |
| Ca2+ activates a protein | is small molecule activator of |
| Ca2+ inhibits a protein | is small molecule inhibitor of |
| Upstream signaling through intermediate steps | causally upstream of, positive/negative effect |
| GEF activates a GTPase | directly positively regulates |

**Common errors to watch for:**
- "directly positively regulates" used for constitutive machinery (AP2 on AMPAR) → should be "constitutively upstream of"
- has_input modeled as a causal edge → should be node metadata
- Reversed edge direction (substrate → enzyme instead of enzyme → substrate)

---

## Phase 6: Confidence Assessment

For each edge, assign confidence:
- **HIGH**: Direct biochemical/enzymatic evidence with purified proteins, OR genetic evidence (KO/KI) with clear phenotype, OR multiple independent assay types confirming
- **MEDIUM**: Cellular evidence (co-IP, imaging, pharmacology) without in vitro confirmation; OR pharmacological evidence without direct enzymatic assay; OR evidence from different species/cell type than model
- **LOW**: Inferred from reviews only, indirect evidence, or single-assay support
