#!/usr/bin/env python3
"""
Extract node and edge data from main.py to separate JSON files.
"""

import json
import re

def extract_nodes_from_main():
    """Extract node data array from main.py"""
    with open('main.py', 'r') as f:
        content = f.read()
    
    # Find the data array
    data_pattern = r'data = \[(.*?)\]\s+default_color'
    match = re.search(data_pattern, content, re.DOTALL)
    
    if not match:
        print("Could not find data array in main.py")
        return []
    
    # Extract individual node dictionaries
    data_section = match.group(1)
    
    # Parse each node dictionary
    nodes = []
    node_pattern = r'\{[^}]+\}'
    
    for node_match in re.finditer(node_pattern, data_section):
        node_text = node_match.group(0)
        
        # Extract fields
        label_match = re.search(r'"graphicLabel":\s*"([^"]*)"', node_text)
        name_match = re.search(r'"graphicName":\s*"([^"]*)"', node_text)
        post_match = re.search(r'"xPostURL":\s*"([^"]*)"', node_text)
        graphic_match = re.search(r'"xGraphicURL":\s*"([^"]*)"', node_text)
        
        if label_match and name_match and post_match and graphic_match:
            nodes.append({
                "graphicLabel": label_match.group(1),
                "graphicName": name_match.group(1),
                "xPostURL": post_match.group(1),
                "xGraphicURL": graphic_match.group(1)
            })
    
    return nodes

def extract_edges_from_main():
    """Extract edge data from main.py"""
    with open('main.py', 'r') as f:
        content = f.read()
    
    # Find the edges array
    edges_pattern = r"'edges':\s*\[(.*?)\]\s*\}\s*\}"
    match = re.search(edges_pattern, content, re.DOTALL)
    
    if not match:
        print("Could not find edges array in main.py")
        return []
    
    edges_section = match.group(1)
    
    # Parse each edge dictionary
    edges = []
    edge_pattern = r'\{[^}]+\}'
    
    for edge_match in re.finditer(edge_pattern, edges_section):
        edge_text = edge_match.group(0)
        
        # Extract fields
        source_match = re.search(r"'source':\s*'([^']*)'", edge_text)
        target_match = re.search(r"'target':\s*'([^']*)'", edge_text)
        label_match = re.search(r"'label':\s*['\"]([^'\"]*)['\"]", edge_text)
        
        if source_match and target_match:
            edge = {
                "source": source_match.group(1),
                "target": target_match.group(1),
                "label": label_match.group(1) if label_match else ""
            }
            edges.append(edge)
    
    return edges

def main():
    # Extract nodes
    print("Extracting nodes from main.py...")
    nodes = extract_nodes_from_main()
    print(f"  Found {len(nodes)} nodes")
    
    # Save nodes
    with open('data/nodes.json', 'w') as f:
        json.dump(nodes, f, indent=2)
    print(f"  ✓ Saved to data/nodes.json")
    
    # Extract edges
    print("\nExtracting edges from main.py...")
    edges = extract_edges_from_main()
    print(f"  Found {len(edges)} edges")
    
    # Save edges
    with open('data/edges.json', 'w') as f:
        json.dump(edges, f, indent=2)
    print(f"  ✓ Saved to data/edges.json")
    
    print("\n✓ Data extraction complete!")

if __name__ == "__main__":
    main()
