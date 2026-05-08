# GO-CAM Comment Template

Use this template for every rdfs:comment annotation in the GO-CAM model.
One comment block per node. One comment block per edge.

---

## Node Comment Template

```
Node: [HGNC symbol] | UniProt: [model organism UniProt ID] | PMID: [PMID] | System: [all species/preparations, comma-separated] | Perturbation: [all perturbations, comma-separated] | Assay: [all assays, comma-separated] | Fig: [all relevant figures] | Note: [consolidated findings, 2-4 sentences]
```

## Edge Comment Template

```
Edge: [Source HGNC symbol] -> [Target HGNC symbol or process] | Relation: [plain English relation] | PMID: [PMID] | System: [all species/preparations, comma-separated] | Perturbation: [all perturbations, comma-separated] | Assay: [all assays, comma-separated] | Fig: [all relevant figures] | Note: [consolidated findings, 2-4 sentences]
```

---

## Field Definitions

| Field | What to put | Example |
|---|---|---|
| HGNC symbol | Official gene symbol | PPP1CA, CACNG2, DLG4 |
| UniProt | UniProt accession for the model organism | P62137 |
| PMID | PubMed ID(s) as clickable links (see format below) | [PMID: 15664178](https://pubmed.ncbi.nlm.nih.gov/15664178/) |
| System | Experimental system(s) used | mouse hippocampal slices, rat cortical neurons, purified recombinant proteins |
| Perturbation | What was manipulated | tautomycin (100 nM), S9D phosphomutant, shRNA knockdown, PP1 KO |
| Assay | Experimental technique(s) | in vitro kinase assay, co-IP, patch-clamp electrophysiology |
| Fig | Figure reference(s) with exact panels and what they show | Tomita 2005 Fig 4B (tautomycin blocks basal dephosphorylation), Bats 2007 Fig 3A-C (QD tracking of AMPAR diffusion) |
| Relation | Plain English RO relation (edges only) | directly negatively regulates, constitutively upstream of |
| Note | 2-4 sentence summary of the key evidence | PP1 dephosphorylates stargazin C-tail serines. Tautomycin blocks both basal and NMDA-induced dephosphorylation. S9D phosphomimetic mutant occludes LTD. |

## PMID Link Format

Every PMID must be a clickable hyperlink to PubMed so readers can go straight to the paper.
- In the comments.md output: `[PMID: 15664178](https://pubmed.ncbi.nlm.nih.gov/15664178/)`
- Multiple PMIDs: `[PMID: 15664178](https://pubmed.ncbi.nlm.nih.gov/15664178/), [PMID: 7724573](https://pubmed.ncbi.nlm.nih.gov/7724573/)`

## Figure Reference Format

Every figure reference must include:
1. Author and year (for disambiguation when multiple papers are cited)
2. Exact panel letters (not just "Fig 4" — write "Fig 4B" or "Fig 4F-G")
3. A parenthetical describing what the figure shows

Example: `Tomita 2005 Fig 4B (tautomycin blocks basal dephosphorylation), Fig 4F-G (tautomycin blocks NMDA-induced dephosphorylation)`

## Rules

- Every field must be filled. If unknown, write "not specified".
- PMID must be verified against the actual paper. Do not guess.
- PMIDs must be clickable hyperlinks to PubMed.
- Fig references must cite exact panels (not just figure numbers) and describe what each shows.
- Fig references must include the author name and year for disambiguation when multiple papers are cited.
- Note should include key quantitative findings where available (Kd values, fold-changes, p-values).
- Keep each comment as a single block of text (no line breaks within the comment).
