import os
import glob
import json
import subprocess

pdf_files = glob.glob('gocam_models/AMPAR/ampar-*/literature/*.pdf')
summaries = {}

for pdf in pdf_files:
    # Try to find corresponding .txt file
    txt_file = pdf + ".txt"
    txt_file2 = pdf.replace('.pdf', '.txt')
    content = ""
    
    if os.path.exists(txt_file):
        with open(txt_file, 'r', errors='ignore') as f:
            content = f.read(4000)
    elif os.path.exists(txt_file2):
        with open(txt_file2, 'r', errors='ignore') as f:
            content = f.read(4000)
    else:
        # Try pdftotext
        try:
            result = subprocess.run(['pdftotext', pdf, '-'], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                content = result.stdout[:4000]
        except:
            # Fallback to python pdf miner if we can
            try:
                import fitz
                doc = fitz.open(pdf)
                for page in doc[:2]:
                    content += page.get_text()
                content = content[:4000]
            except:
                content = "Could not extract text locally."
    
    sub_project = pdf.split('/')[-3]
    filename = os.path.basename(pdf)
    if sub_project not in summaries:
        summaries[sub_project] = {}
    summaries[sub_project][filename] = content.strip().replace('\n', ' ')

with open('local_pdf_abstracts.json', 'w') as f:
    json.dump(summaries, f, indent=2)

print(f"Summarized {len(pdf_files)} PDFs.")
