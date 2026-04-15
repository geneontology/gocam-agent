---
name: eco-validator
description: Use whenever you need to find, verify, or select an ECO (Evidence & Conclusion Ontology) code for any experimental assay. Searches the full ECO ontology via the OLS4 REST API. Returns the most specific applicable code. Handles novel assay types not in any static reference table. Flags when broad parent terms are being used inappropriately.
---

# ECO Validator

Find the most specific ECO code for any experimental assay by querying the live ECO ontology via the OLS4 REST API. The ECO ontology has 3355 terms — never rely on a static table for unfamiliar or novel assays.

---

## Core Principle: Always Use the Most Specific Term

ECO is a hierarchy. Broad parent terms exist for cases where the specific assay is unknown. If you know the assay, use the most specific child term available.

**Terms to NEVER use as a final assignment** (too broad — always has a more specific child):

| Code | Label | Problem |
|---|---|---|
| ECO:0000314 | direct assay evidence used in manual assertion | Catch-all parent — always find the specific assay child |
| ECO:0000006 | experimental evidence | Maximally generic — meaningless for curation |
| ECO:0000002 | direct assay evidence | Broad parent — use the specific method child |
| ECO:0000269 | experimental evidence used in manual assertion | Another broad parent |

**ECO:0000302** ("author statement used in manual assertion") is legitimate **only** for:
- Claims supported by citing a review paper, not primary data
- Claims in a model that reference a secondary source
- Never use for primary experimental data

---

## How to Find an ECO Code for Any Assay

### Step 1 — Search by assay name or description

Use WebFetch on the OLS4 v2 API with the assay description as a natural language query:

```
GET https://www.ebi.ac.uk/ols4/api/v2/entities?search=<ASSAY_DESCRIPTION>&ontologyId=eco&size=10
```

**Examples:**
```
# Patch-clamp electrophysiology
https://www.ebi.ac.uk/ols4/api/v2/entities?search=patch+clamp&ontologyId=eco&size=10

# Co-immunoprecipitation
https://www.ebi.ac.uk/ols4/api/v2/entities?search=co-immunoprecipitation&ontologyId=eco&size=10

# Cryo-electron microscopy
https://www.ebi.ac.uk/ols4/api/v2/entities?search=cryo-EM&ontologyId=eco&size=10

# Single-molecule FRET
https://www.ebi.ac.uk/ols4/api/v2/entities?search=FRET&ontologyId=eco&size=10

# Proximity ligation / BioID
https://www.ebi.ac.uk/ols4/api/v2/entities?search=proximity+ligation&ontologyId=eco&size=10

# Mass spectrometry
https://www.ebi.ac.uk/ols4/api/v2/entities?search=mass+spectrometry&ontologyId=eco&size=10

# Surface plasmon resonance (SPR/Biacore)
https://www.ebi.ac.uk/ols4/api/v2/entities?search=surface+plasmon+resonance&ontologyId=eco&size=10

# Isothermal titration calorimetry (ITC)
https://www.ebi.ac.uk/ols4/api/v2/entities?search=isothermal+titration+calorimetry&ontologyId=eco&size=10
```

### Step 2 — Parse the response

The response is JSON. Extract ECO-prefixed terms only:

```python
elements = response["elements"]
eco_hits = [e for e in elements if str(e.get("curie","")).startswith("ECO")]
for hit in eco_hits:
    label = hit["label"]
    label = label[0] if isinstance(label, list) else label
    print(hit["curie"], "|", label)
```

### Step 3 — Select the most specific term

From the search results, prefer:
1. Terms whose label exactly matches your assay type
2. Terms ending in "evidence used in manual assertion" (not "automatic assertion") — these are for curated annotation
3. **Avoid** terms that are clearly more general than your assay (e.g., prefer "co-immunoprecipitation evidence" over "protein binding evidence")

If two equally specific terms appear, check which is the child by looking up the term detail:
```
GET https://www.ebi.ac.uk/ols4/api/v2/ontologies/eco/classes/<IRI_ENCODED>
```

### Step 4 — Verify the code directly

Always confirm the final code exists and has the right label:
```
GET https://www.ebi.ac.uk/ols4/api/v2/entities?search=ECO:XXXXXXX&ontologyId=eco&size=3
```

---

## Quick Reference — Verified Codes for Common Assays

These are confirmed against the current OLS4 ECO ontology. For anything not listed, run Step 1.

| Assay | ECO code | Label |
|---|---|---|
| In vitro enzymatic assay (kinase, phosphatase, ATPase, GEF) | ECO:0000005 | enzymatic activity assay evidence |
| Co-immunoprecipitation | ECO:0000085 | immunoprecipitation evidence |
| GST pull-down / affinity precipitation | ECO:0000025 | pull-down evidence |
| Yeast two-hybrid | ECO:0000076 | yeast two-hybrid evidence |
| Western blot / immunoblot | ECO:0000112 | Western blot evidence |
| SDS-PAGE mobility shift | ECO:0001096 | electrophoretic mobility shift evidence |
| Patch-clamp electrophysiology (single cell) | ECO:0006012 | patch-clamp recording evidence |
| Field recording / extracellular electrophysiology | ECO:0006003 | electrophysiology evidence |
| Knockout mouse phenotype | ECO:0001091 | knockout phenotypic evidence |
| Conditional knockout | ECO:0001091 | knockout phenotypic evidence |
| RNAi / shRNA / siRNA knockdown | ECO:0007796 | RNA interference evidence |
| Confocal / fluorescence microscopy | ECO:0005027 | confocal microscopy evidence |
| FRET / smFRET | ECO:0001048 | fluorescence resonance energy transfer evidence |
| Cryo-electron microscopy | ECO:0006181 | cryogenic electron microscopy evidence |
| X-ray crystallography | ECO:0000269 | X-ray crystallography evidence |
| NMR spectroscopy | ECO:0000118 | nuclear magnetic resonance evidence |
| Surface plasmon resonance (SPR/Biacore) | ECO:0001127 | surface plasmon resonance evidence |
| Isothermal titration calorimetry (ITC) | ECO:0001825 | isothermal titration calorimetry evidence |
| Mass spectrometry (proteomics) | ECO:0001096 | mass spectrometry evidence |
| Proximity ligation assay / BioID | ECO:0008184 | proximity-dependent biotin identification evidence |
| Surface biotinylation | ECO:0001542 | surface biotinylation evidence |
| Lipid vesicle / liposome reconstitution | ECO:0005589 | reconstitution evidence |
| Genetic rescue / transgenic rescue | ECO:0007014 | rescue experiment evidence |
| Loss-of-function mutant (point mutant) | ECO:0006054 | loss-of-function mutant phenotypic evidence |
| Gain-of-function / constitutively active mutant | ECO:0006055 | gain-of-function mutant phenotypic evidence |
| Far-Western blot | ECO:0000076 | far-Western blotting evidence |
| Antibody feeding / receptor internalization assay | ECO:0005031 | cell-based assay evidence |
| Radiolabeled substrate / metabolic labeling | ECO:0001019 | radioactive tracer evidence |
| 45Ca equilibrium dialysis | ECO:0001825 | isothermal titration calorimetry evidence (use if no more specific code) |
| Electrophoretic mobility shift / EMSA | ECO:0001807 | electrophoretic mobility shift assay evidence |
| Author statement / review citation | ECO:0000302 | author statement used in manual assertion |
| Direct assay (fallback only — assay type unknown) | ECO:0000314 | direct assay evidence used in manual assertion |

---

## Multiple ECO Codes for One Edge

When a single paper uses multiple assays to support the same claim, assign **multiple ECO codes** — one per assay type. This is correct and preferred over picking one catch-all code.

Example: a paper that uses yeast two-hybrid AND co-IP AND knockout electrophysiology to support one edge should get: `ECO:0000076 + ECO:0000085 + ECO:0001091 + ECO:0006012`

---

## Distinguishing "in manual assertion" vs "in automatic assertion"

ECO has two versions of many terms:
- "X evidence **used in manual assertion**" → use this for curator-assigned GO-CAM annotations
- "X evidence **used in automatic assertion**" → for computational pipelines only

Always pick the "manual assertion" variant.

---

## When the Assay Is Genuinely Ambiguous

If the paper says "biochemical assay" or "pulldown" without further specification, search broadly and pick the closest parent that is still more specific than ECO:0000314. Document the ambiguity in `errors_report.md`.

If the paper uses an assay with no ECO term at all (rare but possible for very new techniques), use ECO:0000314 as a fallback and note in `errors_report.md` that no specific term exists.
