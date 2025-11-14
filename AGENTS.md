# Agent instructions for gocam-agent

All commands support `--help`

## Read Access

To dump a model in minerva JSON:


```
barista export-model --model 646ff70100002557
```

In gocam-yaml:

```
barista export-model --model 646ff70100002557 -f gocam-yaml
```

## Search and Browsing models

Most recent 50:

```
barista list-models --limit 50
```

All that reference a gene product

```
barista list-models --gp UniProtKB:Q14457
```

Search by title

```
barista list-models --title "immune"
```

## Editing

Please use the skill provided
