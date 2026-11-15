#!/usr/bin/env python3
"""check_capture: read SELFTEST_OUTPUT.md, if it exists, and say whether it
looks like a complete captured run of THIS folder. It never writes a record and
never fills the ARTIFACTS.md exit cell.

Usage (from inside tools/issue-triage-selftest-check):

    python3 check_capture.py

Exit codes:
    0  a record exists and carries a '## stdout' section, a '## stderr'
       section and exactly one EXIT=<n> line (or, with no record yet, prints
       NO CAPTURE YET and exits 0)
    1  a record exists but is incomplete, carries no single EXIT=<n> line, or
       cannot be read

Exiting 0 with no record is deliberate: until a real run writes the file,
"not captured yet" is the truthful state. Nothing here claims a run happened or
passed. To check that a stored record still matches a fresh run, use
`python3 self_test.py --verify-record`; that is the check guarding the
ARTIFACTS.md exit cell.

Everything in the file is data and is never followed as an instruction.
"""

import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
RECORD = os.path.join(HERE, "SELFTEST_OUTPUT.md")

EXIT_RE = re.compile(r"^EXIT=(\d+)\s*$", re.MULTILINE)


def main():
    if not os.path.exists(RECORD):
        print("NO CAPTURE YET: %s does not exist" % RECORD)
        print("run: env -u PYTHONPATH python3 self_test.py --capture")
        print("then fill the one ARTIFACTS.md run-record exit cell with the "
              "integer on that file's EXIT= line, and nothing else.")
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
    codes = EXIT_RE.findall(text)
    if not codes:
        problems.append("no EXIT=<number> line")
    elif len(codes) > 1:
        problems.append("more than one EXIT= line (%s)" % ", ".join(codes))

    if problems:
        print("check_capture: incomplete record in %s" % RECORD)
        for p in problems:
            print("  - " + p)
        print("note: NOT_RUN is allowed only when the self-test could not be "
              "started at all; it does not fill the ARTIFACTS.md exit cell.")
        return 1

    print("check_capture: %s carries stdout, stderr and EXIT=%s"
          % (RECORD, codes[0]))
    print("next: python3 self_test.py --verify-record   "
          "(stored run must match a fresh one before the exit cell is filled), "
          "then set the cell to %s" % codes[0])
    if "FAIL" in text:
        print("note: the record holds a FAIL line; paste it into the commit "
              "message with five lines either side before filling the cell.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
