#!/usr/bin/env python3
"""
Deployment script to prepare the codebase for production.
This script will:
1. Install production dependencies
2. Replace Pydantic v1 files with Pydantic v2 compatible versions
"""

import os
import sys
import shutil
import subprocess


def main():
    print("Preparing codebase for production deployment...")
    
    # Install production dependencies
    print("Installing production dependencies...")
    subprocess.run(["pip", "install", "-r", "requirements-prod.txt"], check=True)
    
    # Replace Pydantic v1 files with v2 compatible versions
    print("Replacing Pydantic v1 files with v2 compatible versions...")
    
    # Replace models/order.py with models/order_v2.py
    if os.path.exists("models/order_v2.py"):
        shutil.copy("models/order_v2.py", "models/order.py")
        print("✅ Replaced models/order.py with v2 version")
    
    # Replace schemas/common.py with schemas/common_v2.py
    if os.path.exists("schemas/common_v2.py"):
        shutil.copy("schemas/common_v2.py", "schemas/common.py")
        print("✅ Replaced schemas/common.py with v2 version")
    
    # Replace schemas/order.py with schemas/order_v2.py
    if os.path.exists("schemas/order_v2.py"):
        shutil.copy("schemas/order_v2.py", "schemas/order.py")
        print("✅ Replaced schemas/order.py with v2 version")
    
    print("Deployment preparation complete!")
    return 0


if __name__ == "__main__":
    sys.exit(main()) 