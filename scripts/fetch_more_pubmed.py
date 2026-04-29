import urllib.request
import json
import ssl
import time

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

def search_pubmed(query, max_results=20):
    url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term={urllib.parse.quote(query)}&retmode=json&retmax={max_results}"
    try:
        req = urllib.request.urlopen(url, context=ctx)
        res = json.loads(req.read().decode('utf-8'))
        return res['esearchresult'].get('idlist', [])
    except Exception as e:
        print(f"Search failed for {query}: {e}")
        return []

def fetch_titles(idlist):
    if not idlist: return {}
    ids = ",".join(idlist)
    url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id={ids}&retmode=xml"
    req = urllib.request.urlopen(url, context=ctx)
    xml_data = req.read().decode('utf-8')
    import re
    results = {}
    articles = xml_data.split('<PubmedArticle>')
    for art in articles[1:]:
        pmid_m = re.search(r'<PMID[^>]*>(\d+)</PMID>', art)
        if not pmid_m: continue
        pmid = pmid_m.group(1)
        title_m = re.search(r'<ArticleTitle[^>]*>(.*?)</ArticleTitle>', art, re.DOTALL)
        title = title_m.group(1) if title_m else "No Title"
        results[pmid] = title
    return results

queries = {
    "ampar-unanchoring": '("AMPA receptor" OR AMPAR) AND (calcineurin OR "PP1" OR "GSK3") AND (PSD-95 OR Stargazin)',
    "ampar-recycling": '("AMPA receptor" OR AMPAR) AND (Rab11 OR "recycling endosome" OR "GRASP-1" OR "Rab8")',
    "ampar-lysosomal-degradation": '("AMPA receptor" OR AMPAR) AND (lysosome OR degradation OR Rab7 OR ESCRT)'
}

for cat, q in queries.items():
    print(f"=== {cat} ===")
    pmids = search_pubmed(q, 20)
    titles = fetch_titles(pmids)
    for pmid, t in titles.items():
        print(f"PMID: {pmid} | {t}")
    time.sleep(1)

