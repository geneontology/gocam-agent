import urllib.request
import json
import ssl
import time

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

queries = {
    "priming-docking-exocytosis": "presynaptic vesicle exocytosis complexin synaptotagmin docking priming review",
    "synaptic-vesicle-recycling": "presynaptic synaptic vesicle recycling ultrafast endocytosis bulk endocytosis dynamin review"
}

for name, q in queries.items():
    print(f"=== {name} ===")
    url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term={urllib.parse.quote(q)}&retmode=json&retmax=20"
    try:
        req = urllib.request.urlopen(url, context=ctx)
        res = json.loads(req.read().decode('utf-8'))
        idlist = res['esearchresult'].get('idlist', [])
        for pmid in idlist[:5]:
            sum_url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id={pmid}&retmode=json"
            s_req = urllib.request.urlopen(sum_url, context=ctx)
            s_res = json.loads(s_req.read().decode('utf-8'))
            title = s_res['result'][pmid]['title']
            print(f"{pmid} | {title}")
            time.sleep(0.5)
    except Exception as e:
        print(f"Error: {e}")
