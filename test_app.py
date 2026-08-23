#!/usr/bin/env python3
"""
Comprehensive test suite for Flask Network Graph Visualization
Tests data loading, graph generation, Flask routes, and deployment readiness
"""

import sys
import json
import os
from pathlib import Path

def print_test(test_name, status, message=""):
    """Print test result with color"""
    symbol = "✓" if status else "✗"
    status_text = "PASS" if status else "FAIL"
    print(f"{symbol} {test_name}: {status_text} {message}")
    return status

def test_data_files():
    """Test that all required data files exist and are valid JSON"""
    print("\n=== Testing Data Files ===")
    
    tests_passed = True
    
    # Check nodes.json
    nodes_path = Path("data/nodes.json")
    if nodes_path.exists():
        try:
            with open(nodes_path, 'r') as f:
                nodes = json.load(f)
            tests_passed &= print_test("nodes.json exists and valid", True, f"({len(nodes)} nodes)")
            tests_passed &= print_test("nodes.json has data", len(nodes) > 0)
        except json.JSONDecodeError as e:
            tests_passed &= print_test("nodes.json valid JSON", False, str(e))
    else:
        tests_passed &= print_test("nodes.json exists", False)
    
    # Check edges.json
    edges_path = Path("data/edges.json")
    if edges_path.exists():
        try:
            with open(edges_path, 'r') as f:
                edges = json.load(f)
            tests_passed &= print_test("edges.json exists and valid", True, f"({len(edges)} edges)")
            tests_passed &= print_test("edges.json has data", len(edges) > 0)
        except json.JSONDecodeError as e:
            tests_passed &= print_test("edges.json valid JSON", False, str(e))
    else:
        tests_passed &= print_test("edges.json exists", False)
    
    # Check config
    config_path = Path("config/graph_config.json")
    if config_path.exists():
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            tests_passed &= print_test("graph_config.json exists and valid", True)
        except json.JSONDecodeError as e:
            tests_passed &= print_test("graph_config.json valid JSON", False, str(e))
    else:
        tests_passed &= print_test("graph_config.json exists", False)
    
    return tests_passed

def test_imports():
    """Test that all required packages can be imported"""
    print("\n=== Testing Package Imports ===")
    
    tests_passed = True
    
    try:
        import flask
        tests_passed &= print_test("Flask import", True, f"v{flask.__version__}")
    except ImportError as e:
        tests_passed &= print_test("Flask import", False, str(e))
    
    try:
        import networkx
        try:
            version = networkx.__version__
        except AttributeError:
            import importlib.metadata
            version = importlib.metadata.version('networkx')
        tests_passed &= print_test("NetworkX import", True, f"v{version}")
    except ImportError as e:
        tests_passed &= print_test("NetworkX import", False, str(e))
    
    try:
        import gravis
        tests_passed &= print_test("Gravis import", True, f"v{gravis.__version__}")
    except ImportError as e:
        tests_passed &= print_test("Gravis import", False, str(e))
    
    try:
        import gunicorn
        tests_passed &= print_test("Gunicorn import", True)
    except ImportError as e:
        tests_passed &= print_test("Gunicorn import", False, str(e))
    
    return tests_passed

def test_main_app():
    """Test that main.py can be imported and has required components"""
    print("\n=== Testing Main Application ===")
    
    tests_passed = True
    
    try:
        import main
        tests_passed &= print_test("main.py imports", True)
        
        # Check for Flask app
        if hasattr(main, 'app'):
            tests_passed &= print_test("Flask app exists", True)
        else:
            tests_passed &= print_test("Flask app exists", False)
        
        # Check for required functions
        required_functions = [
            'load_nodes',
            'load_edges',
            'load_config',
            'generate_map_v2'
        ]
        
        for func_name in required_functions:
            if hasattr(main, func_name):
                tests_passed &= print_test(f"Function '{func_name}' exists", True)
            else:
                tests_passed &= print_test(f"Function '{func_name}' exists", False)
        
    except ImportError as e:
        tests_passed &= print_test("main.py imports", False, str(e))
    except Exception as e:
        tests_passed &= print_test("main.py loads", False, str(e))
    
    return tests_passed

def test_flask_app():
    """Test Flask app routes and configuration"""
    print("\n=== Testing Flask Application ===")
    
    tests_passed = True
    
    try:
        import main
        app = main.app
        
        # Test app configuration
        tests_passed &= print_test("Flask app created", app is not None)
        
        # Test client
        with app.test_client() as client:
            # Test index route
            response = client.get('/')
            tests_passed &= print_test("Index route responds", response.status_code == 200)
            tests_passed &= print_test("Index returns HTML", b'html' in response.data.lower())
            tests_passed &= print_test("Explorer is home page", b'Decode Explorer' in response.data)
            tests_passed &= print_test("Explorer has X post panel", b'id="post-view"' in response.data)
            tests_passed &= print_test("Explorer has post navigator", b'id="post-nav"' in response.data)
            tests_passed &= print_test("Explorer has insight overlay", b'id="insight-overlay"' in response.data)
            tests_passed &= print_test("Explorer has hub list", b'id="hub-list"' in response.data)
            tests_passed &= print_test("Explorer has mobile tabs", b'id="mobile-tabs"' in response.data)

            catalog = client.get('/api/catalog')
            tests_passed &= print_test("Catalog API responds", catalog.status_code == 200)
            payload = catalog.get_json() or {}
            tests_passed &= print_test("Catalog includes decodes", bool(payload.get('decodes')))
            
    except Exception as e:
        tests_passed &= print_test("Flask app test", False, str(e))
    
    return tests_passed

def test_deployment_files():
    """Test that all deployment files exist"""
    print("\n=== Testing Deployment Files ===")
    
    tests_passed = True
    
    required_files = {
        'requirements.txt': 'Python dependencies',
        'Procfile': 'Deployment config',
        '.replit': 'Replit config',
        'main.py': 'Main application'
    }
    
    for filename, description in required_files.items():
        file_path = Path(filename)
        if file_path.exists():
            tests_passed &= print_test(f"{filename} exists", True, f"({description})")
        else:
            tests_passed &= print_test(f"{filename} exists", False, f"Missing {description}")
    
    return tests_passed

def test_requirements():
    """Test requirements.txt has all necessary packages"""
    print("\n=== Testing Requirements ===")
    
    tests_passed = True
    
    try:
        with open('requirements.txt', 'r') as f:
            requirements = f.read().lower()
        
        required_packages = ['flask', 'networkx', 'gravis', 'gunicorn']
        
        for package in required_packages:
            if package in requirements:
                tests_passed &= print_test(f"'{package}' in requirements.txt", True)
            else:
                tests_passed &= print_test(f"'{package}' in requirements.txt", False)
        
    except FileNotFoundError:
        tests_passed &= print_test("requirements.txt exists", False)
    
    return tests_passed

def test_data_integrity():
    """Test that edges reference valid nodes"""
    print("\n=== Testing Data Integrity ===")
    
    tests_passed = True
    
    try:
        with open('data/nodes.json', 'r') as f:
            nodes = json.load(f)
        with open('data/edges.json', 'r') as f:
            edges = json.load(f)
        
        # Get all node names
        node_names = set()
        for node in nodes:
            if 'graphicName' in node:
                node_names.add(node['graphicName'])
        
        # Check if all edges reference valid nodes
        invalid_edges = []
        for i, edge in enumerate(edges):
            source = edge.get('source')
            target = edge.get('target')
            
            if source not in node_names:
                invalid_edges.append(f"Edge {i}: source '{source}' not found")
            if target not in node_names:
                invalid_edges.append(f"Edge {i}: target '{target}' not found")
        
        if invalid_edges:
            tests_passed &= print_test("All edges reference valid nodes", False)
            for err in invalid_edges[:5]:  # Show first 5 errors
                print(f"  - {err}")
        else:
            tests_passed &= print_test("All edges reference valid nodes", True)
        
    except Exception as e:
        tests_passed &= print_test("Data integrity check", False, str(e))
    
    return tests_passed

def main():
    """Run all tests"""
    print("=" * 50)
    print("  Flask Network Graph - Build Verification Tests")
    print("=" * 50)
    
    all_passed = True
    
    # Run all test suites
    all_passed &= test_imports()
    all_passed &= test_data_files()
    all_passed &= test_deployment_files()
    all_passed &= test_requirements()
    all_passed &= test_main_app()
    all_passed &= test_data_integrity()
    all_passed &= test_flask_app()
    
    # Summary
    print("\n" + "=" * 50)
    if all_passed:
        print("  ✓ ALL TESTS PASSED - BUILD READY FOR DEPLOYMENT")
        print("=" * 50)
        return 0
    else:
        print("  ✗ SOME TESTS FAILED - CHECK ERRORS ABOVE")
        print("=" * 50)
        return 1

if __name__ == "__main__":
    sys.exit(main())
