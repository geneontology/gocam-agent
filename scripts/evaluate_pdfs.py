import os
import glob
import subprocess
import re
import json

processes = {
    'ampar-synthesis-assembly': {
        'keywords': ['adar2', 'q/r', 'editing', 'endoplasmic reticulum', 'tarp', 'stargazin', 'cornichon', 'cnih', 'tetramerization', 'assembly'],
        'grounding': ['12062022', '19265014']
    },
    'ampar-secretory-trafficking': {
        'keywords': ['golgi', 'eres', 'kif5', 'kinesin', 'grip1', 'sap97', 'dendritic shaft', 'rab8', 'secretory', 'forward transport'],
        'grounding': ['11986669', '28875935']
    },
    'ampar-synaptic-insertion': {
        'keywords': ['snare', 'exocytosis', 'syt7', 'synaptotagmin', 'stx4', 'syntaxin-4', 'snap23', 'vamp2', 'insertion'],
        'grounding': ['28355182', '20434989', '17928453']
    },
    'ampar-lateral-diffusion': {
        'keywords': ['diffusion', 'brownian', 'mobility', 'lateral', 'tracking', 'spt', 'extracellular matrix'],
        'grounding': ['12050666', '17329211']
    },
    'ampar-anchoring': {
        'keywords': ['psd-95', 'camkii', 'phosphorylation', 'stargazin', 'pdz', 'lrrtm2', 'n-cadherin', 'akap5', 'anchoring', 'immobilization'],
        'grounding': ['15664178', '30359599']
    },
    'ampar-unanchoring': {
        'keywords': ['calcineurin', 'pp1', 'dephosphorylation', 'gsk3', 'thr19', 'destabilization', 'unanchoring'],
        'grounding': ['15664178', '33990590']
    },
    'ampar-endocytic-priming': {
        'keywords': ['ap2', 'pick1', 'brag2', 'pi(4,5)p2', 'pip2', 'hippocalcin', 'nsf', 'priming'],
        'grounding': ['17302911', '28855251', '20547133']
    },
    'ampar-endocytosis': {
        'keywords': ['clathrin', 'endophilin', 'amphiphysin', 'dynamin', 'ccv', 'scission', 'internalization'],
        'grounding': ['12441055', '24217640']
    },
    'ampar-postendocytic-sorting': {
        'keywords': ['rab5', 'rab4', 'rab11', 'rab7', 'grasp-1', 'neep21', 'sorting', 'early endosome'],
        'grounding': ['20098723', '18984164']
    },
    'ampar-recycling': {
        'keywords': ['rab11', 'rab8', 'myovb', 'myosin vb', 'fip2', 'recycling endosome'],
        'grounding': ['18984164', '18045925']
    },
    'ampar-lysosomal-degradation': {
        'keywords': ['rab7', 'late endosome', 'lysosome', 'degradation', 'escrt', 'ubiquitin', 'nedd4', 'cathepsin'],
        'grounding': ['11144346', '21338354']
    }
}

def extract_text(pdf_path):
    try:
        result = subprocess.run(['pdftotext', pdf_path, '-'], capture_output=True, text=True, timeout=10)
        return result.stdout.lower()
    except:
        return ""

best_grounding = {}

for proc, data in processes.items():
    print(f"Evaluating {proc}...")
    kws = data['keywords']
    pdf_files = glob.glob(f'gocam_models/AMPAR/{proc}/literature/*.pdf')
    
    scores = {}
    for pdf in pdf_files:
        pmid = os.path.basename(pdf).replace('.pdf', '')
        text = extract_text(pdf)
        if not text:
            scores[pmid] = 0
            continue
            
        score = 0
        for kw in kws:
            score += len(re.findall(r'\b' + re.escape(kw) + r'\b', text))
        
        # also give a slight bonus if they mention AMPA or GluR
        if 'ampa' in text or 'glur' in text or 'gria' in text:
            score += 10
            
        scores[pmid] = score
    
    # Sort PMIDs by score
    sorted_pmids = sorted(scores.keys(), key=lambda x: scores[x], reverse=True)
    best_grounding[proc] = sorted_pmids[:3] # take top 3
    print(f"Top PMIDs for {proc}: {[(p, scores[p]) for p in sorted_pmids[:3]]}")

with open('best_grounding.json', 'w') as f:
    json.dump(best_grounding, f, indent=2)

