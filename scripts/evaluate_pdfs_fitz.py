import os
import glob
import re
import json

try:
    import fitz
except ImportError:
    print("PyMuPDF not installed.")
    exit(1)

processes = {
    'ampar-synthesis-assembly': ['adar2', 'q/r', 'editing', 'endoplasmic reticulum', 'tarp', 'stargazin', 'cornichon', 'cnih', 'tetramerization', 'assembly'],
    'ampar-secretory-trafficking': ['golgi', 'eres', 'kif5', 'kinesin', 'grip1', 'sap97', 'dendritic shaft', 'rab8', 'secretory', 'forward transport'],
    'ampar-synaptic-insertion': ['snare', 'exocytosis', 'syt7', 'synaptotagmin', 'stx4', 'syntaxin-4', 'snap23', 'vamp2', 'insertion', 'rab8', 'rab11'],
    'ampar-lateral-diffusion': ['diffusion', 'brownian', 'mobility', 'lateral', 'tracking', 'spt', 'extracellular matrix'],
    'ampar-anchoring': ['psd-95', 'camkii', 'phosphorylation', 'stargazin', 'pdz', 'lrrtm2', 'n-cadherin', 'akap5', 'anchoring', 'immobilization', 'slot'],
    'ampar-unanchoring': ['calcineurin', 'pp1', 'dephosphorylation', 'gsk3', 'thr19', 'destabilization', 'unanchoring'],
    'ampar-endocytic-priming': ['ap2', 'pick1', 'brag2', 'pi(4,5)p2', 'pip2', 'hippocalcin', 'nsf', 'priming'],
    'ampar-endocytosis': ['clathrin', 'endophilin', 'amphiphysin', 'dynamin', 'ccv', 'scission', 'internalization'],
    'ampar-postendocytic-sorting': ['rab5', 'rab4', 'rab11', 'rab7', 'grasp-1', 'neep21', 'sorting', 'early endosome'],
    'ampar-recycling': ['rab11', 'rab8', 'myovb', 'myosin vb', 'fip2', 'recycling endosome'],
    'ampar-lysosomal-degradation': ['rab7', 'late endosome', 'lysosome', 'degradation', 'escrt', 'ubiquitin', 'nedd4', 'cathepsin']
}

def extract_text(pdf_path):
    text = ""
    try:
        doc = fitz.open(pdf_path)
        for page in doc:
            text += page.get_text()
    except Exception:
        pass
    return text.lower()

best_grounding = {}

for proc, kws in processes.items():
    print(f"Evaluating {proc}...")
    pdf_files = glob.glob(f'gocam_models/AMPAR/{proc}/literature/*.pdf')
    
    scores = {}
    for pdf in pdf_files:
        pmid = os.path.basename(pdf).replace('.pdf', '')
        text = extract_text(pdf)
        if not text:
            scores[pmid] = -1
            continue
            
        score = 0
        for kw in kws:
            count = len(re.findall(r'\b' + re.escape(kw) + r'\b', text))
            score += count * 2 # weight keywords more
            
        if 'ampa' in text or 'glur' in text or 'gria' in text:
            score += 10
            
        scores[pmid] = score
    
    sorted_pmids = sorted([p for p in scores.keys() if scores[p] >= 0], key=lambda x: scores[x], reverse=True)
    best_grounding[proc] = sorted_pmids[:3]
    
    print(f"Top PMIDs for {proc}: {[(p, scores[p]) for p in sorted_pmids[:3]]}")

with open('best_grounding_fitz.json', 'w') as f:
    json.dump(best_grounding, f, indent=2)

print("Done")
