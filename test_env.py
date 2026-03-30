#!/usr/bin/env python3

print("Python version:")
import sys
print(sys.version)

print("\nChecking installed packages:")
try:
    import pandas
    print("✓ pandas is installed")
except ImportError:
    print("✗ pandas is not installed")

try:
    import numpy
    print("✓ numpy is installed")
except ImportError:
    print("✗ numpy is not installed")

try:
    import matplotlib
    print("✓ matplotlib is installed")
except ImportError:
    print("✗ matplotlib is not installed")

try:
    import seaborn
    print("✓ seaborn is installed")
except ImportError:
    print("✗ seaborn is not installed")
