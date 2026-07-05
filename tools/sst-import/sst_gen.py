#!/usr/bin/env python3
"""Convenience wrapper for sst_gen CLI.

When run as: python3 sst_gen.py <args>
This script sets up the path and delegates to __main__.
"""
import sys
import os

# Add the script's directory to sys.path so 'sst_gen' package is importable
_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

from sst_gen.__main__ import main

if __name__ == "__main__":
    main()
