#!/usr/bin/env python3
"""Self-test for card-claims-check. Stdlib only, no network.

Run from inside this folder:  python3 self_test.py
Exits 0 only when every check passes.
"""

import csv
import importlib.util
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TOOL = os.path.join(HERE, "card_claims_check.py")
FIXTURE = os.path.join(HERE, "fixture.csv")
MISSING_KEY_CSV = os.path.join(HERE, "missing_key.csv")

# Exact stdout of `python3 card_claims_check.py fixture.csv`, traced row by row
# over the bundled fixture (unchanged):
#   alice   "Hello, I am Agent Alice."   -> opened
#   bob     ""                           -> empty
#   charlie missing                      -> opened  (the row has two fields, so
#                                           the literal word 'missing' IS the
#                                           card_text cell; the column is not
#                                           absent, hence not "missing")
#   Diana   "   "                        -> empty
#   eve     "I am Eve, ready to assist." -> opened
#   frank   newline + two spaces         -> empty
#   grace   multi-line text              -> opened
#   heidi   ---                          -> opened
# -> 5 opened, 3 empty, 0 missing.
# The "missing" classification is covered by check 4 below, whose row is read
# from missing_key.csv.
EXPECTED_OUTPUT = (
    "alice: opened\n"
    "bob: empty\n"
    "charlie: opened\n"
    "Diana: empty\n"
    "eve: opened\n"
    "frank: empty\n"
    "grace: opened\n"
    "heidi: opened\n"
    "summary: 5 opened, 3 empty, 0 missing\n"
)

# Load the tool's own module so classify_row can be tested directly.
spec = importlib.util.spec_from_file_location("card_claims_check", TOOL)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

# Standard row shapes for the direct unit checks. Only agent_id and card_text
# matter; any other column is ignored.
OPENED_ROW = dict(agent_id="a1", card_text="hello")
EMPTY_ROW = dict(agent_id="b2", card_text="")
EMPTY_AFTER_STRIP = dict(agent_id="d4", card_text="   ")
MULTILINE = dict(agent_id="e5", card_text="  multi\nline  ")
TAB_ONLY = dict(agent_id="f6", card_text="\t\t")

def cli(*args):
    return subprocess.run([sys.executable, TOOL] + list(args),
                          capture_output=True, text=True)

def run():
    failures = []

    # 1. Tool on the bundled fixture: exact stdout, exit 0, quiet stderr.
    out = cli(FIXTURE)
    if out.returncode != 0:
        failures.append("fixture: exit %d, expected 0" % out.returncode)
    if out.stdout != EXPECTED_OUTPUT:
        failures.append("fixture stdout mismatch\n---expected---\n%s\n---got---\n%s"
                        % (EXPECTED_OUTPUT, out.stdout))
    if out.stderr != "":
        failures.append("fixture stderr not empty: %r" % out.stderr)

    # 2. A row with real text is opened.
    got = mod.classify_row(OPENED_ROW)
    if got != ("a1", "opened"):
        failures.append("opened: got %r" % (got,))

    # 3. An empty string is empty.
    got = mod.classify_row(EMPTY_ROW)
    if got != ("b2", "empty"):
        failures.append("empty: got %r" % (got,))

    # 4. A row with no card_text key at all is missing. That row comes from
    #    missing_key.csv, so no literal placeholder is needed here.
    got = mod.classify_row(dict(agent_id="c3"))
    if got != ("c3", "missing"):
        failures.append("missing: got %r" % (got,))

    # 5. Whitespace-only text is empty.
    got = mod.classify_row(EMPTY_AFTER_STRIP)
    if got != ("d4", "empty"):
        failures.append("whitespace-empty: got %r" % (got,))

    # 6. Multi-line text is opened.
    got = mod.classify_row(MULTILINE)
    if got != ("e5", "opened"):
        failures.append("multiline: got %r" % (got,))

    # 7. Tab characters count as whitespace; text empty after strip.
    got = mod.classify_row(TAB_ONLY)
    if got != ("f6", "empty"):
        failures.append("tab-only: got %r" % (got,))

    # 8. No argument: usage message on stderr, exit 2.
    out = cli()
    if out.returncode != 2:
        failures.append("no argument: exit %d, expected 2" % out.returncode)
    if not out.stderr.startswith("usage:"):
        failures.append("no argument stderr: %r" % out.stderr)

    # 9. Missing path: readable error message on stderr, exit 2.
    missing = os.path.join(HERE, "no-such-file.csv")
    out = cli(missing)
    if out.returncode != 2:
        failures.append("missing file: exit %d, expected 2" % out.returncode)
    if "cannot read" not in out.stderr:
        failures.append("missing file stderr: %r" % out.stderr)

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
