import os
import glob
import re
import json
import urllib.request
import ssl

try:
    import fitz
except ImportError:
    print("PyMuPDF not installed.")
    exit(1)

pdf_dir = "gocam_models/priming-docking-exocytosis/literature/"
pdf_files = glob.glob(os.path.join(pdf_dir, "*.pdf"))

categories = {
    'sv-tethering-docking': {
        'keywords': ['rab3', 'rab27', 'rim1', 'rim2', 'rims1', 'rim-bp', 'cacna1a', 'vgcc', 'calcium channel', 'docking', 'tethering', 'active zone cytomatrix'],
        'weight': 1.5
    },
    'sv-priming': {
        'keywords': ['munc13', 'unc13a', 'munc18', 'stxbp1', 'caps1', 'cadps', 'snare assembly', 'priming', 'trans-snare', 'syntaxin-1', 'snap-25', 'stx1a', 'snap25'],
        'weight': 1.5
    },
    'sv-fusion-clamping': {
        'keywords': ['complexin', 'cplx', 'tomosyn', 'stxbp5', 'spontaneous fusion', 'clamping', 'super-primed', 'accessory helix', 'metastable'],
        'weight': 1.5
    },
    'sv-calcium-triggered-fusion': {
        'keywords': ['synaptotagmin', 'syt1', 'calcium sensor', 'c2a', 'c2b', 'membrane fusion', 'pore expansion', 'triggered exocytosis', 'calcium-triggered', 'zippering'],
        'weight': 1.5
    },
    'sv-snare-recycling': {
        'keywords': ['nsf', 'alpha-snap', 'napa', 'cis-snare', 'disassembly', 'atpase', 'snare recycling', 'sollner'],
        'weight': 1.5
    },
    'cross-cutting-review': {
        'keywords': ['review', 'overview', 'recent advances', 'mechanism of neurotransmitter release coming into focus'],
        'weight': 1.0
    }
}

def extract_text(pdf_path):
    text = ""
    try:
        doc = fitz.open(pdf_path)
        # Read first 3 pages to get abstract, intro, and keywords
        for page in doc[:3]:
            text += page.get_text()
    except Exception:
        pass
    return text.lower()

results = {cat: [] for cat in categories}
unassigned = []

for pdf in pdf_files:
    filename = os.path.basename(pdf)
    text = extract_text(pdf)
    
    if not text:
        unassigned.append((filename, "Could not extract text"))
        continue
        
    scores = {cat: 0 for cat in categories}
    for cat, data in categories.items():
        for kw in data['keywords']:
            count = len(re.findall(r'\b' + re.escape(kw.lower()) + r'\b', text))
            scores[cat] += count * data['weight']
            
    # Assign to best category
    best_cat = max(scores, key=scores.get)
    if scores[best_cat] > 0:
        results[best_cat].append((filename, scores[best_cat]))
    else:
        unassigned.append((filename, "No strong keyword matches found"))

md_content = "# Proposed PDF Division for Priming-Docking-Exocytosis\n\n"
md_content += "This document proposes the division of all PDFs currently in the `gocam_models/priming-docking-exocytosis/literature/` folder among the 5 sub-projects defined in `ARCHITECTURE.md` (plus a cross-cutting reviews category). The division is based on a programmatic full-text analysis (reading the first 3 pages of each PDF) and scoring against the specific biological keywords defined in the architecture.\n\n"

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

def get_title(pmid):
    if not pmid.isdigit():
        return "Unknown Title"
    url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id={pmid}&retmode=json"
    try:
        req = urllib.request.urlopen(url, context=ctx, timeout=5)
        res = json.loads(req.read().decode('utf-8'))
        title = res['result'][pmid]['title']
        return title
    except:
        return "Unknown Title"

for cat in categories.keys():
    md_content += f"## {cat}\n"
    if not results[cat]:
        md_content += "*(No PDFs assigned to this category)*\n\n"
    else:
        results[cat].sort(key=lambda x: x[1], reverse=True)
        for filename, score in results[cat]:
            pmid = filename.replace('.pdf', '').strip()
            title = get_title(pmid)
            md_content += f"- **{filename}** (Score: {score})\n"
            if pmid.isdigit():
                md_content += f"  - *Title:* {title} (PMID: {pmid} (https://pubmed.ncbi.nlm.nih.gov/{pmid}/))\n"
        md_content += "\n"

md_content += "## Unassigned / Requires Manual Review\n"
if not unassigned:
    md_content += "*(None)*\n\n"
else:
    for filename, reason in unassigned:
        pmid = filename.replace('.pdf', '').strip()
        title = get_title(pmid)
        md_content += f"- **{filename}**: {reason}\n"
        if pmid.isdigit():
            md_content += f"  - *Title:* {title} (PMID: {pmid} (https://pubmed.ncbi.nlm.nih.gov/{pmid}/))\n"
            
os.makedirs('gocam_models/priming-docking-exocytosis/gemini-analysis', exist_ok=True)
with open('gocam_models/priming-docking-exocytosis/gemini-analysis/division.md', 'w') as f:
    f.write(md_content)

print("Generated division.md")
