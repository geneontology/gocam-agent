import re
import urllib.request
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
valid_pmids = {}

def val(p):
    if p in valid_pmids: return valid_pmids[p]
    try:
        r = urllib.request.Request(f'https://pubmed.ncbi.nlm.nih.gov/{p}/', method='HEAD')
        is_val = urllib.request.urlopen(r, context=ctx).status == 200
        valid_pmids[p] = is_val
        return is_val
    except:
        valid_pmids[p] = False
        return False

def rep1(m):
    p = m.group(1)
    if val(p): return f'PMID: {p} (https://pubmed.ncbi.nlm.nih.gov/{p}/)'
    return m.group(0)

def rep2(m):
    p = m.group(1)
    if val(p): return f'- `{p}.pdf` (PMID: {p}, https://pubmed.ncbi.nlm.nih.gov/{p}/)'
    return m.group(0)

files = [
    'gocam_models/AMPAR/gemini-analysis/enrichment-gemini.md',
    'gocam_models/AMPAR/gemini-analysis/literature-overview-gemini.md',
    'gocam_models/AMPAR/gemini-analysis/project_definitions-gemini.md'
]

pat1 = re.compile(r'PMID:\s*(\d+)(?!\s*\()')
pat2 = re.compile(r'-\s+`(\d+)\.pdf`')

for f in files:
    with open(f, 'r') as fp:
        c = fp.read()
    c = pat1.sub(rep1, c)
    c = pat2.sub(rep2, c)
    with open(f, 'w') as fp:
        fp.write(c)

print("Done")