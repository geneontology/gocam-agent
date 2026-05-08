import re
import json
import urllib.request
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

top_pmids = {
    'ampar-synthesis-assembly': ['16815334', '19265014'],
    'ampar-secretory-trafficking': ['23838184', '11986669', '28875935'],
    'ampar-synaptic-insertion': ['20434989', '28355182', '15297461'],
    'ampar-lateral-diffusion': ['19483686', '17329211'],
    'ampar-anchoring': ['25843401', '19968761', '17329211'],
    'ampar-unanchoring': ['24418105', '23100425'],
    'ampar-endocytic-priming': ['28855251', '20547133', '16138078'],
    'ampar-endocytosis': ['28855251', '12441055', '34369573'],
    'ampar-postendocytic-sorting': ['20098723', '15629704'],
    'ampar-recycling': ['18984164', '32329391'],
    'ampar-lysosomal-degradation': ['21338354', '36051867']
}

titles_cache = {}

def get_title(pmid):
    if pmid in titles_cache:
        return titles_cache[pmid]
    url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id={pmid}&retmode=json"
    try:
        req = urllib.request.urlopen(url, context=ctx)
        res = json.loads(req.read().decode('utf-8'))
        title = res['result'][pmid]['title']
        
        # Get first author year
        first_author = ""
        authors = res['result'][pmid].get('authors', [])
        if authors:
            first_author = authors[0]['name'].split(' ')[0]
            if len(authors) > 2:
                first_author += " et al."
            elif len(authors) == 2:
                first_author += " & " + authors[1]['name'].split(' ')[0]
        
        year = res['result'][pmid].get('pubdate', '')[:4]
        
        citation = f"{first_author} {year}" if first_author else "Citation"
        titles_cache[pmid] = (citation, title)
        return titles_cache[pmid]
    except Exception:
        return ("Citation", "Unknown Title")

with open('gocam_models/AMPAR/gemini-analysis/project_definitions-gemini.md', 'r') as f:
    content = f.read()

for process, pmids in top_pmids.items():
    # Find the grounding line for this process
    # Search from the process header to the next double hash
    start_idx = content.find("## ")
    proc_idx = content.find(process, start_idx)
    if proc_idx == -1:
        continue
        
    next_idx = content.find("## ", proc_idx + 10)
    if next_idx == -1:
        next_idx = len(content)
        
    block = content[proc_idx:next_idx]
    
    # generate new grounding text
    grounding_parts = []
    for p in pmids:
        citation, title = get_title(p)
        grounding_parts.append(f"{citation} (PMID: {p} (https://pubmed.ncbi.nlm.nih.gov/{p}/))")
        
    new_grounding = "**Grounding:** " + "; ".join(grounding_parts) + "."
    
    # replace grounding line
    new_block = re.sub(r'\*\*Grounding:\*\*.*?(?=\n\n|\n$|$)', new_grounding, block, flags=re.DOTALL)
    
    content = content[:proc_idx] + new_block + content[next_idx:]

with open('gocam_models/AMPAR/gemini-analysis/project_definitions-gemini.md', 'w') as f:
    f.write(content)

print("Updated project_definitions-gemini.md successfully.")
