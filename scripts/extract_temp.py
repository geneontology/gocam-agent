import fitz
import sys

pdf_paths = [
    "gocam_models/AMPAR/ampar-postendocytic-sorting/literature/20098723.pdf",
    "gocam_models/AMPAR/ampar-postendocytic-sorting/literature/18984164.pdf",
    "gocam_models/AMPAR/ampar-recycling/literature/18045925.pdf",
    "gocam_models/AMPAR/ampar-lysosomal-degradation/literature/21338354.pdf",
    "gocam_models/AMPAR/ampar-lysosomal-degradation/literature/11144360.pdf"
]

for p in pdf_paths:
    try:
        doc = fitz.open(p)
        text = ""
        for page in doc:
            text += page.get_text() + "\n"
        with open(p.replace('.pdf', '.txt'), 'w', encoding='utf-8') as f:
            f.write(text)
        print(f"Extracted {p}")
    except Exception as e:
        print(f"Failed {p}: {e}")
