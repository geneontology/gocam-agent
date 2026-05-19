import os
import json
import subprocess
import concurrent.futures

with open('local_pdf_abstracts.json', 'r') as f:
    pdf_abstracts = json.load(f)

with open('gocam_models/AMPAR/gemini-analysis/project_definitions-gemini.md', 'r') as f:
    baseline_defs = f.read()

with open('gocam_models/peer_reviewer_prompt.md', 'r') as f:
    peer_prompt = f.read()

with open('gocam_models/go_cam_curator_prompt.md', 'r') as f:
    gocam_prompt = f.read()

sub_processes = [
    'ampar-synthesis-assembly', 'ampar-secretory-trafficking', 'ampar-synaptic-insertion',
    'ampar-lateral-diffusion', 'ampar-anchoring', 'ampar-unanchoring',
    'ampar-endocytic-priming', 'ampar-endocytosis', 'ampar-postendocytic-sorting',
    'ampar-recycling', 'ampar-lysosomal-degradation'
]

def generate_process_def(sub):
    print(f"Starting {sub}...")
    
    # Extract baseline block for this sub
    try:
        baseline_start = baseline_defs.find("## ")
        block_start = baseline_defs.find(sub, baseline_start)
        block_end = baseline_defs.find("## ", block_start)
        if block_end == -1:
            block = baseline_defs[block_start:]
        else:
            block = baseline_defs[block_start:block_end]
    except:
        block = "Baseline not found."

    abstracts_text = ""
    if sub in pdf_abstracts:
        for pdf, text in pdf_abstracts[sub].items():
            abstracts_text += f"\n--- PDF: {pdf} ---\n{text}\n"

    # Molecular question to append
    q = f"Question for {sub}: Based strictly on the provided PDFs, what are the specific molecular functions (e.g. kinase activity, GTPase activity), biological processes, and cellular components? Follow the 'no binding' rule."

    prompt = f"""You are a strict GO-CAM Curator and Peer Reviewer. Your task is to generate a highly detailed, high-resolution GO-CAM process definition for the AMPAR sub-process '{sub}'.

{peer_prompt[:1500]}

{gocam_prompt[:1500]}

{q}

Here is the baseline process definition:
{block}

Here are the extracted texts from the relevant PDFs in this sub-process folder:
{abstracts_text}

Instructions:
1. Develop a high-resolution GO-CAM process definition for '{sub}'.
2. Include the 'Process Summary', 'START', 'Mechanism', 'Key Actors/Functions' (strictly using GO terms and NO BINDING for MF), 'END', and 'Grounding' (citing the specific PMIDs provided).
3. Do NOT hallucinate. Rely ONLY on the provided PDF text and baseline.
4. Output ONLY the raw Markdown content. Do not include markdown code block wrappers (like ```markdown).

Generate the file content now:
"""
    
    out_path = f"gocam_models/AMPAR/{sub}/process_definitions_gemini.md"
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    
    try:
        # Run gemini -p in headless mode to act as the subagent
        result = subprocess.run(
            ['gemini', '-p', prompt, '--output-format', 'text'],
            capture_output=True, text=True, timeout=120
        )
        with open(out_path, 'w') as f:
            # clean output of markdown wrappers if present
            out_text = result.stdout.strip()
            if out_text.startswith("```markdown"):
                out_text = out_text[11:]
            if out_text.startswith("```"):
                out_text = out_text[3:]
            if out_text.endswith("```"):
                out_text = out_text[:-3]
            f.write(out_text.strip())
        print(f"Finished {sub}")
    except Exception as e:
        print(f"Failed {sub}: {e}")

# Run concurrently
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
    executor.map(generate_process_def, sub_processes)

print("Done")
