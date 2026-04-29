---
name: blind-review-gemini
description: Independent blind evaluation of GO-CAM claims documents using Gemini. One Gemini instance per primary PDF reads the paper directly and returns PASS/FLAG/FAIL verdicts on every claim citing it. Use after gocam-claims-pipeline has generated its output. Always run in a fresh session — never in the same session as the pipeline. For a Claude-engine alternative, see /blind-review-claude.
argument-hint: "[PROCESS_FOLDER_NAME e.g. ampar-endocytosis]"
---

# GO-CAM Claims — Independent Blind Review (Gemini engine)

## Purpose

You are an **independent reviewer** running blind evaluation of GO-CAM annotation claims **through Gemini**. You yourself do not read the PDFs — Gemini does. Your job is to: parse the claims doc, dispatch Gemini calls, collect their answers, and assemble the evaluation report.

You have NOT seen the annotation agent's reasoning, intermediate notes, or drafts. You receive ONLY:

1. The claims document (`agent-output/expert_validation_claims.md` — canonical pipeline output; fall back to a `.docx` export if that's all that exists)
2. The primary literature PDFs in `literature/`

Each claim is evaluated **from scratch** by Gemini against the cited PDF. Neither you nor Gemini reads `comments.md`, `errors_report.md`, or `network_topology.md` — ever.

**You are a skeptic, not an advocate.** The goal is to find errors, not confirm the annotator's work.

## How this differs from the other review skills

| | `/blind-review-gemini` | `/blind-review-claude` | `/gemini-dual-review` | `/validate-claims` |
|---|---|---|---|---|
| Engine | Gemini (one per PMID) | Claude Explore subagents | Two Gemini per PMID | Claude Explore subagents |
| Perspectives | One (single blind reviewer) | One (single blind reviewer) | Two (peer reviewer + curator) | One (forensic verifier) |
| Approach | Blind, single-perspective | Blind, single-perspective | Dual perspective, raw output | Verify exactly what was written |
| Reads comments.md? | NO | NO | NO | YES |
| Verdict scale | PASS / FLAG / FAIL | PASS / FLAG / FAIL | OK / WRONG / UNCERTAIN (per perspective) | OK / WRONG / UNCERTAIN |
| Skill synthesizes? | Yes — assigns final verdict from Gemini's per-question answers | Yes — assigns final verdict from subagent's quotes | No — preserves Gemini text verbatim | Yes |
| Output | `blind-review-gemini/` (3 files) | `blind-review-claude/` (3 files) | `peer_review_claims.md` (single file) | `validation/` (2 files) |
| Session | MUST be fresh | MUST be fresh | Same or fresh | Same or fresh |

Run `/blind-review-gemini` when you want a fast independent second opinion that does **not** consume Claude's context window on PDFs. Run `/blind-review-claude` when you want Claude itself to redo the analysis. Run both for higher confidence.

## Session Isolation — MANDATORY

This skill must run in a fresh session, separate from the `gocam-claims-pipeline` session. Starting fresh guarantees:
- No shared context with the annotation agent's reasoning
- No inherited assumptions about which claims are correct

If you find yourself in the same session that ran the pipeline, stop and ask the user to start a new session.

## Folder Structure

```
gocam_models/
└── <process-name>/
    ├── literature/              # Gemini reads these directly
    ├── agent-output/
    │   ├── expert_validation_claims.md     ← READ THIS (canonical; .docx fallback)
    │   ├── comments.md                     ← DO NOT READ
    │   ├── errors_report.md                ← DO NOT READ
    │   └── network_topology.md             ← DO NOT READ
    └── blind-review-gemini/     # YOUR OUTPUT GOES HERE (create if missing)
        ├── blind-review-gemini_report.md
        ├── blind-review-gemini_summary.md
        └── discrepancies.md
```

## Dependencies

| Tool | Purpose |
|---|---|
| `gemini` CLI (`gemini --yolo -p ...`) | Reads PDFs and evaluates claims |
| `/gocam-curator` skill | UniProt ID + GO MF/BP/CC cross-check (Phase 5, selective) |
| `/amigo` skill | Independent GO annotation cross-check |
| `/pubmed` skill | Article metadata when a PDF is missing |
| `python-docx` | Reading `.docx` claims-doc fallback (`pip3 install python-docx --break-system-packages` if missing) |

---

## Protocol

### Phase 1 — Intake

1. Read `agent-output/expert_validation_claims.md` (or `.docx` fallback via `python-docx`).
2. Parse claims into structured records: claim number, biological statement, PMID(s), figure(s), ECO code(s), GO term(s), UniProt ID(s), confidence level, RO relation, section heading.
3. Inventory PDFs in `literature/`. For any cited PMID with no PDF, do not call Gemini — those claims will be marked **UNVERIFIABLE** (see Phase 3).

### Phase 2 — Group by PMID

Build `{ PMID → [list of full claim blocks citing it] }`. **One Gemini call per unique PMID**, regardless of how many claims cite that paper.

### Phase 3 — Launch Gemini Evaluators in Parallel

For each unique PMID, send one `gemini --yolo -p ...` Bash call. When multiple PMIDs are independent, launch **multiple Bash calls in the same message** so they run concurrently.

Substitute `<PROCESS>` and `<PMID>`, and paste the full claim blocks (verbatim from the claims doc) into `<CLAIMS>` before sending.

```bash
gemini --yolo -p "$(cat <<'EVAL_EOF'
You are an independent expert reviewer performing a blind evaluation of GO-CAM annotation claims. You have NOT seen the annotator's reasoning, intermediate notes, or comment files. You see only the claims below and the primary paper.

Read this paper: gocam_models/<PROCESS>/literature/<PMID>.pdf

You are a skeptic, not an advocate. Your job is to find errors, not confirm the annotator's work. Training knowledge does not count as evidence — only what the paper actually states.

Each claim has this structure:
- Claim text: a plain-English biological statement naming the proteins (HGNC symbols in parentheses) and the mechanism. It must state HOW a protein acts (e.g. "phosphorylates", "disrupts the X-Y complex") and include the functional consequence. Vague language like "regulates" is insufficient.
- Evidence line: assay type(s) | Author et al. Year | PMID | exact figure panel(s), each with a parenthetical describing what that panel shows
- Confidence line: HIGH / MEDIUM / LOW rating, followed by a written justification that cites specific figure panels and quantitative findings, ending with ECO code(s)
  - HIGH = direct biochemical/enzymatic evidence with purified proteins, OR genetic KO/KI with clear phenotype, OR multiple independent assay types
  - MEDIUM = cellular evidence (co-IP, imaging, pharmacology) without in vitro confirmation; OR evidence from a different species or cell type
  - LOW = inferred, indirect, or single-assay only

GO-CAM annotation rules to enforce:
- GO MF terms must NEVER contain "binding" — binding is modelled as has_input, not as MF
- GO MF terms must describe a generalised biochemical activity, never a substrate-specific name (not "syntaxin phosphorylase activity" — use "protein serine/threonine kinase activity")
- ECO codes must match the actual assay performed in this paper
- "directly positively/negatively regulates" requires direct mechanistic evidence (enzyme activity, direct binding causing conformational change); "causally upstream of" is for indirect or phenotypic evidence (KO phenotype, pharmacology, overexpression)
- UniProt IDs must match the species studied in this paper

For EACH claim below, evaluate independently against the paper:

1. Paper identity — is this the right paper for the claim?
2. Figure existence — does the cited figure panel exist?
3. Figure content — describe what the panel actually shows in your own words; does it match the parenthetical?
4. Assay type — is the named assay what the paper performed?
5. Biological statement — score: CONFIRMED / PARTIALLY SUPPORTED / OVERSTATED / CONTRADICTED / UNVERIFIABLE / WRONG REFERENCE. Quote the exact passage that supports or refutes the statement.
6. ECO code — is it appropriate for the assay actually performed?
7. GO term(s) — does the paper demonstrate this MF/BP/CC? Any "binding" MF? Any substrate-specific MF?
8. UniProt ID — consistent with the species in the paper?
9. RO relation — is "directly regulates" justified, or should it be "causally upstream of"?
10. Confidence — assign your own (HIGH / MEDIUM / LOW / UNSUPPORTED). Agree or disagree with the annotator's level?
11. Caveats — any limitations the paper raises that the claim fails to acknowledge?

Then assign a single overall verdict per claim:
- PASS — statement confirmed; evidence codes appropriate; GO terms correct
- FLAG — minor issue (wrong ECO, confidence disagreement, more specific GO term available, missing caveat)
- FAIL — statement wrong, evidence does not support it, or cited paper is irrelevant

Format your reply as one block per claim, exactly:

==== CLAIM [N] ====
Paper identity: [yes/no + 1 sentence]
Figure [X][panel]: EXISTS / MISSING — [what it shows in your own words, with exact quote]
Assay: CORRECT / WRONG → actual assay is [type]
Biological statement: CONFIRMED / PARTIALLY SUPPORTED / OVERSTATED / CONTRADICTED / UNVERIFIABLE / WRONG REFERENCE — [exact quote]
ECO: CORRECT / WRONG → should be [code] — [reason]
GO term(s): CORRECT / WRONG → should be [term] — [reason]
UniProt ID: CORRECT / WRONG → should be [ID] — [reason]
RO relation: CORRECT / WRONG → should be [relation] — [reason]
Confidence: AGREE / DISAGREE → my assessment: [level] — [reason]
Caveats: [any limitations the claim should acknowledge, or NONE]
VERDICT: PASS / FLAG / FAIL
Notes: [1–3 sentences of specific issues; if PASS, why the evidence is solid]

<CLAIMS>
[paste full claim blocks here]
</CLAIMS>
EVAL_EOF
)"
```

If a PDF is missing for a cited PMID, do **not** call Gemini for it. Use `/pubmed` to fetch metadata for paper identity, and mark every claim citing that PMID as **UNVERIFIABLE — abstract only** (or **UNVERIFIABLE — no metadata** if PubMed has nothing).

### Phase 4 — Cross-Claim Consistency (you, not Gemini)

After Gemini calls return, perform consistency checks across the full claim set:

1. Contradictions — does claim N contradict claim M?
2. Causal gaps — missing links in the pathway?
3. Species mixing — all gene products from the same organism?
4. Orphan gene products — mentioned in one claim but never connected?

These observations go into `discrepancies.md`.

### Phase 5 — Independent GO Annotation Cross-Check (you, selective)

For any gene product where Gemini flagged the GO term, run an independent lookup via `/gocam-curator`:

```bash
cd gocam-curator
.venv/bin/gocam search <GENE_SYMBOL> --species mouse
```

Or `/amigo` for an MGI/MOD ID. Only do this for FAILed/FLAGged claims — do not run for every gene.

### Phase 6 — Output Generation

All outputs to `blind-review-gemini/` (create the folder if missing).

#### `blind-review-gemini/blind-review-gemini_report.md` (Primary Output)

One block per claim, in claim-number order. Quote Gemini's per-question lines verbatim.

```markdown
# Blind Review Report (Gemini) — <Process Name>
**Date:** <date> | **Reviewer:** Gemini (blind-review-gemini skill)
**Claims evaluated:** N | **PMIDs covered:** K | **PDFs available:** P/N

---

## Section [Letter]: [Phase name]

---

### Claim [N]: [original biological statement]

**Cited:** [Author Year], PMID:[PMID], Fig [X][panel] | ECO: [code] | Confidence: [level]

**Gemini findings:**
[paste the verbatim ==== CLAIM ==== block returned by Gemini]

**VERDICT: PASS / FLAG / FAIL**

---

### Claim [N+1]: ...
```

#### `blind-review-gemini/blind-review-gemini_summary.md`

```markdown
# Blind Review Summary (Gemini)
**Process:** [name] | **Date:** [date] | **Claims evaluated:** N | **PDFs available:** P/N

## Scorecard
| Verdict | Count | % |
|---|---|---|
| PASS | | |
| FLAG | | |
| FAIL | | |
| UNVERIFIABLE | | |

## Top issues
1. [Most critical FAIL]
2. ...

## Recommendation
[APPROVE / REVISE / REJECT] — [one sentence]
```

#### `blind-review-gemini/discrepancies.md`

Tables grouping every disagreement: biological-statement errors, ECO errors, GO-term errors, RO-relation errors, confidence disagreements, missing caveats. Plus the cross-claim findings from Phase 4.

---

## Critical Rules

1. **FRESH SESSION** — never run in the same session as `gocam-claims-pipeline`.
2. **BLIND** — never read `comments.md`, `errors_report.md`, or `network_topology.md`. Do not pass them to Gemini.
3. **GEMINI READS THE PDFs, NOT YOU** — never use the `Read` tool on PDFs in this skill. The point of using Gemini is to keep PDF binary content out of Claude's context.
4. **ONE GEMINI CALL PER PMID** — batch all claims citing a paper into one prompt; do not launch one call per claim.
5. **PARALLEL DISPATCH** — when launching multiple PMIDs, put the Bash calls in a single message so they run concurrently.
6. **PASS THE FULL CLAIM BLOCK** — Gemini must see every line of the claim verbatim, including evidence and confidence lines.
7. **PRESERVE GEMINI'S TEXT** — quote per-question answers verbatim into the report; do not paraphrase.
8. **NO SILENT PASSES** — every claim ends with an explicit PASS / FLAG / FAIL / UNVERIFIABLE.
9. **TRAINING KNOWLEDGE IS NOT EVIDENCE** — verdict must come from the PDF, not plausibility.

## Verdicts

| Verdict | When |
|---|---|
| **PASS** | Statement confirmed; evidence codes appropriate; GO terms correct |
| **FLAG** | Minor issue (wrong ECO, confidence disagreement, more specific GO term available, missing caveat) |
| **FAIL** | Statement wrong, evidence does not support claim, or cited paper is irrelevant |
| **UNVERIFIABLE** | PDF not available for the cited PMID |
