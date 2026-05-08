import urllib.request
import json
import ssl

def fetch_pubmed(query):
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    
    url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term={urllib.parse.quote(query)}&retmode=json&retmax=1"
    try:
        req = urllib.request.urlopen(url, context=ctx)
        res = json.loads(req.read().decode('utf-8'))
        idlist = res['esearchresult']['idlist']
        if not idlist:
            return "No results"
        pmid = idlist[0]
        
        summary_url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id={pmid}&retmode=json"
        s_req = urllib.request.urlopen(summary_url, context=ctx)
        s_res = json.loads(s_req.read().decode('utf-8'))
        title = s_res['result'][pmid]['title']
        return f"PMID: {pmid} - {title}"
    except Exception as e:
        return str(e)

queries = {
    "ampar-synthesis-assembly": "AMPA receptor synthesis assembly ER ADAR2",
    "ampar-secretory-trafficking": "AMPA receptor secretory trafficking Golgi dendrite",
    "ampar-unanchoring": "AMPA receptor unanchoring calcineurin PP1 Stargazin LTD",
    "ampar-recycling": "AMPA receptor recycling Rab11 exocytosis LTP",
    "ampar-lysosomal-degradation": "AMPA receptor lysosomal degradation Rab7 late endosome"
}

for proc, q in queries.items():
    print(f"{proc}: {fetch_pubmed(q)}")
