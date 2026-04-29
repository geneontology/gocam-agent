import urllib.request
import json
import ssl
import time

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

def search_pubmed(query, max_results=20):
    url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term={urllib.parse.quote(query)}&retmode=json&retmax={max_results}"
    req = urllib.request.urlopen(url, context=ctx)
    res = json.loads(req.read().decode('utf-8'))
    return res['esearchresult'].get('idlist', [])

def fetch_abstracts(idlist):
    if not idlist: return {}
    ids = ",".join(idlist)
    url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id={ids}&retmode=xml"
    req = urllib.request.urlopen(url, context=ctx)
    xml_data = req.read().decode('utf-8')
    
    # Simple XML parsing for title and abstract (regex for simplicity)
    import re
    results = {}
    articles = xml_data.split('<PubmedArticle>')
    for art in articles[1:]:
        pmid_m = re.search(r'<PMID[^>]*>(\d+)</PMID>', art)
        if not pmid_m: continue
        pmid = pmid_m.group(1)
        
        title_m = re.search(r'<ArticleTitle[^>]*>(.*?)</ArticleTitle>', art, re.DOTALL)
        title = title_m.group(1) if title_m else "No Title"
        
        abstract_m = re.search(r'<Abstract>(.*?)</Abstract>', art, re.DOTALL)
        if abstract_m:
            # combine abstract texts
            ab_texts = re.findall(r'<AbstractText[^>]*>(.*?)</AbstractText>', abstract_m.group(1), re.DOTALL)
            abstract = " ".join(ab_texts)
        else:
            abstract = "No Abstract"
            
        results[pmid] = {"title": title, "abstract": abstract}
    return results

queries = {
    "ampar-synthesis-assembly": "AMPA receptor synthesis assembly ER editing",
    "ampar-secretory-trafficking": "AMPA receptor secretory trafficking Golgi",
    "ampar-unanchoring": "AMPA receptor unanchoring calcineurin PP1 LTD",
    "ampar-recycling": "AMPA receptor recycling Rab11 exocytosis LTP",
    "ampar-lysosomal-degradation": "AMPA receptor lysosomal degradation late endosome Rab7"
}

output = {}
for category, q in queries.items():
    print(f"Searching {category}...")
    pmids = search_pubmed(q, 20)
    time.sleep(1) # rate limit
    abstracts = fetch_abstracts(pmids)
    output[category] = abstracts
    time.sleep(1)

with open("pubmed_abstracts.json", "w") as f:
    json.dump(output, f, indent=2)

print("Saved to pubmed_abstracts.json")
