import os
import shutil
import glob

# Move general reviews to reviews folder
general_reviews = ['30359599', '30364226', '32895399']
reviews_dir = 'gocam_models/AMPAR/reviews'
os.makedirs(reviews_dir, exist_ok=True)

for pmid in general_reviews:
    for f in glob.glob(f'gocam_models/AMPAR/ampar-*/literature/{pmid}.*'):
        shutil.move(f, os.path.join(reviews_dir, os.path.basename(f)))

# Move specific misaligned papers to their rightful folders
moves = {
    # from ampar-anchoring
    "11986669": "ampar-secretory-trafficking", # GRIP1 steers kinesin
    
    # from ampar-synaptic-insertion
    "34369573": "ampar-endocytosis", # Phosphorylation regulates clathrin internalization
    
    # from ampar-endocytosis
    "21496646": "ampar-unanchoring", # Thorase regulates synaptic plasticity (maybe keep or move)
    
    # from synaptic-vesicle-recycling to AMPAR
    "gocam_models/synaptic-vesicle-recycling/literature/18045925.pdf": "gocam_models/AMPAR/ampar-recycling/literature",
    "gocam_models/synaptic-vesicle-recycling/literature/20098723.pdf": "gocam_models/AMPAR/ampar-postendocytic-sorting/literature",
    "gocam_models/synaptic-vesicle-recycling/literature/15297461.pdf": "gocam_models/AMPAR/ampar-synaptic-insertion/literature", # Rab8
    "gocam_models/synaptic-vesicle-recycling/literature/15629704.pdf": "gocam_models/AMPAR/ampar-postendocytic-sorting/literature", # Rab5
    "gocam_models/synaptic-vesicle-recycling/literature/28384478.pdf": "gocam_models/AMPAR/ampar-recycling/literature", # Retromer
    "gocam_models/synaptic-vesicle-recycling/literature/23524343.pdf": "gocam_models/AMPAR/ampar-recycling/literature", # Nexin 27
    "gocam_models/synaptic-vesicle-recycling/literature/19955431.pdf": "gocam_models/AMPAR/ampar-secretory-trafficking/literature" # Dysbindin
}

for src_pmid, dest_folder in moves.items():
    if "/" in src_pmid: # direct path
        if os.path.exists(src_pmid):
            os.makedirs(dest_folder, exist_ok=True)
            shutil.move(src_pmid, os.path.join(dest_folder, os.path.basename(src_pmid)))
    else:
        for f in glob.glob(f'gocam_models/AMPAR/ampar-*/literature/{src_pmid}.*'):
            dest = f"gocam_models/AMPAR/{dest_folder}/literature"
            os.makedirs(dest, exist_ok=True)
            shutil.move(f, os.path.join(dest, os.path.basename(f)))

print("Moved files")
