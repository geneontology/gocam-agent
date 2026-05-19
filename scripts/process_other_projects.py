import os
import json
import urllib.request
import ssl
import time
import re

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

def fetch_title_abstract(pmid):
    url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id={pmid}&retmode=xml"
    try:
        req = urllib.request.urlopen(url, context=ctx)
        xml_data = req.read().decode('utf-8')
        title_m = re.search(r'<ArticleTitle[^>]*>(.*?)</ArticleTitle>', xml_data, re.DOTALL)
        title = title_m.group(1) if title_m else "No Title"
        abstract_m = re.search(r'<Abstract>(.*?)</Abstract>', xml_data, re.DOTALL)
        abstract = " ".join(re.findall(r'<AbstractText[^>]*>(.*?)</AbstractText>', abstract_m.group(1), re.DOTALL)) if abstract_m else "No Abstract"
        return title, abstract
    except:
        return "Error", "Error"

projects = {
    "priming-docking-exocytosis": "gocam_models/priming-docking-exocytosis/literature",
    "synaptic-vesicle-recycling": "gocam_models/synaptic-vesicle-recycling/literature"
}

results = {}
for proj, path in projects.items():
    results[proj] = {}
    if os.path.exists(path):
        for f in os.listdir(path):
            if f.endswith('.pdf'):
                pmid = f.replace('.pdf', '').strip()
                # only fetch if it's a number
                if pmid.isdigit():
                    title, _ = fetch_title_abstract(pmid)
                    results[proj][pmid] = title
                    time.sleep(0.5)

with open('other_projects_pmids.json', 'w') as out:
    json.dump(results, out, indent=2)
print("Done")
