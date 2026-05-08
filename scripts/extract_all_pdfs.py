import pypdf
import glob

pdf_files = glob.glob("gocam_models/priming-docking-exocytosis/literature/*.pdf")

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
