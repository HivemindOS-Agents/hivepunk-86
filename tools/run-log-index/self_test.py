#!/usr/bin/env python3
"""Self-test for run-log-index. Stdlib only, no network.

Run from inside this folder:  python3 self_test.py
Exits 0 only when every check passes.
"""

import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
TOOL = os.path.join(HERE, "run_log_index.py")
FIXTURE = os.path.join(HERE, "fixture.json")

# Expected filtered output from fixture.json (3 valid rows)
EXPECTED_FILTERED = [
    {"folder": "valid1", "run_url": "https://example.com/run/1"},
    {"folder": "valid2", "run_url": "http://example.com/run/2"},
    {"folder": "also_valid", "run_url": "https://github.com/user/repo/actions/runs/12345"},
]
EXPECTED_JSON = json.dumps(EXPECTED_FILTERED, indent=2) + "\n"


def cli(*args):
    return subprocess.run([sys.executable, TOOL] + list(args),
                          capture_output=True, text=True)


def run():
    failures = []

    # 1. Normal mode: only 3 rows with http(s) URLs.
    out = cli(FIXTURE)
    if out.returncode != 0:
        failures.append("fixture: exit %d, expected 0" % out.returncode)
    if out.stdout != EXPECTED_JSON:
        failures.append("fixture stdout mismatch")
    if out.stderr != "":
        failures.append("fixture stderr not empty: %r" % out.stderr)

    # 2. --check mode: exits 1 because 3 rows lack a valid URL.
    out = cli("--check", FIXTURE)
    if out.returncode != 1:
        failures.append("--check: exit %d, expected 1" % out.returncode)
    expected_stderr = (
        "run-log-index: missing run_url: empty\n"
        "run-log-index: missing run_url: whitespace\n"
        "run-log-index: missing run_url: no_url\n"
    )
    if out.stderr != expected_stderr:
        failures.append("--check stderr: %r" % out.stderr)
    if out.stdout != EXPECTED_JSON:
        failures.append("--check stdout mismatch")

    # 3. --check on a fixture with all valid URLs: exits 0.
    all_valid = [
        {"folder": "a", "run_url": "https://example.com/run/1"},
        {"folder": "b", "run_url": "http://example.com/run/2"},
    ]
    all_valid_json = json.dumps(all_valid, indent=2) + "\n"
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as fh:
        temp_path = fh.name
        json.dump(all_valid, fh)
    try:
        out = cli("--check", temp_path)
        if out.returncode != 0:
            failures.append("--check all-valid: exit %d, expected 0" % out.returncode)
        if out.stdout != all_valid_json:
            failures.append("--check all-valid stdout mismatch")
        if out.stderr != "":
            failures.append("--check all-valid stderr: %r" % out.stderr)
    finally:
        os.remove(temp_path)

    # 4. No argument: usage message on stderr, exit 2.
    out = cli()
    if out.returncode != 2:
        failures.append("no argument: exit %d, expected 2" % out.returncode)
    if not out.stderr.startswith("usage:"):
        failures.append("no argument stderr: %r" % out.stderr)

    # 5. Missing file: message on stderr, exit 2.
    missing_path = os.path.join(HERE, "no-such-file.json")
    out = cli(missing_path)
    if out.returncode != 2:
        failures.append("missing file: exit %d, expected 2" % out.returncode)
    if "cannot read" not in out.stderr:
        failures.append("missing file stderr: %r" % out.stderr)

    # 6. --check with missing file: exit 2.
    out = cli("--check", missing_path)
    if out.returncode != 2:
        failures.append("--check missing file: exit %d, expected 2" % out.returncode)

    # 7. Empty array: no output, exit 0.
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as fh:
        temp_empty = fh.name
        json.dump([], fh)
    try:
        out = cli(temp_empty)
        if out.returncode != 0:
            failures.append("empty array: exit %d, expected 0" % out.returncode)
        if out.stdout.strip() != "[]":
            failures.append("empty array stdout: %r" % out.stdout)
    finally:
        os.remove(temp_empty)

    # 8. Row with None run_url: filtered out, --check fails.
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as fh:
        temp_none = fh.name
        json.dump([{"folder": "test", "run_url": None}], fh)
    try:
        out = cli(temp_none)
        if out.returncode != 0:
            failures.append("None run_url: exit %d" % out.returncode)
        if out.stdout.strip() != "[]":
            failures.append("None run_url stdout: %r" % out.stdout)
        out = cli("--check", temp_none)
        if out.returncode != 1:
            failures.append("None run_url --check: exit %d" % out.returncode)
        if "test" not in out.stderr:
            failures.append("None run_url --check stderr: %r" % out.stderr)
    finally:
        os.remove(temp_none)

    # 9. Row with missing run_url key: filtered out, --check fails.
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as fh:
        temp_missing_key = fh.name
        json.dump([{"folder": "test2"}], fh)
    try:
        out = cli(temp_missing_key)
        if out.returncode != 0:
            failures.append("missing key: exit %d" % out.returncode)
        if out.stdout.strip() != "[]":
            failures.append("missing key stdout: %r" % out.stdout)
        out = cli("--check", temp_missing_key)
        if out.returncode != 1:
            failures.append("missing key --check: exit %d" % out.returncode)
        if "test2" not in out.stderr:
            failures.append("missing key --check stderr: %r" % out.stderr)
    finally:
        os.remove(temp_missing_key)

    # 10. Non-array JSON: exit 2.
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as fh:
        temp_bad = fh.name
        fh.write('{"not": "array"}')
    try:
        out = cli(temp_bad)
        if out.returncode != 2:
            failures.append("non-array json: exit %d" % out.returncode)
        if "not a JSON array" not in out.stderr:
            failures.append("non-array json stderr: %r" % out.stderr)
    finally:
        os.remove(temp_bad)

    return failures


if __name__ == "__main__":
    problems = run()
    if problems:
        print("FAILED checks:", file=sys.stderr)
        for p in problems:
            print("  - " + p, file=sys.stderr)
        sys.exit(1)
    print("all checks passed")
    sys.exit(0)
