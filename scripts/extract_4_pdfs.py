import pypdf
import glob
import os

directories = [
    "gocam_models/AMPAR/ampar-synthesis-assembly/literature",
    "gocam_models/AMPAR/ampar-secretory-trafficking/literature",
    "gocam_models/AMPAR/ampar-synaptic-insertion/literature",
    "gocam_models/AMPAR/ampar-lateral-diffusion/literature"
]

for directory in directories:
    pdf_files = glob.glob(f"{directory}/*.pdf")
    for pdf in pdf_files:
        try:
            reader = pypdf.PdfReader(pdf)
            text = ""
            for page in reader.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"
            
            out_path = pdf + ".txt"
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(text)
            print(f"Extracted {pdf} to {out_path}")
        except Exception as e:
            print(f"Failed {pdf}: {e}")
