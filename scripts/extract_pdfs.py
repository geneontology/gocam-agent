import os
import fitz  # PyMuPDF
import json
import glob

def extract_intro(folder):
    data = {}
    for filepath in glob.glob(folder + "/*.pdf"):
        try:
            doc = fitz.open(filepath)
            text = doc[0].get_text()[:1500].replace('\n', ' ')
            data[os.path.basename(filepath)] = text
        except Exception as e:
            data[os.path.basename(filepath)] = str(e)
    return data

ampar_pdfs = extract_intro("gocam_models/ampar-endocytosis/literature")
svr_pdfs = extract_intro("gocam_models/synaptic-vesicle-recycling/literature")
reviews = extract_intro("gocam_models/AMPAR/reviews")

with open("pdf_summaries.json", "w") as f:
    json.dump({"ampar": ampar_pdfs, "svr": svr_pdfs, "reviews": reviews}, f, indent=2)

print(f"Extracted {len(ampar_pdfs)} AMPAR, {len(svr_pdfs)} SVR, {len(reviews)} reviews.")
