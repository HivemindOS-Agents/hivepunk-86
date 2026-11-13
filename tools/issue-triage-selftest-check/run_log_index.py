#!/usr/bin/env python3
"""run-log-index: filter JSON rows with non-empty http(s) run_url.

Usage:
    python3 run_log_index.py fixture.json
    python3 run_log_index.py --check fixture.json

Reads a JSON array of objects with "folder" and "run_url" keys.

Both modes print to stdout the JSON array of rows whose run_url is a
non-empty string starting with http:// or https://, followed by a newline.

With --check, the tool validates the *shape* of every row (each must be an
object carrying a non-empty-string "folder" key). It does not care whether a
row's run_url is absent -- rows without a URL are simply filtered out of the
stdout array, which is the tool's whole job, and are not errors. When one or
more rows are malformed (not an object, or no usable "folder"), --check prints
one line per malformed row on stderr and exits 1.

Exit codes:
    0  success (filtered rows printed; --check found no malformed row)
    1  --check found one or more malformed rows
    2  usage or read error (missing file, bad JSON, non-array)
"""

import json
import sys

USAGE = "usage: run_log_index.py [--check] <file.json>"


def is_valid_url(url):
    if not isinstance(url, str) or not url.strip():
        return False
    low = url.strip().lower()
    return low.startswith("http://") or low.startswith("https://")


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

    valid_rows = [row for row in rows if is_valid_url(row.get("run_url"))
                  ] if all(isinstance(r, dict) for r in rows) else []

    json.dump(valid_rows, sys.stdout, indent=2)
    print()

    if check_mode:
        bad = [row_problem(r, i) for i, r in enumerate(rows)]
        bad = [lab for lab in bad if lab]
        if bad:
            for lab in bad:
                print("run-log-index: malformed row: %s" % lab, file=sys.stderr)
            return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
