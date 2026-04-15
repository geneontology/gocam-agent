---
name: drawio
description: Generate a .drawio pathway diagram from a GO-CAM claims document. Use after completing the annotation pipeline (Phase 7) to produce agent-output/pathway_sketch.drawio. Reads shape styles and the Shape Palette page from gocam_models/network_template_draw.drawio.
---

# Skill: GO-CAM Network Sketch (draw.io)

Generate `.drawio` files for GO-CAM pathway network diagrams from a claims document.

## When to use

After completing the annotation pipeline (Phase 7), generate a network sketch as Output 5.
Input: the claims document (`expert_validation_claims.docx` or `.md`).
Output: `agent-output/pathway_sketch.drawio`.

## Dependency: template file

This skill requires `gocam_models/network_template_draw.drawio`. It copies page 1 (Shape Palette) verbatim into the output file. The template is confirmed to exist at that path — read it before generating the diagram.

## File format

A `.drawio` file is XML. The root element is `<mxfile>` containing `<diagram>` pages.
Each diagram contains an `<mxGraphModel>` with a `<root>` holding `<mxCell>` elements for nodes and edges.

## Page structure

The file must have exactly 3 pages (diagrams):

1. **Shape Palette** (`id="palette"`) — copy of the template shapes, arrows, badges, and annotation notes. Copy this verbatim from the template file at `gocam_models/network_template_draw.drawio`, page 1.
2. **Canvas** (`id="canvas"`) — the actual network diagram. You build this.
3. **Canvas 2** (`id="canvas2"`) — overflow page. Leave empty unless the network is very large.

## Building the Canvas page

### Step 1: Extract nodes and edges from the claims document

From the claims document, identify:
- **Proteins** → blue rounded rectangles
- **Small molecules** (Ca²⁺, PI(4,5)P₂) → yellow ellipses
- **Protein complexes** (AMPAR, AP-2, Calcineurin) → green dashed rounded rectangles
- **Linked processes** (NMDAR activation, endocytosis) → pink clouds
- **Positive regulation edges** → green arrows (strokeColor=#27AE60)
- **Negative regulation edges** → red arrows (strokeColor=#E74C3C)
- **Upstream context edges** (not in core model) → grey dashed arrows (strokeColor=#95A5A6)

### Step 2: Create node cells

Each node type has a specific style string. Copy exactly from the template.

**Protein / enzyme node:**
```xml
<mxCell id="[gene_symbol]" parent="1"
  style="rounded=1;whiteSpace=wrap;html=0;fillColor=#D6EAF8;strokeColor=#2980B9;strokeWidth=2;arcSize=10;verticalAlign=middle;fontSize=11;fontFamily=Arial;"
  value="[GENE_SYMBOL]&#xa;[brief role]" vertex="1">
  <mxGeometry height="68" width="168" x="[X]" y="[Y]" as="geometry" />
</mxCell>
```

**Small molecule node:**
```xml
<mxCell id="[molecule_id]" parent="1"
  style="ellipse;whiteSpace=wrap;html=0;fillColor=#FCF3CF;strokeColor=#F39C12;strokeWidth=2;verticalAlign=middle;fontSize=12;fontFamily=Arial;fontStyle=1;"
  value="[Name]" vertex="1">
  <mxGeometry height="62" width="118" x="[X]" y="[Y]" as="geometry" />
</mxCell>
```

**Complex node:**
```xml
<mxCell id="[complex_id]" parent="1"
  style="rounded=1;whiteSpace=wrap;html=0;fillColor=#D5F5E3;strokeColor=#27AE60;strokeWidth=2;dashed=1;dashPattern=8 4;arcSize=10;verticalAlign=middle;fontSize=11;fontFamily=Arial;"
  value="[Complex Name]&#xa;[subunits]" vertex="1">
  <mxGeometry height="82" width="215" x="[X]" y="[Y]" as="geometry" />
</mxCell>
```

**Linked process (cloud):**
```xml
<mxCell id="[process_id]" parent="1"
  style="ellipse;shape=cloud;whiteSpace=wrap;html=0;fillColor=#F2D7D5;strokeColor=#C0392B;strokeWidth=1.5;verticalAlign=middle;fontSize=11;fontFamily=Arial;fontStyle=1;"
  value="[Process name]" vertex="1">
  <mxGeometry height="75" width="168" x="[X]" y="[Y]" as="geometry" />
</mxCell>
```

### Step 3: Create edge cells

**Positive regulation (green arrow):**
```xml
<mxCell id="e_[source]_[target]" edge="1" parent="1" source="[source_id]" target="[target_id]"
  style="edgeStyle=orthogonalEdgeStyle;rounded=0;strokeColor=#27AE60;strokeWidth=2.5;endArrow=block;endFill=1;"
  value="">
  <mxGeometry relative="1" as="geometry" />
</mxCell>
```

**Negative regulation (red arrow):**
```xml
<mxCell id="e_[source]_[target]" edge="1" parent="1" source="[source_id]" target="[target_id]"
  style="edgeStyle=orthogonalEdgeStyle;rounded=0;strokeColor=#E74C3C;strokeWidth=2.5;endArrow=block;endFill=1;"
  value="">
  <mxGeometry relative="1" as="geometry" />
</mxCell>
```

**Upstream context (grey dashed arrow):**
```xml
<mxCell id="e_[source]_[target]" edge="1" parent="1" source="[source_id]" target="[target_id]"
  style="edgeStyle=orthogonalEdgeStyle;rounded=0;strokeColor=#95A5A6;strokeWidth=1.5;endArrow=block;endFill=0;dashed=1;dashPattern=6 4;"
  value="">
  <mxGeometry relative="1" as="geometry" />
</mxCell>
```

For edges that need waypoints (routing around other nodes), add an `<Array>` inside geometry:
```xml
<mxGeometry relative="1" as="geometry">
  <Array as="points">
    <mxPoint x="[X]" y="[Y]" />
  </Array>
</mxGeometry>
```

### Step 4: Add claim badges

Each edge gets a numbered badge corresponding to its claim number in the claims document.

**HIGH confidence badge (blue):**
```xml
<mxCell id="badge_[N]" parent="1"
  style="ellipse;whiteSpace=wrap;html=0;fillColor=#2980B9;strokeColor=none;fontColor=#FFFFFF;fontStyle=1;fontSize=10;fontFamily=Arial;verticalAlign=middle;"
  value="[N]" vertex="1">
  <mxGeometry height="22" width="28" x="[X]" y="[Y]" as="geometry" />
</mxCell>
```

**MEDIUM confidence badge (dark grey):**
```xml
<mxCell id="badge_[N]" parent="1"
  style="ellipse;whiteSpace=wrap;html=0;fillColor=#7F8C8D;strokeColor=none;fontColor=#FFFFFF;fontStyle=1;fontSize=10;fontFamily=Arial;verticalAlign=middle;"
  value="[N]" vertex="1">
  <mxGeometry height="22" width="28" x="[X]" y="[Y]" as="geometry" />
</mxCell>
```

**LOW / upstream context badge (light grey):**
```xml
<mxCell id="badge_[N]" parent="1"
  style="ellipse;whiteSpace=wrap;html=0;fillColor=#95A5A6;strokeColor=none;fontColor=#FFFFFF;fontStyle=1;fontSize=10;fontFamily=Arial;verticalAlign=middle;"
  value="[N]" vertex="1">
  <mxGeometry height="22" width="28" x="[X]" y="[Y]" as="geometry" />
</mxCell>
```

Place badges near the midpoint of their corresponding edge.

### Step 5: Add the title

```xml
<mxCell id="title" parent="1"
  style="text;html=0;fontSize=16;fontFamily=Arial;fontStyle=1;fontColor=#2C3E50;align=left;"
  value="[Pathway Name] — [Species] | GO-CAM [model ID]" vertex="1">
  <mxGeometry height="30" width="1400" x="15" y="10" as="geometry" />
</mxCell>
```

## Layout guidelines

- Canvas size: 1654 x 1169 (standard draw.io page)
- Signal flow: left-to-right or top-to-bottom. Upstream triggers on the left/bottom, downstream effectors on the right/top.
- Group spatially by pathway phase (match the claims document sections).
- Keep nodes at least 100px apart to leave room for arrows and badges.
- Node IDs should be lowercase gene symbols (e.g., `camk2a`, `pick1`, `ca2`, `ampar`).
- Edge IDs should be `e_[source]_[target]` (e.g., `e_camk2a_cacng2`).
- Badge IDs should be `badge_[N]` matching claim numbers.

## Assembly

```python
# Pseudocode for assembling the .drawio file
palette_xml = read_page_1_from("gocam_models/network_template_draw.drawio")
canvas_xml = build_canvas(nodes, edges, badges, title)
canvas2_xml = empty_canvas()

output = f'''<mxfile host="app.diagrams.net" pages="3">
{palette_xml}
{canvas_xml}
{canvas2_xml}
</mxfile>'''

write("agent-output/pathway_sketch.drawio", output)
```

## Validation

After generating the file:
1. Verify it is valid XML (no unclosed tags, proper escaping of `&` as `&amp;`, `<` as `&lt;`)
2. Verify every claim badge number exists in the claims document
3. Verify every edge has both a source and target that exist as node IDs
4. Verify the 3-page structure is intact
5. Note: the file can be opened in draw.io (app.diagrams.net) or VS Code with the draw.io extension
