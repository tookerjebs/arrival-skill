"""
Runtime hook for PyInstaller to fix common import issues.
This file will be included in the PyInstaller bundle and executed before the application starts.
"""

import os
import sys
import importlib.util
import importlib.machinery

# Print diagnostic information to help debug import issues
print("Python version:", sys.version)
print("Executable path:", sys.executable)

# Fix for the "Failed to execute script" error
if hasattr(sys, '_MEIPASS'):
    print("Running from PyInstaller bundle:", sys._MEIPASS)
    
    # Add the PyInstaller bundle directory to sys.path
    if sys._MEIPASS not in sys.path:
        sys.path.insert(0, sys._MEIPASS)
    
    # Add the _internal directory to sys.path
    internal_dir = os.path.join(sys._MEIPASS, '_internal')
    if os.path.isdir(internal_dir) and internal_dir not in sys.path:
        sys.path.insert(0, internal_dir)

# Fix for "No module named 'requests'" error
try:
    import requests
    print("Successfully imported requests module")
except ImportError as e:
    print(f"Error importing requests: {e}")
    
    # Try to find requests module in the bundle
    if hasattr(sys, '_MEIPASS'):
        requests_path = os.path.join(sys._MEIPASS, 'requests')
        if os.path.isdir(requests_path):
            print(f"Found requests at {requests_path}")
            if requests_path not in sys.path:
                sys.path.insert(0, requests_path)
        else:
            print(f"requests directory not found at {requests_path}")

# Fix for NumPy import issues
try:
    import numpy
    print("Successfully imported numpy module")
except ImportError as e:
    print(f"Error importing numpy: {e}")
    
    # Try to find numpy module in the bundle
    if hasattr(sys, '_MEIPASS'):
        numpy_path = os.path.join(sys._MEIPASS, 'numpy')
        if os.path.isdir(numpy_path):
            print(f"Found numpy at {numpy_path}")
            if numpy_path not in sys.path:
                sys.path.insert(0, numpy_path)
        else:
            print(f"numpy directory not found at {numpy_path}")

# Print the current sys.path to help with debugging
print("\nCurrent sys.path:")
for path in sys.path:
    print(f"  {path}")
