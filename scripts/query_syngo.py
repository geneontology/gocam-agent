import pandas as pd
import json

try:
    df = pd.read_excel("syngo-data/annotations.xlsx")
    proteasome_genes = df[df['hgnc_symbol'].str.contains('PSM', na=False)]['hgnc_symbol'].unique()
    ampar_genes = df[df['hgnc_symbol'].str.contains('GRIA', na=False)]['hgnc_symbol'].unique()
    
    out = {
        "proteasome_genes_in_syngo": list(proteasome_genes),
        "ampar_genes_in_syngo": list(ampar_genes)
    }
    with open("syngo_insights.json", "w") as f:
        json.dump(out, f, indent=2)
    print("Success")
except Exception as e:
    print("Error:", e)
