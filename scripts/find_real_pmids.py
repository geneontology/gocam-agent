import urllib.request
import json
import ssl
import time

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

queries = {
    # Hallucinated ones that need fixing
    "Greger 2002 AMPAR ER": "Greger AMPA receptor endoplasmic reticulum 2002",
    "Schwenk 2009 TARP cornichon": "Schwenk AMPA receptor cornichon 2009",
    "Ehlers 2000 degradation": "Ehlers Reinsertion or degradation of AMPA receptors 2000",
    "Lin 2011 Nedd4": "Lin Nedd4-mediated AMPA receptor ubiquitination 2011",
    "Loo 2015 degradation": "Loo ESCRT AMPA receptor degradation 2014",
    "Widagdo 2015 ubiquitination": "Widagdo AMPA receptor ubiquitination 2015",
    "Goo 2017 ubiquitination": "Goo AMPA receptor ubiquitination 2017",
    "Wu 2017 SYT7": "Wu Synaptotagmin-7 AMPA receptor 2017",
    "Kennedy 2010 STX4": "Kennedy Syntaxin-4 AMPA receptor 2010",
    "Bowen 2017": "Bowen Golgi-independent secretory trafficking 2017"
}

def search_pubmed(query):
    url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term={urllib.parse.quote(query)}&retmode=json&retmax=1"
    try:
        req = urllib.request.urlopen(url, context=ctx)
        res = json.loads(req.read().decode('utf-8'))
        idlist = res['esearchresult'].get('idlist', [])
        if not idlist: return "Not Found"
        pmid = idlist[0]
        
        sum_url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id={pmid}&retmode=json"
        s_req = urllib.request.urlopen(sum_url, context=ctx)
        s_res = json.loads(s_req.read().decode('utf-8'))
        title = s_res['result'][pmid]['title']
        return f"{pmid} | {title}"
    except Exception as e:
        return f"Error: {e}"

for name, q in queries.items():
    print(f"{name}: {search_pubmed(q)}")
    time.sleep(0.5)
