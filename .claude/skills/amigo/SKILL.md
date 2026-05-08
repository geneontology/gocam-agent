---
name: amigo
description: Search GO bioentities (genes, gene products, complexes) and their GO annotations directly from the GO database. Use to resolve MGI/MOD/ComplexPortal IDs, cross-check GO annotations independently of gocam search, or find MOD-specific gene product IDs needed in Noctua models.
---

# AmiGO — GO Bioentity and Annotation Search

Use as a complement to `gocam search` when you need to:
- Resolve an MGI ID or other MOD ID to a gene symbol
- Find the canonical bioentity ID used in Noctua (MOD IDs for MODs, UniProtKB for human/other species)
- Cross-check GO annotations directly from the GO database
- Look up ComplexPortal entries for protein complexes

## Invocation

```bash
# Same pattern as barista — requires uv in PATH
uv run noctua amigo <subcommand> [options]
```

Or if the `amigo` alias is set:
```bash
alias amigo='uv run noctua amigo'
amigo <subcommand> [options]
```

---

## Resolve a gene product (find its bioentity ID and species)

```bash
# Search by gene symbol + taxon
uv run noctua amigo search-bioentities -t Syt1 --taxon NCBITaxon:10090

# Returns: bioentity ID, label, name, taxon, type, source
# e.g. MGI:MGI:98777  Syt1  synaptotagmin I  Mus musculus  protein  MGI
```

This is the authoritative source for which IDs Noctua actually uses. For mouse, expect MGI IDs. For human, expect UniProtKB IDs.

```bash
# Confirm a specific accession exists
uv run noctua amigo get-bioentity UniProtKB:P04637
uv run noctua amigo get-bioentity MGI:MGI:98777
```

---

## Get all GO annotations for a gene product

```bash
uv run noctua amigo bioentity-annotations UniProtKB:P46096 -l 100
# Returns: GO_TERM, GO_NAME, ASPECT (F/P/C), EVIDENCE, REFERENCE, QUALIFIER, ASSIGNED_BY, DATE
```

Use this to:
- Cross-check MF assignments (ASPECT=F) independently of `gocam search`
- Verify BP (ASPECT=P) and CC (ASPECT=C) annotations for `part_of` and `occurs_in`
- Check for NOT annotations that conflict with model claims

Filter by aspect:
```bash
# MF only
uv run noctua amigo search-annotations -b UniProtKB:P46096 -a F -l 100

# With evidence filter (experimental codes only)
uv run noctua amigo search-annotations -b UniProtKB:P46096 -a F -e IDA -e IMP -e IPI -l 100
```

---

## When to use AmiGO vs gocam search

| Situation | Use |
|---|---|
| Need UniProt ID for a mouse gene | `gocam search` (faster, CLI output) |
| Encountered an MGI ID, need the gene symbol | `/amigo` `search-bioentities --taxon NCBITaxon:10090` |
| Need canonical Noctua bioentity ID | `/amigo` `search-bioentities` |
| Verify MF annotations, get SynGO | `gocam search` |
| Independent cross-check of GO annotations | `/amigo` `bioentity-annotations` |
| Look up ComplexPortal entry | `/amigo` `search-bioentities -t <complex name>` |
