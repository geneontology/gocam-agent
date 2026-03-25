
# gocam-agent

This is the project description.

## Documentation Website

[https://geneontology.github.io/gocam-agent](https://geneontology.github.io/gocam-agent)

## Repository Structure

* [docs/](docs/) - mkdocs-managed documentation
* [project/](project/) - project files (these files are auto-generated, do not edit)
* [src/](src/) - source files (edit these)
  * [gocam_agent](src/gocam_agent)
* [tests/](tests/) - Python tests
  * [data/](tests/data) - Example data

## Developer Tools

There are several pre-defined command-recipes available.
They are written for the command runner [just](https://github.com/casey/just/). To list all pre-defined commands, run `just` or `just --list`.

## Credits

This project uses the template [monarch-project-copier](https://github.com/monarch-initiative/monarch-project-copier)

## MCP Servers

The project `.mcp.json` configures an OLS (Ontology Lookup Service) MCP server for term lookups.

**Note:** If you are authenticated with Claude Max/Pro, your web session MCPs (e.g., Noctua, PubMed, Notion) will also appear in Claude Code sessions. These are inherited from your account, not from this project's config. To restrict to project-only MCPs, use `--strict-mcp-config`. For this project, the CLI (`barista`) is the preferred interface for GO-CAM operations, not the Noctua MCP.
