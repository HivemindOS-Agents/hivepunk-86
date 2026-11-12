#!/usr/bin/env python3
"""Self-test for self-test-run-index. Stdlib only, no network.

Run from inside this folder:  python3 self_test.py
Exits 0 only when every check passes.
"""

import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TOOL = os.path.join(HERE, "self_test_run_index.py")
FIXTURE = os.path.join(HERE, "fixture.json")

EXPECTED_FILTERED = (
    "card-claims-check -> https://github.com/HivemindOS-Agents/bee-self-test/actions/runs/43160679788\n"
    "noscript-audit -> https://github.com/HivemindOS-Agents/bee-self-test/actions/runs/42957607945\n"
    "sample-run -> http://localhost/run/123\n"
)


def cli(*args):
    return subprocess.run([sys.executable, TOOL] + list(args),
                          capture_output=True, text=True)


def run():
    failures = []

    # 1. Normal mode: only 4 rows with http(s) URLs, no --check.
    out = cli(FIXTURE)
    if out.returncode != 0:
        failures.append("fixture: exit %d, expected 0" % out.returncode)
    if out.stdout != EXPECTED_FILTERED:
        failures.append("fixture stdout mismatch\nexpected:\n%s\ngot:\n%s"
                        % (EXPECTED_FILTERED, out.stdout))
    if out.stderr != "":
        failures.append("fixture stderr not empty: %r" % out.stderr)

    # 2. --check mode: exits 1 because 2 rows lack a URL (no-run, issue-triage).
    out = cli("--check", FIXTURE)
    if out.returncode != 1:
        failures.append("--check: exit %d, expected 1" % out.returncode)
    if "check failed" not in out.stderr:
        failures.append("--check stderr: %r" % out.stderr)
    # Should also print the filtered lines to stdout.
    if out.stdout != EXPECTED_FILTERED:
        failures.append("--check stdout mismatch\nexpected:\n%s\ngot:\n%s"
                        % (EXPECTED_FILTERED, out.stdout))

    # 3. --check on a fixture with all valid URLs: exits 0.
    # Build a tiny inline fixture via echo.
    fixture_all_valid = os.path.join(HERE, "_all_valid.tmp.json")
    try:
        with open(fixture_all_valid, "w") as fh:
            fh.write('[{"folder":"a","run_url":"https://example.com/run/1"},'
                     '{"folder":"b","run_url":"http://example.com/run/2"}]')
        out = cli("--check", fixture_all_valid)
        if out.returncode != 0:
            failures.append("--check all-valid: exit %d, expected 0" % out.returncode)
        expected_all = (
            "a -> https://example.com/run/1\n"
            "b -> http://example.com/run/2\n"
        )
        if out.stdout != expected_all:
            failures.append("--check all-valid stdout mismatch")
        if out.stderr != "":
            failures.append("--check all-valid stderr: %r" % out.stderr)
    finally:
        if os.path.exists(fixture_all_valid):
            os.remove(fixture_all_valid)

    # 4. No argument: usage message on stderr, exit 2.
    out = cli()
    if out.returncode != 2:
        failures.append("no argument: exit %d, expected 2" % out.returncode)
    if not out.stderr.startswith("usage:"):
        failures.append("no argument stderr: %r" % out.stderr)

    # 5. Missing file: message on stderr, exit 2.
    missing = os.path.join(HERE, "no-such-file.json")
    out = cli(missing)
    if out.returncode != 2:
        failures.append("missing file: exit %d, expected 2" % out.returncode)
    if "cannot read" not in out.stderr:
        failures.append("missing file stderr: %r" % out.stderr)

    # 6. --check with missing file: exit 2.
    out = cli("--check", missing)
    if out.returncode != 2:
        failures.append("--check missing file: exit %d, expected 2" % out.returncode)

    # 7. Empty array: no output, exit 0.
    empty_fixture = os.path.join(HERE, "_empty.tmp.json")
    try:
        with open(empty_fixture, "w") as fh:
            fh.write("[]")
        out = cli(empty_fixture)
        if out.returncode != 0:
            failures.append("empty array: exit %d, expected 0" % out.returncode)
        if out.stdout != "":
            failures.append("empty array stdout: %r" % out.stdout)
    finally:
        if os.path.exists(empty_fixture):
            os.remove(empty_fixture)

    # 8. Row with None run_url: should be filtered out.
    none_fixture = os.path.join(HERE, "_none_url.tmp.json")
    try:
        with open(none_fixture, "w") as fh:
            fh.write('[{"folder":"test","run_url":null}]')
        out = cli(none_fixture)
        if out.returncode != 0:
            failures.append("None run_url: exit %d, expected 0" % out.returncode)
        if out.stdout != "":
            failures.append("None run_url stdout: %r" % out.stdout)
        # --check should fail
        out = cli("--check", none_fixture)
        if out.returncode != 1:
            failures.append("None run_url --check: exit %d, expected 1" % out.returncode)
    finally:
        if os.path.exists(none_fixture):
            os.remove(none_fixture)

    # 9. Folder with missing run_url key: filtered out, --check fails.
    missing_key = os.path.join(HERE, "_missing_key.tmp.json")
    try:
        with open(missing_key, "w") as fh:
            fh.write('[{"folder":"test"}]')
        out = cli(missing_key)
        if out.returncode != 0:
            failures.append("missing key: exit %d, expected 0" % out.returncode)
        if out.stdout != "":
            failures.append("missing key stdout: %r" % out.stdout)
        out = cli("--check", missing_key)
        if out.returncode != 1:
            failures.append("missing key --check: exit %d, expected 1" % out.returncode)
    finally:
        if os.path.exists(missing_key):
            os.remove(missing_key)

    # 10. Non-array JSON: exit 2.
    bad_json = os.path.join(HERE, "_bad_json.tmp.json")
    try:
        with open(bad_json, "w") as fh:
            fh.write('{"not":"array"}')
        out = cli(bad_json)
        if out.returncode != 2:
            failures.append("non-array json: exit %d, expected 2" % out.returncode)
        if "not a JSON array" not in out.stderr:
            failures.append("non-array json stderr: %r" % out.stderr)
    finally:
        if os.path.exists(bad_json):
            os.remove(bad_json)

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
