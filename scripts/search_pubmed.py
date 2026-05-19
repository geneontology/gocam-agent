import urllib.request
import urllib.parse
import json
import ssl
import sys

def search_pubmed(query, max_results=3):
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    
    url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term={urllib.parse.quote(query)}&retmode=json&retmax={max_results}"
    try:
        req = urllib.request.urlopen(url, context=ctx)
        res = json.loads(req.read().decode('utf-8'))
        idlist = res['esearchresult']['idlist']
        if not idlist:
            return "No results"
        
        pmids = ",".join(idlist)
        summary_url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id={pmids}&retmode=json"
        s_req = urllib.request.urlopen(summary_url, context=ctx)
        s_res = json.loads(s_req.read().decode('utf-8'))
        
        abstract_url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id={pmids}&retmode=text&rettype=abstract"
        a_req = urllib.request.urlopen(abstract_url, context=ctx)
        abstracts = a_req.read().decode('utf-8')
        
        return abstracts
    except Exception as e:
        return str(e)

if __name__ == "__main__":
    query = sys.argv[1]
    print(f"--- Results for: {query} ---")
    print(search_pubmed(query))
