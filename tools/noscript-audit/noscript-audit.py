#!/usr/bin/env python3
"""Thin CLI shim: delegate to noscript_audit.main() so the two cannot drift."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from noscript_audit import main  # noqa: E402

if __name__ == "__main__":
    sys.exit(main(sys.argv))
