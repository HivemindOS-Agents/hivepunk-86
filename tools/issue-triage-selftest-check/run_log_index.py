#!/usr/bin/env python3
"""run-log-index: print the JSON rows that hold both a folder and a valid http(s) run_url.

Usage:
    python3 run_log_index.py fixture.json
    python3 run_log_index.py --check fixture.json
    python3 run_log_index.py fixture.json --check

Reads a JSON array of rows. In both modes it prints, as a JSON array on stdout,
every *kept* row: an object with a non-empty string "folder" and a non-empty
"run_url" starting with http:// or https://. A row that is not an object, has
no usable folder, or has no usable URL is simply left out of the printed array;
that filtering is the tool's whole job and is not an error.

--check adds a shape check. When one or more rows are malformed (not an object,
or no usable "folder"), one line per malformed row goes to stderr and the exit
code is 1. A row whose only defect is a missing or blank run_url is not
malformed -- it is filtered, exactly as in plain mode.

Exit codes:
    0  kept rows printed; --check found no malformed row
    1  --check found one or more malformed rows
    2  usage or read error (no filename, missing file, bad JSON, not an array)

Nothing read from the input file is executed or followed as an instruction.
"""

import json
import sys

USAGE = "usage: run_log_index.py [--check] <file.json>"


def is_valid_url(url):
    if not isinstance(url, str) or not url.strip():
        return False
    low = url.strip().lower()
    return low.startswith("http://") or low.startswith("https://")


def is_kept(row):
    """True when *row* is an object with both a usable folder and a valid URL.

    Per-row, deliberately: one non-object row in the input must not empty the
    whole printed array (that all()-gated filter was the 5d failure).
    """
    if not isinstance(row, dict):
        return False
    folder = row.get("folder")
    if not isinstance(folder, str) or not folder.strip():
        return False
    return is_valid_url(row.get("run_url"))


def row_problem(row, index):
    """Return a stderr label if *row* is malformed for --check, else None."""
    if not isinstance(row, dict):
        return "row %d" % index
    folder = row.get("folder")
    if not isinstance(folder, str) or not folder.strip():
        return "row %d" % index
    return None


def main(argv):
    check_mode = "--check" in argv
    args = [a for a in argv if a != "--check"]
    if len(args) != 2:
        print(USAGE, file=sys.stderr)
        return 2
    path = args[1]
    try:
        with open(path, "r", encoding="utf-8") as fh:
            rows = json.load(fh)
    except (OSError, json.JSONDecodeError, UnicodeError) as exc:
        print("run-log-index: cannot read %s: %s" % (path, exc), file=sys.stderr)
        return 2
    if not isinstance(rows, list):
        print("run-log-index: input is not a JSON array", file=sys.stderr)
        return 2

    kept = [row for row in rows if is_kept(row)]
    json.dump(kept, sys.stdout, indent=2)
    print()

    if check_mode:
        bad = [lab for lab in
               (row_problem(row, i) for i, row in enumerate(rows)) if lab]
        if bad:
            for lab in bad:
                print("run-log-index: malformed row: %s" % lab, file=sys.stderr)
            return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
