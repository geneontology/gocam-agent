# GO-CAM Annotation Rules

Read this file at session start. These rules apply to every phase of the pipeline.

---

## Critical Rules

1. **Never write to Noctua** — no barista write commands (`add-individual`, `add-fact`, `add-fact-evidence`). The curator builds the GO-CAM after expert sign-off. Your outputs are `expert_validation_claims.md` (primary) and `comments.md` (curator resource).
2. **Every PMID must be verified against the actual PDF** — no trusting the existing comments. If PDF missing, use PubMed MCP and flag accordingly.
3. **Every figure reference must exist in the cited paper** — open the PDF and check.
4. **Every ECO code must match the actual assay** — re-derive from the paper, never trust input.
5. **UniProt IDs must match the correct species** — use `gocam search` to confirm; do not guess.
6. **MF must never contain "binding"** — binding is has_input, not MF.
7. **MF must never contain a substrate name** — use generic mechanism terms.
8. **CHEBI IDs must be verified against OLS** — the biological context does not guarantee the ID is correct.
9. **Do not invent biology** — if evidence is absent, flag it, don't fabricate.
10. **Distinguish direct from indirect** — pharmacological inhibitor blocking an effect ≠ direct enzymatic evidence.
11. **Show your work** — for every correction, state what was wrong and why the correction is right.
12. **When in doubt, mark as MEDIUM confidence** and flag for expert review.

---

## MF Assignment Rules (Strict — apply when assigning Molecular Functions)

1. **THE ABSOLUTE "NO BINDING" RULE FOR MF**: You are STRICTLY FORBIDDEN from using ANY GO term for a Molecular Function that contains the word "binding" (e.g., NO protein binding, NO syntaxin binding, NO ATP binding, NO lipid binding) or generic terms like "regulator", "activator", or "inhibitor".

2. **THE "SUBSTRATE INDEPENDENCE" CARDINAL RULE**: A Molecular Function term MUST NEVER be named after its specific substrate or target protein. DO NOT use or invent terms like "syntaxin chaperone activity" or "AMPA receptor phosphorylator". The GO term must describe the generalized biochemical mechanism. Capture the target via has_input edges.

3. **If the text ONLY says "Protein A binds Protein B"**: Do not invent a binding term. Extract the inherent activity of Protein A from the wider context, or state "Activity unknown — text only describes interaction". Model the binding purely as the relation (Edge) to the target.

---

## Datamine Rules

- **Never `Read` datamine files directly.** `validated_claims.json` is 1–3 MB; `claims_nodes.md` is 200–450 KB. Reading them floods the context window.
- Extract PMIDs only via `Grep`:
  ```bash
  grep -oE 'PMID:[0-9]+' gocam_models/<process>/datamine/claims_nodes*.md | sort -u
  ```
- Extract verbatim quotes for a specific gene via `Grep`:
  ```bash
  grep -A2 -B2 "RAB5" gocam_models/<process>/datamine/claims_nodes*.md | head -50
  ```
- Discard everything else from the datamine. ECO codes, MF terms, figure refs, and RO relations from datamine are systematically unreliable.

---

## Noctua File Rules (Stage 2 only — skip entirely for Stage 1)

- **Never `Read` noctua OWL/TTL files whole.** The model files can be 200–300 KB / 3000+ lines.
- Use `barista export-model -f gocam-yaml` for the node/edge inventory.
- Use `Grep` for targeted extraction from TTL:
  ```bash
  grep -oE '"PMID: ?[0-9]+"' noctua/*.ttl | sort -u          # PMIDs
  grep -c 'rdfs:comment' noctua/*.ttl                          # evidence format
  grep -c 'owl:Axiom' noctua/*.ttl                             # evidence format
  grep -A5 'rdfs:comment' noctua/*.ttl | head -100             # first comments
  ```
- If you must read specific sections of the TTL, use `Read` with `offset` and `limit` (100–150 lines at a time), not the whole file.
