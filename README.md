# gocam-agent

An AI-assisted workspace for exploring, reviewing, and editing [GO-CAM](https://geneontology.org/docs/gocam-overview/) models. Open this repo in [Claude Code](https://claude.ai/code) and start working with GO-CAM models through natural language.

> ⚠️ **This workspace targets the development server by default.** Production models require the `--live` flag.

## Getting started

```bash
git clone https://github.com/geneontology/gocam-agent.git
cd gocam-agent
uv sync
export BARISTA_TOKEN=<your-token>
claude
```

Then just ask:

- *"What GO-CAM models exist for human TP53?"*
- *"Show me the most recent models and summarize them"*
- *"Review model 680ad14200006567 — is it well-structured?"*
- *"Help me add causal edges to connect the enzymatic steps in this sphingolipid model"*

The agent has access to GO-CAM annotation guidelines, ontology lookup, and tools for reading models directly.

## Running a literature-backed annotation project

To annotate a pathway from primary literature (verified claims doc, comments, pathway diagram), use the `/gocam-claims-pipeline` skill.

1. **Create a process folder** under `gocam_models/`, lowercase and hyphenated:

   ```bash
   PROCESS=ampar-endocytosis   # your pathway name
   mkdir -p gocam_models/$PROCESS/{literature,noctua,datamine,agent-output}
   ```

2. **Add PDFs** to `gocam_models/$PROCESS/literature/`, named `<PMID>.pdf` (e.g. `15664178.pdf`). For Stage 2 (extending an existing GO-CAM), also drop the OWL/TTL into `noctua/`.

3. **Run the pipeline**: ask Claude *"Run the GO-CAM claims pipeline for `ampar-endocytosis`"*. The pipeline reads instructions from `workflow/` and writes outputs to `gocam_models/$PROCESS/agent-output/`.

4. **Review outputs.** The primary deliverable is `agent-output/expert_validation_claims.md`. Optional follow-ups (separate sessions): `/validate-claims`, `/gemini-dual-review`, `/blind-review-claude`, `/blind-review-gemini`.

See `CLAUDE.md` for the full skill list and project layout. Pipeline phases live in `workflow/`.

