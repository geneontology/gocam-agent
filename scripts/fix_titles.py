import re
import urllib.request
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

with open('gocam_models/AMPAR/gemini-analysis/literature-overview-gemini.md', 'r') as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    if "Unknown Title" in line:
        m = re.search(r'PMID:\s*(\d+)', line)
        if m:
            pmid = m.group(1)
            try:
                url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id={pmid}&retmode=json"
                req = urllib.request.urlopen(url, context=ctx)
                import json
                res = json.loads(req.read().decode('utf-8'))
                title = res['result'][pmid]['title']
                line = line.replace("Unknown Title", title)
            except:
                pass
    new_lines.append(line)

with open('gocam_models/AMPAR/gemini-analysis/literature-overview-gemini.md', 'w') as f:
    f.writelines(new_lines)
