#!/usr/bin/env python3
"""run-log-index: filter JSON rows with non-empty http(s) run_url.

Usage:
    python3 run_log_index.py fixture.json
    python3 run_log_index.py --check fixture.json

Reads a JSON array of objects with "folder" and "run_url" keys.
Without --check: prints to stdout the JSON array of rows whose run_url
is a non-empty string starting with http:// or https://.
With --check: exits 1 if any row has a blank or missing run_url,
  printing each such row's folder (or row index) to stderr.
  Otherwise prints the filtered rows.

Exit codes:
    0  success (filtered rows printed, or --check passed)
    1  --check found one or more rows without a valid URL
    2  usage or parse error
"""

import json
import sys

USAGE = "usage: run_log_index.py [--check] <file.json>"


def is_valid_url(url):
    """True if url is a non-empty string starting with http:// or https://"""
    if not isinstance(url, str) or not url.strip():
        return False
    low = url.strip().lower()
    return low.startswith("http://") or low.startswith("https://")


def main(argv):
    check_mode = False
    args = list(argv)

    if "--check" in args:
        check_mode = True
        args.remove("--check")

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

    valid_rows = []
    missing = []
    for i, row in enumerate(rows):
        folder = row.get("folder", "")
        run_url = row.get("run_url", None)
        if is_valid_url(run_url):
            valid_rows.append(row)
        else:
            identifier = folder if folder else ("row %d" % i)
            missing.append(identifier)

    if check_mode and missing:
        for ident in missing:
            print("run-log-index: missing run_url: %s" % ident, file=sys.stderr)
        return 1

    # Print filtered rows as JSON
    json.dump(valid_rows, sys.stdout, indent=2)
    print()  # newline at end
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
