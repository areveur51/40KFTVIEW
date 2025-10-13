#!/usr/bin/env python3
"""
Script to fix broken links in main.py by removing edges that reference non-existent nodes.
"""

import re
import sys


def find_broken_edges():
    """Find all edges that reference non-existent nodes."""
    with open('main.py', 'r') as f:
        content = f.read()
    
    # Extract all node names
    graphic_names = set(re.findall(r'"graphicName":\s*"([^"]+)"', content))
    print(f"Found {len(graphic_names)} nodes")
    
    # Find all edges
    edge_pattern = r"\{\s*'source':\s*'([^']+)',\s*'target':\s*'([^']+)',\s*'label':\s*\"([^\"]*)\",\s*'metadata':\s*default_edge_metadata\s*\}"
    edges = list(re.finditer(edge_pattern, content))
    print(f"Found {len(edges)} edges")
    
    broken_edges = []
    for match in edges:
        source = match.group(1)
        target = match.group(2)
        label = match.group(3)
        
        missing = []
        if source not in graphic_names:
            missing.append(f"source '{source}'")
        if target not in graphic_names:
            missing.append(f"target '{target}'")
        
        if missing:
            broken_edges.append({
                'match': match,
                'source': source,
                'target': target,
                'label': label,
                'missing': missing,
                'full_text': match.group(0)
            })
    
    return broken_edges


def fix_broken_edges(broken_edges, dry_run=True):
    """Remove broken edges from main.py."""
    if not broken_edges:
        print("No broken edges to fix!")
        return
    
    with open('main.py', 'r') as f:
        content = f.read()
    
    print(f"\nFound {len(broken_edges)} broken edges:")
    print("=" * 80)
    
    for i, edge in enumerate(broken_edges, 1):
        print(f"\n{i}. {edge['source']} -> {edge['target']}")
        print(f"   Label: {edge['label']}")
        print(f"   Missing: {', '.join(edge['missing'])}")
        
        if not dry_run:
            # Remove the edge and the comma before it
            # Look for the pattern with optional comma and newline
            patterns_to_try = [
                f",\n                {re.escape(edge['full_text'])}",  # With comma before
                f"\n                {re.escape(edge['full_text'])},",  # With comma after
                f"{re.escape(edge['full_text'])}",  # Just the edge itself
            ]
            
            for pattern in patterns_to_try:
                if pattern in content:
                    content = content.replace(pattern, '', 1)
                    print(f"   ✓ Removed")
                    break
    
    if dry_run:
        print("\n" + "=" * 80)
        print("DRY RUN - No changes made to main.py")
        print("Run with --fix to actually remove broken edges")
    else:
        with open('main.py', 'w') as f:
            f.write(content)
        print("\n" + "=" * 80)
        print(f"✓ Fixed {len(broken_edges)} broken edges in main.py")


def main():
    broken_edges = find_broken_edges()
    
    dry_run = '--fix' not in sys.argv
    fix_broken_edges(broken_edges, dry_run=dry_run)


if __name__ == '__main__':
    main()
