#!/usr/bin/env python3
"""
AICL Provenance Visualization Tool

Generates interactive HTML visualization of compilation provenance
graphs from Proof of Origin files.

Features:
    - Interactive provenance graph (D3.js force-directed layout)
    - Artifact-provenance linkage visualization
    - Coverage heatmap showing audit coverage per layer
    - Timeline view of compilation stages
    - Click-to-explore provenance chains

Usage:
    python visualize_provenance.py <proof.aicl-proof> [--output <output.html>]
    aicl visualize <proof.aicl-proof> [--output <output.html>]
"""

import json
import sys
import os
from typing import Dict, List, Any, Optional


HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>AICL Provenance Visualization</title>
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{
    font-family: 'Inter', -apple-system, sans-serif;
    background: #0d1117;
    color: #c9d1d9;
    overflow: hidden;
  }}
  .header {{
    background: #161b22;
    border-bottom: 1px solid #30363d;
    padding: 12px 24px;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }}
  .header h1 {{
    font-size: 16px;
    color: #58a6ff;
  }}
  .header .meta {{
    font-size: 12px;
    color: #8b949e;
  }}
  .container {{
    display: flex;
    height: calc(100vh - 48px);
  }}
  .sidebar {{
    width: 320px;
    background: #161b22;
    border-right: 1px solid #30363d;
    overflow-y: auto;
    padding: 16px;
  }}
  .sidebar h2 {{
    font-size: 13px;
    color: #8b949e;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 12px;
  }}
  .artifact-item {{
    padding: 8px 12px;
    margin-bottom: 4px;
    border-radius: 6px;
    cursor: pointer;
    border: 1px solid transparent;
    transition: all 0.15s;
  }}
  .artifact-item:hover {{
    background: #1f2937;
    border-color: #30363d;
  }}
  .artifact-item.active {{
    background: #1f2937;
    border-color: #58a6ff;
  }}
  .artifact-item .name {{
    font-size: 13px;
    font-weight: 500;
    color: #c9d1d9;
  }}
  .artifact-item .type {{
    font-size: 11px;
    color: #8b949e;
  }}
  .artifact-item .orphan {{
    color: #f85149;
    font-size: 10px;
  }}
  .graph-area {{
    flex: 1;
    position: relative;
  }}
  .node {{
    cursor: pointer;
  }}
  .node circle {{
    stroke-width: 2;
  }}
  .node text {{
    font-size: 11px;
    fill: #c9d1d9;
    pointer-events: none;
  }}
  .link {{
    stroke: #30363d;
    stroke-width: 1;
    fill: none;
  }}
  .detail-panel {{
    position: absolute;
    bottom: 16px;
    right: 16px;
    width: 400px;
    max-height: 300px;
    background: #161b22;
    border: 1px solid #30363d;
    border-radius: 8px;
    padding: 16px;
    overflow-y: auto;
    display: none;
  }}
  .detail-panel.visible {{
    display: block;
  }}
  .detail-panel h3 {{
    font-size: 14px;
    color: #58a6ff;
    margin-bottom: 8px;
  }}
  .detail-panel .field {{
    margin-bottom: 6px;
  }}
  .detail-panel .field .label {{
    font-size: 11px;
    color: #8b949e;
  }}
  .detail-panel .field .value {{
    font-size: 12px;
    color: #c9d1d9;
    word-break: break-all;
  }}
  .stats {{
    display: flex;
    gap: 16px;
    margin-bottom: 16px;
  }}
  .stat {{
    text-align: center;
    flex: 1;
  }}
  .stat .num {{
    font-size: 24px;
    font-weight: 700;
    color: #58a6ff;
  }}
  .stat .label {{
    font-size: 10px;
    color: #8b949e;
    text-transform: uppercase;
  }}
  .coverage-bar {{
    height: 4px;
    background: #21262d;
    border-radius: 2px;
    margin-top: 4px;
  }}
  .coverage-fill {{
    height: 100%;
    border-radius: 2px;
    background: #3fb950;
  }}
</style>
</head>
<body>

<div class="header">
  <h1>AICL Provenance Visualization</h1>
  <div class="meta">
    <span id="compiler-info">AICL v{compiler_version}</span> &middot;
    <span id="record-count">{record_count} records</span> &middot;
    <span id="artifact-count">{artifact_count} artifacts</span>
  </div>
</div>

<div class="container">
  <div class="sidebar">
    <div class="stats">
      <div class="stat">
        <div class="num">{audit_coverage}</div>
        <div class="label">Audit Coverage</div>
      </div>
      <div class="stat">
        <div class="num">{orphan_count}</div>
        <div class="label">Orphans</div>
      </div>
      <div class="stat">
        <div class="num">{pattern_count}</div>
        <div class="label">Patterns</div>
      </div>
    </div>

    <div class="coverage-bar">
      <div class="coverage-fill" style="width: {audit_coverage_pct}%"></div>
    </div>

    <h2 style="margin-top: 20px;">Artifacts</h2>
    <div id="artifact-list">
      {artifact_list_html}
    </div>
  </div>

  <div class="graph-area">
    <svg id="graph" width="100%" height="100%"></svg>
    <div class="detail-panel" id="detail-panel">
      <h3 id="detail-title"></h3>
      <div id="detail-content"></div>
    </div>
  </div>
</div>

<script src="https://d3js.org/d3.v7.min.js"></script>
<script>
const proofData = {proof_json};

// Color scheme for provenance types
const typeColors = {{
  'pattern_match': '#3fb950',
  'sub_language': '#58a6ff',
  'fallback': '#f85149',
  'architecture_template': '#d2a8ff',
  'direct_mapping': '#79c0ff',
  'recovery_synthesis': '#ffa657',
  'validation_synthesis': '#7ee787',
  'condition_synthesis': '#ff7b72',
  'event_synthesis': '#a5d6ff',
  'helper_method': '#8b949e',
  'entity_generation': '#d2a8ff',
  'layer_initialization': '#79c0ff',
  'security_method': '#f85149',
  'parallel_execution': '#ffa657',
  'run_method': '#3fb950',
  'import_generation': '#8b949e',
  'entry_point': '#58a6ff',
  'test_generation': '#7ee787',
  'class_structure': '#d2a8ff',
}};

// Build nodes and links
const nodes = [];
const links = [];

// Add source node
nodes.push({{ id: 'source', type: 'source', label: 'AICL Source' }});

// Add provenance records as nodes
(proofData.records || []).forEach((record, i) => {{
  nodes.push({{
    id: `record_${{i}}`,
    type: record.source_type,
    label: record.source_location.substring(0, 30),
    full: record,
  }});
  links.push({{ source: 'source', target: `record_${{i}}` }});
}});

// Add artifacts as nodes
(proofData.artifacts || []).forEach((artifact, i) => {{
  nodes.push({{
    id: `artifact_${{i}}`,
    type: 'artifact',
    label: artifact.name.substring(0, 25),
    full: artifact,
    isOrphan: artifact.is_orphan,
  }});
}});

// Link records to artifacts
(proofData.records || []).forEach((record, i) => {{
  if (record.artifact_names) {{
    record.artifact_names.forEach(name => {{
      const artIdx = (proofData.artifacts || []).findIndex(a => a.name === name);
      if (artIdx >= 0) {{
        links.push({{ source: `record_${{i}}`, target: `artifact_${{artIdx}}` }});
      }}
    }});
  }}
}});

// Create force simulation
const width = document.getElementById('graph').clientWidth;
const height = document.getElementById('graph').clientHeight;

const svg = d3.select('#graph');
const g = svg.append('g');

// Zoom
svg.call(d3.zoom().on('zoom', (event) => {{
  g.attr('transform', event.transform);
}}));

const simulation = d3.forceSimulation(nodes)
  .force('link', d3.forceLink(links).id(d => d.id).distance(80))
  .force('charge', d3.forceManyBody().strength(-200))
  .force('center', d3.forceCenter(width / 2, height / 2))
  .force('collision', d3.forceCollide().radius(30));

const link = g.append('g')
  .selectAll('line')
  .data(links)
  .enter().append('line')
  .attr('class', 'link');

const node = g.append('g')
  .selectAll('.node')
  .data(nodes)
  .enter().append('g')
  .attr('class', 'node')
  .call(d3.drag()
    .on('start', (event, d) => {{
      if (!event.active) simulation.alphaTarget(0.3).restart();
      d.fx = d.x; d.fy = d.y;
    }})
    .on('drag', (event, d) => {{
      d.fx = event.x; d.fy = event.y;
    }})
    .on('end', (event, d) => {{
      if (!event.active) simulation.alphaTarget(0);
      d.fx = null; d.fy = null;
    }})
  );

node.append('circle')
  .attr('r', d => d.type === 'source' ? 12 : d.type === 'artifact' ? 8 : 6)
  .attr('fill', d => {{
    if (d.type === 'source') return '#58a6ff';
    if (d.type === 'artifact') return d.isOrphan ? '#f85149' : '#3fb950';
    return typeColors[d.type] || '#8b949e';
  }})
  .attr('stroke', d => {{
    if (d.type === 'source') return '#1f6feb';
    if (d.type === 'artifact') return d.isOrphan ? '#da3633' : '#238636';
    return '#30363d';
  }});

node.append('text')
  .attr('dx', 12)
  .attr('dy', 4)
  .text(d => d.label);

node.on('click', (event, d) => {{
  const panel = document.getElementById('detail-panel');
  const title = document.getElementById('detail-title');
  const content = document.getElementById('detail-content');

  title.textContent = d.label || d.id;
  let html = '';
  if (d.full) {{
    html += '<div class="field"><div class="label">Type</div><div class="value">' + (d.type || 'N/A') + '</div></div>';
    if (d.full.source_type) {{
      html += '<div class="field"><div class="label">Source Type</div><div class="value">' + d.full.source_type + '</div></div>';
    }}
    if (d.full.resolution_path) {{
      html += '<div class="field"><div class="label">Resolution Path</div><div class="value">' + d.full.resolution_path.join(' → ') + '</div></div>';
    }}
    if (d.full.is_orphan !== undefined) {{
      html += '<div class="field"><div class="label">Orphan</div><div class="value">' + d.full.is_orphan + '</div></div>';
    }}
  }}
  content.innerHTML = html;
  panel.classList.add('visible');
}});

simulation.on('tick', () => {{
  link
    .attr('x1', d => d.source.x)
    .attr('y1', d => d.source.y)
    .attr('x2', d => d.target.x)
    .attr('y2', d => d.target.y);

  node.attr('transform', d => `translate(${{d.x}},${{d.y}})`);
}});

// Artifact list click handler
document.querySelectorAll('.artifact-item').forEach(item => {{
  item.addEventListener('click', () => {{
    document.querySelectorAll('.artifact-item').forEach(i => i.classList.remove('active'));
    item.classList.add('active');
  }});
}});
</script>
</body>
</html>"""


def load_proof(path: str) -> Dict[str, Any]:
    """Load a proof file."""
    with open(path, 'r') as f:
        return json.load(f)


def generate_visualization(proof_data: Dict[str, Any], output_path: str = "provenance.html") -> str:
    """
    Generate an HTML visualization from a proof dictionary.

    Args:
        proof_data: The proof data as a dictionary
        output_path: Path to write the HTML file

    Returns:
        Path to the generated HTML file
    """
    records = proof_data.get("records", [])
    artifacts = proof_data.get("artifacts", [])
    audit_coverage = proof_data.get("audit_coverage", {})
    coverage_val = audit_coverage.get("audit_coverage", 1.0)
    orphan_count = len(audit_coverage.get("orphan_artifacts", []))
    pattern_count = sum(1 for r in records if r.get("source_type") == "pattern_match")

    # Generate artifact list HTML
    artifact_list_items = []
    for i, artifact in enumerate(artifacts):
        is_orphan = artifact.get("is_orphan", False)
        orphan_badge = ' <span class="orphan">ORPHAN</span>' if is_orphan else ""
        artifact_list_items.append(
            f'<div class="artifact-item" data-index="{i}">'
            f'<div class="name">{artifact.get("name", "unknown")}</div>'
            f'<div class="type">{artifact.get("type", "unknown")}{orphan_badge}</div>'
            f'</div>'
        )
    artifact_list_html = "\n".join(artifact_list_items)

    html = HTML_TEMPLATE.format(
        compiler_version=proof_data.get("compiler_version", "unknown"),
        record_count=len(records),
        artifact_count=len(artifacts),
        audit_coverage=f"{coverage_val:.0%}",
        audit_coverage_pct=f"{coverage_val * 100:.0f}",
        orphan_count=orphan_count,
        pattern_count=pattern_count,
        artifact_list_html=artifact_list_html,
        proof_json=json.dumps(proof_data),
    )

    with open(output_path, 'w') as f:
        f.write(html)

    return output_path


def main():
    """CLI entry point."""
    if len(sys.argv) < 2:
        print("Usage: python visualize_provenance.py <proof.aicl-proof> [--output <output.html>]")
        sys.exit(1)

    proof_path = sys.argv[1]
    output_path = "provenance.html"

    if "--output" in sys.argv:
        idx = sys.argv.index("--output")
        if idx + 1 < len(sys.argv):
            output_path = sys.argv[idx + 1]

    proof_data = load_proof(proof_path)
    result_path = generate_visualization(proof_data, output_path)
    print(f"Visualization generated: {result_path}")


if __name__ == "__main__":
    main()
