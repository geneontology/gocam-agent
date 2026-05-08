import os
import json
from google import genai
from google.genai import types

# Initialize client using environment variables
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

with open("pdf_summaries.json", "r") as f:
    data = json.load(f)

# Combine the data into a single prompt text
prompt = """
You are an expert GO-CAM annotation curator and senior peer reviewer in molecular and cellular biology.

I have a dataset of PDF texts (first 1500 chars) related to the AMPA receptor trafficking lifecycle (8 stages: 1. ampar-synthesis-assembly, 2. ampar-secretory-trafficking, 3. ampar-anchoring, 4. ampar-diffusion, 5. ampar-recruitment, 6. ampar-endocytosis, 7. ampar-postendocytic-sorting, 8. ampar-degradation).

Also included is the synaptic vesicle recycling (SVR) project and a new review about the synaptic proteasome.

Task 1: Generate the content for 'literature-overview-gemini.md'.
Assign each PDF filename in the dataset to one or more of the 8 AMPAR sub-processes.
If a PDF (e.g., from the SVR project) does not fit any of the AMPAR processes, add it to 'Unassigned' with a short (max 1 sentence) reason.

Task 2: Generate the content for 'enrichment-gemini.md'.
Based on the reviews (including the synaptic proteasome review) and your general knowledge (simulating PubMed search), detail the missing literature that is important and needs to be added. 
Include the specific sub-process it is relevant for and in max 1 sentence why. Do not harvest the PDFs from PubMed yourself.

Output format MUST be a JSON object with two keys: "literature_overview" and "enrichment", containing the raw markdown strings for each file.

Dataset:
"""

prompt += json.dumps(data, indent=2)[:80000] # Truncate if too large to fit in context window, but 59 * 1500 = ~90k chars, well within 1M token limit.

response = client.models.generate_content(
    model='gemini-1.5-flash',
    contents=prompt,
    config=types.GenerateContentConfig(
        response_mime_type="application/json",
    ),
)

import json
output = json.loads(response.text)

os.makedirs("gocam_models/ampar-endocytosis/sub-projects/gemini-analysis", exist_ok=True)

with open("gocam_models/ampar-endocytosis/sub-projects/gemini-analysis/literature-overview-gemini.md", "w") as f:
    f.write(output.get("literature_overview", "# Error"))

with open("gocam_models/ampar-endocytosis/sub-projects/gemini-analysis/enrichment-gemini.md", "w") as f:
    f.write(output.get("enrichment", "# Error"))

with open("gocam_models/ampar-endocytosis/sub-projects/gemini-analysis/current-gocams-overview-gemini.md", "w") as f:
    f.write("no access")

print("Files generated successfully.")
