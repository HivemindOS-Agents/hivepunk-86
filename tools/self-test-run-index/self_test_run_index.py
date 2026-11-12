#!/usr/bin/env python3
"""self-test-run-index: filter JSON rows with non-empty http(s) run_url.

Usage:
    python3 self_test_run_index.py fixture.json
    python3 self_test_run_index.py --check fixture.json

Reads a JSON array of objects each having at least "folder" and "run_url" keys.
Without --check: prints one "folder -> run_url" line per row whose run_url is
  a non-empty string starting with http:// or https://.
With --check: exits 1 if any row has a blank or missing run_url (prints first
  such folder on stderr). Otherwise the same filtered output.

Exit codes:
    0  no check failures and output printed
    1  --check found one or more rows without a URL
    2  usage or parse error
"""

import json
import sys

USAGE = "usage: self_test_run_index.py [--check] <file.json>"


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

    try:
        with open(args[1], "r", encoding="utf-8") as fh:
            rows = json.load(fh)
    except (OSError, json.JSONDecodeError, UnicodeError) as exc:
        print("cannot read %s: %s" % (args[1], exc), file=sys.stderr)
        return 2

    if not isinstance(rows, list):
        print("input is not a JSON array", file=sys.stderr)
        return 2

    failures = []
    kept = []
    for i, row in enumerate(rows):
        folder = row.get("folder", "")
        run_url = row.get("run_url", None)
        if not is_valid_url(run_url):
            failures.append((i, folder, run_url))
        else:
            kept.append((folder, run_url))

    if check_mode and failures:
        i, folder, url = failures[0]
        folder_str = folder if folder else ("row %d" % i)
        print("check failed: %s has no run_url" % folder_str, file=sys.stderr)
        return 1

    for folder, run_url in kept:
        print("%s -> %s" % (folder, run_url))

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
