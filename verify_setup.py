#!/usr/bin/env python3
"""
Verification script for data science problems repository.
This script checks that the repository structure is correct.
"""

import os
import sys
from pathlib import Path

def verify_structure():
    """Verify that all required directories and files exist."""
    
    print("Verifying repository structure...\n")
    
    # Required directories
    required_dirs = [
        "problems",
        "problems/data_cleaning",
        "problems/exploratory_analysis",
        "problems/machine_learning",
        "problems/visualization"
    ]
    
    # Required files
    required_files = [
        "README.md",
        "requirements.txt",
        "problems/data_cleaning/README.md",
        "problems/exploratory_analysis/README.md",
        "problems/machine_learning/README.md",
        "problems/visualization/README.md"
    ]
    
    all_ok = True
    
    # Check directories
    for dir_path in required_dirs:
        if os.path.isdir(dir_path):
            print(f"✓ Directory exists: {dir_path}")
        else:
            print(f"✗ Directory missing: {dir_path}")
            all_ok = False
    
    print()
    
    # Check files
    for file_path in required_files:
        if os.path.isfile(file_path):
            size = os.path.getsize(file_path)
            print(f"✓ File exists: {file_path} ({size} bytes)")
        else:
            print(f"✗ File missing: {file_path}")
            all_ok = False
    
    print()
    
    if all_ok:
        print("✓ All structure checks passed!")
        return 0
    else:
        print("✗ Some structure checks failed!")
        return 1

if __name__ == "__main__":
    sys.exit(verify_structure())
