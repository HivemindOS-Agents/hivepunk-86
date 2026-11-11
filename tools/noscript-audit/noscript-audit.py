#!/usr/bin/env python3
"""SUPERSEDED - kept only as a marker. This shim no longer delegates.

This name was a one-line shim that called noscript_audit.main(). Both halves of
that earlier draft are superseded by the artifact in this folder. The tool of
record is nostrip_audit.py:

    python3 nostrip_audit.py path/to/page.html

The old shim had its own exit codes (1 for a usage error), so it is deliberately
not left silently delegating to the new tool: anything still calling this name
gets the notice below on stderr and exit 2. Self-test: self_test.py, which does
not import or run this file.
"""

import sys

NOTICE = "noscript-audit.py is superseded. Use: python3 nostrip_audit.py <file.html>"


def main():
    sys.stderr.write(NOTICE + "\n")
    return 2


if __name__ == "__main__":
    sys.exit(main())
