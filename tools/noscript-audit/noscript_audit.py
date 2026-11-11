#!/usr/bin/env python3
"""SUPERSEDED - kept only as a marker. No audit logic lives in this file.

This name held an earlier, differently shaped draft of the noscript-audit tool
(script counts, inline handlers, elements hidden until a script runs, empty
script mount points, regex-based). The tool of record in this folder is
nostrip_audit.py:

    python3 nostrip_audit.py path/to/page.html

Documentation: README.md. Self-test: self_test.py, which does not import or run
this file. The real output of a self-test run is written by HivemindOS into
SELFTEST_OUTPUT.md after each commit; read the run state there.
"""

import sys

NOTICE = "noscript_audit.py is superseded. Use: python3 nostrip_audit.py <file.html>"


def main():
    sys.stderr.write(NOTICE + "\n")
    return 2


if __name__ == "__main__":
    sys.exit(main())
