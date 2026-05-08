import os
import json
import urllib.request
import ssl
import re
import shutil

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
results = {}

for root, dirs, files in os.walk(base):
    if "literature" in root.split(os.sep):
        sub_proc = root.split(os.sep)[-2]
        if sub_proc not in results:
            results[sub_proc] = {}
        for f in files:
            if f.endswith('.pdf') or f.endswith('.txt') or f.endswith('.xml'):
                pmid = f.split('.')[0]
                if pmid.isdigit():
                    title = fetch_title(pmid)
                    results[sub_proc][pmid] = title

with open('ampar_audit.json', 'w') as out:
    json.dump(results, out, indent=2)

print("Done")
