import urllib.request
import json
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

pmids = [
    # ampar-synthesis-assembly
    "12097498", "19234475", "14622580", "12062022", "19717983", "16815334",
    # ampar-secretory-trafficking
    "40840626", "34241635", "30600260", "28875935", "23838184", "11986669", "28871032",
    # ampar-unanchoring
    "15664178", "23100425", "24418105", "19169250", "12177200", "33990590",
    # ampar-recycling
    "18984164", "31757887", "33999113", "29166605", "32329391", "18045925",
    # ampar-lysosomal-degradation
    "11086992", "21849535", "26468430", "24962637", "28626159",
    # others from previous enrichment
    "28215682", "20439000", "25753037", "12050666", "19483686", "12847086", "10481184"
]

def fetch_title(pmid):
    url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id={pmid}&retmode=json"
    try:
        req = urllib.request.urlopen(url, context=ctx)
        res = json.loads(req.read().decode('utf-8'))
        title = res['result'][pmid]['title']
        return title
    except Exception as e:
        return f"ERROR: {e}"

for pmid in pmids:
    print(f"PMID: {pmid} | {fetch_title(pmid)}")

