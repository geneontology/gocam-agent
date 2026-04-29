import fitz
import os
import glob
folders = [
    "gocam_models/AMPAR/ampar-anchoring/literature",
    "gocam_models/AMPAR/ampar-unanchoring/literature",
    "gocam_models/AMPAR/ampar-endocytic-priming/literature",
    "gocam_models/AMPAR/ampar-endocytosis/literature"
]
for folder in folders:
    proc = folder.split('/')[2]
    out_name = f"{proc}_full_text.txt"
    with open(out_name, 'w') as f:
        for pdf in glob.glob(folder + "/*.pdf"):
            try:
                doc = fitz.open(pdf)
                text = "\n".join([page.get_text() for page in doc])
                f.write(f"\n\n{'='*40}\nPMID / FILE: {os.path.basename(pdf)}\n{'='*40}\n")
                f.write(text)
            except Exception as e:
                f.write(f"Error reading {pdf}: {e}\n")
