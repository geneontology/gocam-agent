# Claims Document Template

Use this template when generating `expert_validation_claims.docx` in the `agent-output/` folder.
The document structure, formatting, and field order must match exactly.

---

## Document Structure

```
[Title block]
[Reviewer instructions]
[Pathway overview image — if available, reference it; do not generate one]
[Sections A through N — one per pathway phase]
[Model topology summary]
[Totals line]
```

---

## Title Block

```
Expert Validation Document

[Full model title — plain English description of the pathway]

GO-CAM Model — [Species]

Date: [YYYY-MM-DD] | Curator: [Lab / Institution]
```

---

## Reviewer Instructions

```
Instructions for the expert reviewer

For each numbered claim, please respond with one of:

  OK — The biology is correct as stated
  WRONG — with your correction (e.g. "this is indirect" or "Fig 3C not 3B")
  UNCERTAIN — Evidence is ambiguous or debated
```

---

## Section Format

Sections group claims by pathway phase. Name sections by biological stage, not by protein.

```
## Section [Letter]: [Phase name] — [Brief description]
```

Examples:
- Section A: Basal state — Synaptic stabilization of AMPARs
- Section B: LTD initiation — NMDAR activation and Ca²⁺ signaling
- Section C: Release of AMPARs from synaptic anchors
- Section D: AMPAR recruitment to endocytic zone
- Section E: PI(4,5)P₂ signaling and AP2 clustering
- Section F: Cargo recognition at clathrin-coated pits
- Section G: Verified literature annotations

---

## Claim Format

Each claim follows this exact structure:

```
Claim [N]: [Plain English biological statement naming the proteins and what happens.
Include HGNC symbols in parentheses on first mention. State the mechanism, not just the interaction.]

  Evidence: [assay type(s)], [Author et al. Year] (PMID: [PMID](https://pubmed.ncbi.nlm.nih.gov/[PMID]/)),
  Fig [X][panel(s)] ([what the figure shows])
  [For multiple papers, list each on its own line with full citation and figures]

  Confidence: [HIGH/MEDIUM/LOW] — [1-2 sentences justifying the rating.
  Include key quantitative findings. Cite specific figure panels.
  If ECO codes are relevant, list them at the end.]

  Expert response: OK / WRONG / UNCERTAIN
```

### PMID Links (mandatory)

Every PMID must be a clickable hyperlink to PubMed. Format:
- In the .docx output: `PMID: 15664178` where "15664178" is a hyperlink to `https://pubmed.ncbi.nlm.nih.gov/15664178/`
- In markdown: `[PMID: 15664178](https://pubmed.ncbi.nlm.nih.gov/15664178/)`

### Figure References (mandatory)

Every claim must cite the exact figure panels that support it. Do not just write "Fig 4" — write "Fig 4B" or "Fig 4F-G". After each figure reference, add a parenthetical stating what the figure shows:
- `Fig 4B (tautomycin blocks basal dephosphorylation)`
- `Fig 6E (effect requires PICK1-binding GluR2, not -SVKE mutant)`

If a claim cites multiple figures from the same paper, list each with its parenthetical.
If a claim cites figures from multiple papers, attribute each: `Tomita 2005 Fig 4B, Ouimet 1995 Fig 3A-B`.

### Confidence Criteria

- **HIGH** — Direct biochemical/enzymatic evidence with purified proteins, OR genetic evidence (KO/KI) with clear phenotype, OR multiple independent assay types confirming the same claim
- **MEDIUM** — Cellular evidence (co-IP, imaging, pharmacology) without in vitro confirmation; OR pharmacological evidence only (no direct enzymatic assay); OR evidence from a different species/cell type than the model
- **LOW** — Inferred from reviews only, indirect evidence, or single-assay support

### Claim Writing Rules

- Name proteins with HGNC symbol in parentheses on first mention: "Calcineurin (PPP3CA)"
- State the mechanism: "phosphorylates", "dephosphorylates", "disrupts the X-Y complex", "enhances binding"
- Do not just say "regulates" — say HOW
- Include the functional consequence: "...releasing AMPARs from the synaptic trap"
- If the claim spans multiple papers, list all with their specific figure contributions
- If a claim has a known limitation, state it explicitly (e.g., "no direct in vitro phosphatase assay reported")

---

## Model Topology Summary

At the end of the document, include a text-based pathway diagram showing all paths:

```
## Model topology summary

All paths converge on [endpoint]:

[Upstream signal] → [intermediate] → [intermediate] → [effector] → [output]
[Upstream signal] → [intermediate] → ⊣ [target] ([explanation])

Use → for activation/positive regulation
Use ⊣ for inhibition/negative regulation
Use parenthetical notes for mechanism clarity

Total: [N] protein nodes + [N] small molecules + [N] complexes | [N] biological claims
```

---

## Example Claim (for reference)

```
Claim 11: PP1 (PPP1CA) directly dephosphorylates Stargazin (CACNG2),
disrupting its interaction with PSD-95 and releasing AMPARs from the
synaptic trap.

  Evidence: SDS-PAGE mobility shift + tautomycin (PP1 inhibitor, 10 µM),
  Tomita et al. 2005 (PMID: 15664178)(https://pubmed.ncbi.nlm.nih.gov/15664178/),
  Fig 4B (tautomycin blocks basal dephosphorylation),
  Fig 4E (NMDA strips ³²P from STG),
  Fig 4F-G (tautomycin blocks NMDA-induced dephosphorylation; FK506 partly blocks),
  Fig 4H (S9D phosphomimic blocks LTD);
  PP1α/γ1 concentrated in dendritic spines, Ouimet et al. 1995
  (PMID: 7724573)(https://pubmed.ncbi.nlm.nih.gov/7724573/), Fig 3A-B
  (PP1α/γ1 immunolabel in spine heads and PSDs by immunoEM)

  Confidence: MEDIUM — tautomycin completely blocks both basal and
  NMDA-induced Stargazin dephosphorylation (Fig 4B, 4F-G). S9D
  phosphomimic blocks LTD (Fig 4H). However, evidence is pharmacological
  only — no direct in vitro phosphatase assay with purified PP1 +
  purified Stargazin substrate has been reported. PP1α/γ1 are correctly
  localized to dendritic spines (Ouimet 1995, Fig 3A-B). ECO:0006054 +
  ECO:0001096

  Expert response: OK / WRONG / UNCERTAIN
```
