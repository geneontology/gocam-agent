import pandas as pd
import json

genes_to_search = ["Gria1", "Gria2", "Gria3", "Gria4", "Adarb1", "Cacng2", "Syt7", "Kif5", "Stx4", "Snap23"]

try:
    df_genes = pd.read_excel("syngo-data/genes.xlsx")
    df_ann = pd.read_excel("syngo-data/annotations.xlsx")
    
    # We will search by gene symbol (case insensitive)
    results = {}
    for gene in genes_to_search:
        ann = df_ann[df_ann['hgnc_symbol'].str.lower() == gene.lower()]
        terms = ann[['go_id', 'go_term', 'domain']].drop_duplicates().to_dict('records')
        results[gene] = terms
        
    with open("syngo_query_results.json", "w") as f:
        json.dump(results, f, indent=2)
    print("Success")
except Exception as e:
    print("Error:", e)
