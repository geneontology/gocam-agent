---
name: pubmed
description: Fetch full-text articles and metadata from PubMed/PMC. Use when a PDF is missing from literature/ and you need the article text or abstract to verify a claim. Full text is only available for open-access PMC articles (~6 million).
---

# PubMed Full-Text Retrieval

Use when a PDF is not available in `literature/` and you need to verify a claim against the actual paper.

## Full-text retrieval (2-step — PMC open-access articles only)

**Step 1 — Convert PMID to PMCID:**
```
mcp__claude_ai_PubMed__convert_article_ids(pmids=["12345678"], target_id_type="pmcid")
```

**Step 2 — Fetch full text:**
```
mcp__claude_ai_PubMed__get_full_text_article(pmc_ids=["PMC1234567"])
```

Returns the full article text. ~6 million open-access articles are available. If the article is paywalled, this returns nothing — fall back to abstract.

**Context budget warning:** Full-text articles can be 20,000–50,000 words. Do not dump the entire text into your response. Extract only the sections you need (Results, Methods for the relevant figures) and discard the rest. If delegating to a subagent, instruct it to return only the specific passages that answer your verification question.

## Abstract / metadata fallback (works for all PubMed articles)

```
mcp__claude_ai_PubMed__get_article_metadata(pmids=["12345678", "87654321"])
```

Returns title, authors, journal, year, abstract. Accepts arrays — batch multiple PMIDs in one call. Use when full text is unavailable. Mark any claim verified only from abstract as "PDF not available — abstract only" in `errors_report.md`.

## Searching for papers

```
mcp__claude_ai_PubMed__search_articles(query="synaptic vesicle exocytosis Munc18 mouse", max_results=20)
```

## Limitations

- Full text only available for PMC open-access articles (~6M of ~35M total PubMed records)
- Paywalled articles return no text — curator must obtain the PDF manually
- Always cite PubMed and include DOIs when reporting results from these tools
