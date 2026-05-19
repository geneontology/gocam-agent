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
    "Wu 2017": "Wu synaptotagmin-7 AMPA receptor 2017",
    "Kennedy 2010": "Kennedy syntaxin-4 AMPA receptor 2010",
    "Frischknecht 2009": "Frischknecht extracellular matrix lateral diffusion",
    "Borgdorff 2002": "Borgdorff Choquet lateral diffusion AMPA",
    "Brachet 2015": "Brachet Cdc42 cholesterol AMPA receptor",
    "Wang 2008": "Wang Myosin Vb Rab11 AMPA receptor 2008"
}

for proc, q in queries.items():
    print(f"{proc}: {fetch_pubmed(q)}")
