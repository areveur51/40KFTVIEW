#!/usr/bin/env python3
"""
Deployment Verification Script
Ensures the app is production-ready for Replit deployment
"""

import subprocess
import sys
import os

def run_command(cmd, description):
    """Run a command and return success status"""
    print(f"\n🔍 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print(f"✓ {description}: SUCCESS")
            if result.stdout.strip():
                print(f"  Output: {result.stdout.strip()[:200]}")
            return True
        else:
            print(f"✗ {description}: FAILED")
            if result.stderr:
                print(f"  Error: {result.stderr.strip()[:200]}")
            return False
    except subprocess.TimeoutExpired:
        print(f"✗ {description}: TIMEOUT")
        return False
    except Exception as e:
        print(f"✗ {description}: ERROR - {e}")
        return False

def main():
    print("=" * 60)
    print("  DEPLOYMENT VERIFICATION - Production Readiness Check")
    print("=" * 60)
    
    all_checks_passed = True
    
    # 1. Test imports and dependencies
    print("\n📦 CHECKING DEPENDENCIES...")
    all_checks_passed &= run_command(
        "python -c 'import flask, networkx, gravis, gunicorn; print(\"All imports successful\")'",
        "Import all required packages"
    )
    
    # 2. Test data files
    print("\n📂 CHECKING DATA FILES...")
    all_checks_passed &= run_command(
        "python -c 'import json; nodes=json.load(open(\"data/nodes.json\")); print(f\"{len(nodes)} nodes loaded\")'",
        "Load nodes.json"
    )
    all_checks_passed &= run_command(
        "python -c 'import json; edges=json.load(open(\"data/edges.json\")); print(f\"{len(edges)} edges loaded\")'",
        "Load edges.json"
    )
    
    # 3. Test main app
    print("\n🐍 CHECKING MAIN APPLICATION...")
    all_checks_passed &= run_command(
        "python -c 'import main; print(\"main.py imports successfully\")'",
        "Import main.py"
    )
    
    # 4. Run comprehensive tests
    print("\n🧪 RUNNING COMPREHENSIVE TESTS...")
    all_checks_passed &= run_command(
        "python test_app.py",
        "Run full test suite"
    )
    
    # 5. Test Gunicorn can start
    print("\n🚀 CHECKING GUNICORN CONFIGURATION...")
    all_checks_passed &= run_command(
        "gunicorn --check-config main:app",
        "Validate Gunicorn config"
    )
    
    # 6. Check deployment files
    print("\n📋 CHECKING DEPLOYMENT FILES...")
    required_files = [
        "main.py",
        "requirements.txt",
        "Procfile",
        ".replit",
        "data/nodes.json",
        "data/edges.json",
        "config/graph_config.json"
    ]
    
    for file in required_files:
        if os.path.exists(file):
            print(f"✓ {file}: EXISTS")
        else:
            print(f"✗ {file}: MISSING")
            all_checks_passed = False
    
    # Summary
    print("\n" + "=" * 60)
    if all_checks_passed:
        print("  ✅ DEPLOYMENT VERIFICATION PASSED")
        print("  Your app is ready for production deployment!")
        print("=" * 60)
        print("\n📌 NEXT STEPS:")
        print("  1. Click the 'Deploy' button in Replit")
        print("  2. Your app will deploy with Gunicorn on autoscale")
        print("  3. You'll receive a public URL for your network graph")
        return 0
    else:
        print("  ❌ DEPLOYMENT VERIFICATION FAILED")
        print("  Please fix the errors above before deploying")
        print("=" * 60)
        return 1

if __name__ == "__main__":
    sys.exit(main())
