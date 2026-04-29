import os
import json
import urllib.request
import ssl
import re

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

def fetch_title(pmid):
    url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id={pmid}&retmode=xml"
    try:
        req = urllib.request.urlopen(url, context=ctx)
        xml_data = req.read().decode('utf-8')
        title_m = re.search(r'<ArticleTitle[^>]*>(.*?)</ArticleTitle>', xml_data, re.DOTALL)
        return title_m.group(1) if title_m else "No Title"
    except:
        return "Error"

base = "gocam_models/AMPAR"
dirs = ["ampar-endocytosis/literature", "ampar-endocytic-priming/literature", "ampar-lateral-diffusion/literature", "ampar-synaptic-insertion/literature"]

for d in dirs:
    path = os.path.join(base, d)
    if os.path.exists(path):
        print(f"=== {d} ===")
        for f in os.listdir(path):
            if f.endswith('.pdf'):
                pmid = f.replace('.pdf', '')
                if pmid.isdigit():
                    title = fetch_title(pmid)
                    print(f"{pmid}: {title}")
