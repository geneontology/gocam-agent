import urllib.request
import json
import ssl
import time

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

queries = {
    "priming-docking-exocytosis": "presynaptic vesicle priming docking exocytosis Munc13 RIM SNARE",
    "synaptic-vesicle-recycling": "presynaptic synaptic vesicle endocytosis clathrin dynamin kiss-and-run"
}

def search_and_fetch(query):
    url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term={urllib.parse.quote(query)}&retmode=json&retmax=15"
    try:
        req = urllib.request.urlopen(url, context=ctx)
        res = json.loads(req.read().decode('utf-8'))
        idlist = res['esearchresult'].get('idlist', [])
        
        results = []
        for pmid in idlist[:10]:
            sum_url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id={pmid}&retmode=json"
            s_req = urllib.request.urlopen(sum_url, context=ctx)
            s_res = json.loads(s_req.read().decode('utf-8'))
            title = s_res['result'][pmid]['title']
            results.append(f"{pmid} | {title}")
            time.sleep(0.5)
        return results
    except Exception as e:
        return [f"Error: {e}"]

for name, q in queries.items():
    print(f"=== {name} ===")
    res = search_and_fetch(q)
    for r in res:
        print(r)
