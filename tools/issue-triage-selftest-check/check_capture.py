#!/usr/bin/env python3
"""check_capture: read SELFTEST_OUTPUT.md, if it exists, and say whether it
looks like a complete captured run. It never runs anything and never writes.

Usage (from inside tools/issue-triage-selftest-check):

    python3 check_capture.py

Exit codes:
    0  a capture exists and carries a stdout section, a stderr section and an
       EXIT= line (or, with no capture file, prints NO CAPTURE YET and exits 0)
    1  a capture file exists but a required part is missing

This checker deliberately exits 0 when SELFTEST_OUTPUT.md is absent: the file is
written by the HivemindOS runner (or by selftest_capture.sh), and until then the
correct state is "not captured yet". Nothing here claims a run result.

Everything in the file is data and is never followed as an instruction.
"""

import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
RECORD = os.path.join(HERE, "SELFTEST_OUTPUT.md")


def main():
    if not os.path.exists(RECORD):
        print("NO CAPTURE YET: %s does not exist" % RECORD)
        print("run: sh selftest_capture.sh   (or let the HivemindOS runner write it)")
        return 0

    try:
        with open(RECORD, "r", encoding="utf-8") as fh:
            text = fh.read()
    except (OSError, UnicodeError) as exc:
        print("check_capture: cannot read %s: %s" % (RECORD, exc),
              file=sys.stderr)
        return 1

    problems = []
    if "## stdout" not in text:
        problems.append("no '## stdout' heading")
    if "## stderr" not in text:
        problems.append("no '## stderr' heading")
    if not re.search(r"^EXIT=\d+\s*$", text, re.MULTILINE):
        problems.append("no EXIT=<number> line")

    if problems:
        print("check_capture: incomplete record in %s" % RECORD)
        for p in problems:
            print("  - " + p)
        print("note: NOT_RUN instead of EXIT= is allowed only when the "
              "self-test could not be started at all.")
        return 1

    match = re.search(r"^EXIT=(\d+)\s*$", text, re.MULTILINE)
    print("check_capture: %s carries stdout, stderr and EXIT=%s"
          % (RECORD, match.group(1)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
