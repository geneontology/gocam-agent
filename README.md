# gocam-agent

An AI-assisted workspace for exploring, reviewing, and editing [GO-CAM](https://geneontology.org/docs/gocam-overview/) models. Open this repo in [Claude Code](https://claude.ai/code) or locally with `claude`, and start working with GO-CAM models through natural language.

> ⚠️ **This workspace targets the development server by default.** Use `--live` only when you intend to modify production models.

## Getting started

```bash
# Clone and install
git clone https://github.com/geneontology/gocam-agent.git
cd gocam-agent
uv sync

# Set your Barista token (get one from the GO Noctua team)
export BARISTA_TOKEN=<your-token>

# Open in Claude Code
claude
```

Then just ask:

- *"Show me the 5 most recent GO-CAM models"*
- *"Export the Hedgehog signaling model and tell me if it's well-structured"*
- *"Review all models for human SMO and summarize the pathway coverage"*
- *"Create a new model for the EGFR → MAPK signaling cascade"*

The agent uses the `barista` CLI and built-in curation guidelines to work with models.

## What's inside

- **`barista` CLI** — list, export, create, and edit GO-CAM models on the Noctua/Minerva server
- **Curation skills** — annotation guidelines for transcription factors, receptors, transporters, complexes, ubiquitin ligases, and more (`.claude/skills/`)
- **OLS MCP** — ontology term lookup for GO, ChEBI, and other OBO ontologies
- **`amigo` CLI** — search GO annotations and bioentities via GOlr

## Key commands

```bash
# Browse models
barista list-models --limit 20
barista list-models --gp UniProtKB:Q14457
barista list-models --title "apoptosis"

# Export a model
barista export-model --model 680ad14200006567 -f gocam-yaml
barista export-model --model 680ad14200006567 -f markdown

# Create and edit (dev server by default)
barista create-model --title "My pathway model"
barista add-individual --model <id> --class GO:0004674 --assign kinase
barista add-fact --model <id> --subject receptor --object kinase --predicate RO:0002413

# Search annotations
amigo search-annotations --gene-product UniProtKB:P04637
amigo term-bioentities --term GO:0006915
```

All commands default to the **development server**. Add `--live` to target production.

## Reviews

Model reviews live in `docs/reviews/`. See [SMO.md](docs/reviews/SMO.md) for an example review of 17 Hedgehog/Smoothened pathway models.

## MCP servers

The project configures an [OLS](https://www.ebi.ac.uk/ols4/) MCP server for ontology term lookups (`.mcp.json`).

**Note:** If you're authenticated with Claude Max/Pro, your web session MCPs (e.g., PubMed, Notion) will also appear in Claude Code. These are inherited from your account, not this project. Use `--strict-mcp-config` to restrict to project-only MCPs. For GO-CAM operations, the `barista` CLI is the preferred interface.

## Documentation

- [Full docs](https://geneontology.github.io/gocam-agent)
- [GO-CAM overview](https://geneontology.org/docs/gocam-overview/)
- [Noctua editor](https://noctua.geneontology.org/)
