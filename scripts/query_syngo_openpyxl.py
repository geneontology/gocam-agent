import openpyxl
import json

try:
    wb = openpyxl.load_workbook("syngo-data/annotations.xlsx")
    sheet = wb.active
    
    # Assume row 1 has headers, find 'hgnc_symbol'
    headers = [cell.value for cell in sheet[1]]
    symbol_idx = headers.index('hgnc_symbol') if 'hgnc_symbol' in headers else -1
    
    if symbol_idx != -1:
        proteasome_genes = set()
        ampar_genes = set()
        for row in sheet.iter_rows(min_row=2, values_only=True):
            symbol = str(row[symbol_idx])
            if 'PSM' in symbol:
                proteasome_genes.add(symbol)
            if 'GRIA' in symbol:
                ampar_genes.add(symbol)
                
        out = {
            "proteasome_genes_in_syngo": list(proteasome_genes),
            "ampar_genes_in_syngo": list(ampar_genes)
        }
        with open("syngo_insights.json", "w") as f:
            json.dump(out, f, indent=2)
        print("Success")
    else:
        print("hgnc_symbol header not found")
except Exception as e:
    print("Error:", e)
