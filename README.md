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
- *"Let's build a model of the EGFR → MAPK cascade from this paper: PMID:12345678"*
- *"Review model 680ad14200006567 — is it well-structured?"*
- *"Help me add causal edges to connect the enzymatic steps in this sphingolipid model"*

The agent has access to GO-CAM annotation guidelines, ontology lookup, and tools for reading and editing models directly.

## Reviews

Model reviews live in `docs/reviews/`. See [SMO.md](docs/reviews/SMO.md) for an example.

## Documentation

- [GO-CAM overview](https://geneontology.org/docs/gocam-overview/)
- [Project docs](https://geneontology.github.io/gocam-agent)
