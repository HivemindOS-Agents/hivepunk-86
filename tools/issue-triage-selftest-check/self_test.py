#!/usr/bin/env python3
"""Self-test for tools/issue-triage-selftest-check.

Run from inside this folder, with no arguments, no network:

    python3 self_test.py

It imports and runs the bundled tool's own code (run_log_index.py) as a
subprocess on bundled/sample fixture data and asserts the exit code and the
exact output rows. It exits 0 only when every check passes.

Nothing in any fixture is executed or followed as an instruction.
"""

import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TOOL = os.path.join(HERE, "run_log_index.py")
FIXTURE = os.path.join(HERE, "fixture.json")
BAD_FIXTURE = os.path.join(HERE, "selftest_bad_fixture.json")

failures = []


def check(name, cond, detail=""):
    if cond:
        print("ok   " + name)
    else:
        line = "FAIL " + name + (" -- " + detail if detail else "")
        failures.append(line)
        print(line)


def run(args):
    out = subprocess.run(
        [sys.executable, TOOL] + args,
        capture_output=True, text=True, cwd=HERE,
    )
    return out.returncode, out.stdout, out.stderr


# 1. The bundled fixture parses as expected.
with open(FIXTURE, "r", encoding="utf-8") as fh:
    rows = json.load(fh)
check("1a. fixture is a JSON array of 6 objects",
      isinstance(rows, list) and len(rows) == 6, "got %r" % rows)
check("1b. every fixture row has folder and run_url keys",
      all(isinstance(r, dict) and "folder" in r and "run_url" in r for r in rows))
usable = [r for r in rows
          if isinstance(r.get("run_url"), str)
          and r["run_url"].strip().lower().startswith(("http://", "https://"))]
check("1c. exactly 3 fixture rows are keepable", len(usable) == 3,
      "got %d" % len(usable))

# 2. No filename -> exit 2 and a usage line on stderr.
rc, out, err = run([])
check("2a. no filename exits 2", rc == 2, "got exit %d" % rc)
check("2b. no filename prints usage on stderr", "usage:" in err, "stderr: %r" % err)

# 3. Good fixture plain mode -> exit 0 and the kept rows exactly.
rc, out, err = run([FIXTURE])
check("3a. good fixture exits 0", rc == 0, "got exit %d" % rc)
check("3b. good fixture stderr empty", err.strip() == "", "stderr: %r" % err)
kept = json.loads(out)
check("3c. good fixture keeps exactly 3 rows", len(kept) == 3, "got %r" % kept)
check("3d. kept folders are valid1, valid2, also_valid in order",
      [r.get("folder") for r in kept] == ["valid1", "valid2", "also_valid"],
      "got %r" % [r.get("folder") for r in kept])

# 4. Good fixture --check -> exit 0 (all rows valid) and same kept rows.
rc, out, err = run(["--check", FIXTURE])
check("4a. good fixture --check exits 0", rc == 0, "got exit %d" % rc)
check("4b. good fixture --check keeps same 3 rows",
      sorted(r.get("folder") for r in json.loads(out))
      == ["also_valid", "valid1", "valid2"],
      "got %r" % out)
check("4c. good fixture --check stderr empty", err.strip() == "", "stderr: %r" % err)

# 5. Bad-URL fixture the test writes itself -> exit 1, exact stderr rows.
bad_rows = [
    {"folder": "check-good-row", "run_url": "https://example.com/run/1"},
    {"folder": "check-empty-url", "run_url": ""},
    {"folder": "check-blank-url", "run_url": "   "},
]
with open(BAD_FIXTURE, "w", encoding="utf-8") as fh:
    json.dump(bad_rows, fh)
try:
    rc, out, err = run(["--check", BAD_FIXTURE])
    check("5a. bad fixture --check exits 1", rc == 1, "got exit %d" % rc)
    lines = err.strip().splitlines()
    check("5b. bad fixture stderr names both bad rows in order",
          lines == ["run-log-index: missing run_url: check-empty-url",
                    "run-log-index: missing run_url: check-blank-url"],
          "stderr lines: %r" % lines)
    check("5c. bad fixture stderr does not name the good row",
          "check-good-row" not in err, "stderr: %r" % err)
    check("5d. bad fixture stdout still holds only the kept row",
          [r.get("folder") for r in json.loads(out)] == ["check-good-row"],
          "stdout: %r" % out)
finally:
    if os.path.exists(BAD_FIXTURE):
        os.unlink(BAD_FIXTURE)

# 6. Unreadable/missing file -> exit 2.
rc, out, err = run([os.path.join(HERE, "no-such-file.json")])
check("6a. missing file exits 2", rc == 2, "got exit %d" % rc)
check("6b. missing file mentions cannot read on stderr",
      "cannot read" in err, "stderr: %r" % err)

if failures:
    print()
    print("FAILED checks:")
    for f in failures:
        print("  - " + f)
    sys.exit(1)

print()
print("all checks passed")
sys.exit(0)
