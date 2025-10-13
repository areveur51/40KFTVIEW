#!/usr/bin/env python3
"""
Test script to verify data consistency between backend (main.py) and frontend (template).

This script checks:
1. All edge source/target nodes exist in the node data
2. No broken links or undefined references  
3. Backend and frontend data structures match
"""

import json
import re
import sys
from pathlib import Path


def extract_nodes_from_main():
    """Extract all node names from the data array in main.py."""
    with open('main.py', 'r') as f:
        content = f.read()
    
    # Find all graphicName values (they appear in the data array)
    graphic_names = re.findall(r'"graphicName":\s*"([^"]+)"', content)
    
    if not graphic_names:
        print("ERROR: Could not find any graphicName values in main.py")
        return set()
    
    return set(graphic_names)


def extract_edges_from_main():
    """Extract all edges from graph5 in main.py."""
    with open('main.py', 'r') as f:
        content = f.read()
    
    # Find all edges in graph5
    edges = []
    edge_pattern = r"'source':\s*'([^']+)',\s*'target':\s*'([^']+)',\s*'label':\s*\"([^\"]*)\""
    matches = re.findall(edge_pattern, content)
    
    for source, target, label in matches:
        edges.append({
            'source': source,
            'target': target,
            'label': label
        })
    
    return edges


def extract_frontend_data(template_path='templates/index.html'):
    """Extract data from the generated frontend template."""
    if not Path(template_path).exists():
        print(f"WARNING: Template {template_path} does not exist")
        return None
    
    with open(template_path, 'r') as f:
        content = f.read()
    
    # Find the state.rawData assignment
    pattern = r'state\.rawData = (\[.*?\]);'
    match = re.search(pattern, content, re.DOTALL)
    
    if not match:
        print("ERROR: Could not find state.rawData in template")
        return None
    
    try:
        raw_data_str = match.group(1)
        # Parse JSON
        raw_data = json.loads(raw_data_str)
        return raw_data[0] if raw_data else None
    except json.JSONDecodeError as e:
        print(f"ERROR: Could not parse frontend data: {e}")
        return None


def check_backend_consistency():
    """Check that all edges in backend reference existing nodes."""
    print("=" * 80)
    print("BACKEND DATA CONSISTENCY CHECK")
    print("=" * 80)
    
    nodes = extract_nodes_from_main()
    edges = extract_edges_from_main()
    
    print(f"\nTotal nodes found: {len(nodes)}")
    print(f"Total edges found: {len(edges)}")
    
    # Check for broken links
    broken_links = []
    
    for edge in edges:
        source = edge['source']
        target = edge['target']
        label = edge['label']
        
        if source not in nodes:
            broken_links.append({
                'type': 'missing_source',
                'source': source,
                'target': target,
                'label': label,
                'message': f"Source node '{source}' does not exist"
            })
        
        if target not in nodes:
            broken_links.append({
                'type': 'missing_target',
                'source': source,
                'target': target,
                'label': label,
                'message': f"Target node '{target}' does not exist"
            })
    
    if broken_links:
        print(f"\n❌ FOUND {len(broken_links)} BROKEN LINKS:")
        print("-" * 80)
        for i, link in enumerate(broken_links, 1):
            print(f"\n{i}. {link['message']}")
            print(f"   Edge: {link['source']} -> {link['target']}")
            if link['label']:
                print(f"   Label: {link['label']}")
    else:
        print("\n✅ All edges reference valid nodes!")
    
    return len(broken_links) == 0


def compare_backend_frontend():
    """Compare backend data with frontend data."""
    print("\n" + "=" * 80)
    print("BACKEND vs FRONTEND COMPARISON")
    print("=" * 80)
    
    # Get backend data
    backend_nodes = extract_nodes_from_main()
    backend_edges = extract_edges_from_main()
    
    # Get frontend data
    frontend_data = extract_frontend_data()
    
    if not frontend_data:
        print("\n⚠️  Cannot compare - frontend template not found or invalid")
        return False
    
    frontend_nodes = set(frontend_data.get('nodes', {}).keys())
    frontend_edges = frontend_data.get('edges', [])
    
    # Frontend edges should be a list of dicts
    try:
        frontend_edge_tuples = {(e['source'], e['target']) for e in frontend_edges if isinstance(e, dict)}
    except (TypeError, KeyError) as ex:
        print(f"WARNING: Could not parse frontend edges: {ex}")
        frontend_edge_tuples = set()
    
    print(f"\nBackend nodes: {len(backend_nodes)}")
    print(f"Frontend nodes: {len(frontend_nodes)}")
    print(f"\nBackend edges: {len(backend_edges)}")
    print(f"Frontend edges: {len(frontend_edges)}")
    
    # Check node consistency
    missing_in_frontend = backend_nodes - frontend_nodes
    missing_in_backend = frontend_nodes - backend_nodes
    
    if missing_in_frontend:
        print(f"\n❌ {len(missing_in_frontend)} nodes in backend but NOT in frontend:")
        for node in sorted(missing_in_frontend)[:10]:  # Show first 10
            print(f"   - {node}")
        if len(missing_in_frontend) > 10:
            print(f"   ... and {len(missing_in_frontend) - 10} more")
    
    if missing_in_backend:
        print(f"\n❌ {len(missing_in_backend)} nodes in frontend but NOT in backend:")
        for node in sorted(missing_in_backend)[:10]:  # Show first 10
            print(f"   - {node}")
        if len(missing_in_backend) > 10:
            print(f"   ... and {len(missing_in_backend) - 10} more")
    
    # Check edge consistency
    backend_edge_tuples = {(e['source'], e['target']) for e in backend_edges}
    
    missing_edges_in_frontend = backend_edge_tuples - frontend_edge_tuples
    missing_edges_in_backend = frontend_edge_tuples - backend_edge_tuples
    
    if missing_edges_in_frontend:
        print(f"\n❌ {len(missing_edges_in_frontend)} edges in backend but NOT in frontend:")
        for source, target in list(missing_edges_in_frontend)[:10]:
            print(f"   - {source} -> {target}")
        if len(missing_edges_in_frontend) > 10:
            print(f"   ... and {len(missing_edges_in_frontend) - 10} more")
    
    if missing_edges_in_backend:
        print(f"\n❌ {len(missing_edges_in_backend)} edges in frontend but NOT in backend:")
        for source, target in list(missing_edges_in_backend)[:10]:
            print(f"   - {source} -> {target}")
        if len(missing_edges_in_backend) > 10:
            print(f"   ... and {len(missing_edges_in_backend) - 10} more")
    
    # Final verdict
    if (not missing_in_frontend and not missing_in_backend and 
        not missing_edges_in_frontend and not missing_edges_in_backend):
        print("\n✅ Backend and frontend data are CONSISTENT!")
        return True
    else:
        print("\n❌ Backend and frontend data are INCONSISTENT!")
        return False


def main():
    """Run all consistency checks."""
    print("\n" + "=" * 80)
    print("DATA CONSISTENCY TEST SUITE")
    print("=" * 80)
    
    backend_ok = check_backend_consistency()
    frontend_ok = compare_backend_frontend()
    
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Backend consistency: {'✅ PASS' if backend_ok else '❌ FAIL'}")
    print(f"Backend-Frontend sync: {'✅ PASS' if frontend_ok else '❌ FAIL'}")
    
    if backend_ok and frontend_ok:
        print("\n🎉 All tests PASSED!")
        return 0
    else:
        print("\n⚠️  Some tests FAILED - see details above")
        return 1


if __name__ == '__main__':
    sys.exit(main())
