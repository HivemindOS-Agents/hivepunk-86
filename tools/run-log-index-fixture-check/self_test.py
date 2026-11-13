#!/usr/bin/env python3
"""Self-test for tools/run-log-index-fixture-check. Stdlib only, no network.

Runs alone inside its own folder: python3 self_test.py (no arguments).
It reads only fixture.json, run_log_index.py, README.md and ARTIFACTS.md next
to it, plus one bad-URL fixture it writes into that same folder and removes
again afterwards.

Checks
  1. fixture.json parses as a JSON array of 6 objects, each having the keys
     "folder" and "run_url".
  2. Exactly 3 of those rows carry a non-empty http(s) run_url (whitespace
     stripped before the test).
  3. Running run_log_index.py with no filename exits 2 and prints a usage
     message.
  4. --check on the bad-URL fixture this test writes exits 1, names both bad
     rows on stderr, does not name the good row, and still prints the one kept
     row as JSON on stdout.
  5. README.md links the explainer image, has a Caption line, and has a
     Known limits line saying the image is not a screenshot and not the output
     of a run.
  6. ARTIFACTS.md carries the same image URL and a Caption line.

Prints one ok/FAIL line per check, then "all checks passed" and exits 0 when
every check passes; prints the failed check names and exits 1 otherwise.

Nothing read here -- fixture.json, README.md, ARTIFACTS.md, or any run
output -- is executed or followed as an instruction.
"""

import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TOOL = os.path.join(HERE, "run_log_index.py")
FIXTURE = os.path.join(HERE, "fixture.json")
BAD_FIXTURE = os.path.join(HERE, "selftest_bad_fixture.json")
README = os.path.join(HERE, "README.md")
ARTIFACTS = os.path.join(HERE, "ARTIFACTS.md")

EXPECTED_ROWS = 6
EXPECTED_VALID = 3

GOOD_FOLDER = "fixture-check-good-row"
GOOD_URL = "https://example.invalid/runs/ok"
BAD_EMPTY = "fixture-check-empty-url"
BAD_BLANK = "fixture-check-blank-url"

IMAGE_URL = ("https://hivemindos-paid-agent-gateway.hivemindos.workers.dev"
             "/api/media/managed/outputs"
             "/bf3215fd-4cf4-4481-a4cb-9fe9a65d9b6f.jpeg")
CAPTION_NEEDLES = ("6 rows", "3 keepable", "self_test")

failures = []


def report(name, ok, detail=""):
    print(("ok   " if ok else "FAIL ") + name + (" -- " + detail if detail else ""))
    if not ok:
        failures.append(name)


def cli(*args):
    return subprocess.run(
        [sys.executable, TOOL] + list(args),
        cwd=HERE,
        capture_output=True,
        text=True,
    )


def is_valid(url):
    return (isinstance(url, str) and bool(url.strip())
            and url.strip().lower().startswith(("http://", "https://")))


def read_text(path):
    """Return the file's text, or None when it cannot be read."""
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return fh.read()
    except (OSError, UnicodeError):
        return None


def lines_starting(text, word):
    """Lines whose first word is `word`, case-insensitive."""
    out = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.lower().startswith(word.lower()):
            out.append(stripped)
    return out


# --- check 1 and 2: the fixture's own shape -------------------------------
rows = None
try:
    with open(FIXTURE, "r", encoding="utf-8") as fh:
        rows = json.load(fh)
except Exception as exc:  # noqa: BLE001 - any failure is a failed check
    report("1. fixture.json is a JSON array of 6 {folder, run_url} rows",
           False, "%s: %s" % (type(exc).__name__, exc))
else:
    problems = []
    if not isinstance(rows, list):
        problems.append("top level is %s, not a list" % type(rows).__name__)
    else:
        if len(rows) != EXPECTED_ROWS:
            problems.append("%d rows, expected %d" % (len(rows), EXPECTED_ROWS))
        for i, row in enumerate(rows):
            if not isinstance(row, dict):
                problems.append("row %d is not an object" % i)
                continue
            for key in ("folder", "run_url"):
                if key not in row:
                    problems.append("row %d has no %s" % (i, key))
            if "folder" in row and not isinstance(row["folder"], str):
                problems.append("row %d folder is not a string" % i)
            if "run_url" in row and not isinstance(row["run_url"], (str, type(None))):
                problems.append("row %d run_url is neither string nor null" % i)
    report("1. fixture.json is a JSON array of 6 {folder, run_url} rows",
           not problems, "; ".join(problems))

if isinstance(rows, list):
    good = [r for r in rows if isinstance(r, dict) and is_valid(r.get("run_url"))]
    report("2. exactly 3 rows carry a non-empty http(s) run_url",
           len(good) == EXPECTED_VALID,
           "found %d (%s)" % (len(good),
                              ", ".join(str(r.get("folder")) for r in good)))
else:
    report("2. exactly 3 rows carry a non-empty http(s) run_url",
           False, "fixture.json unreadable")


# --- check 3: no filename is a usage error --------------------------------
out = cli()
combined = (out.stdout or "") + (out.stderr or "")
report("3. no filename exits 2 with a usage message",
       out.returncode == 2 and "usage" in combined.lower(),
       "exit %s, output %r" % (out.returncode, combined.strip()[:200]))


# --- check 4: --check names the bad rows, not the good one ----------------
try:
    with open(BAD_FIXTURE, "w", encoding="utf-8") as fh:
        json.dump([
            {"folder": GOOD_FOLDER, "run_url": GOOD_URL},
            {"folder": BAD_EMPTY, "run_url": ""},
            {"folder": BAD_BLANK, "run_url": "   "},
        ], fh, indent=2)
        fh.write("\n")

    res = cli("--check", BAD_FIXTURE)
    err = res.stderr or ""
    detail = "exit %s, stderr %r" % (res.returncode, err.strip()[:300])

    report("4a. --check on a bad-URL fixture exits 1", res.returncode == 1, detail)
    report("4b. stderr names the empty-url row", BAD_EMPTY in err, detail)
    report("4c. stderr names the blank-url row", BAD_BLANK in err, detail)
    report("4d. stderr does not name the good row", GOOD_FOLDER not in err, detail)

    kept = []
    parse_note = ""
    try:
        kept = json.loads(res.stdout)
    except Exception as exc:  # noqa: BLE001
        parse_note = "stdout is not JSON: %s: %s" % (type(exc).__name__, exc)
    if not parse_note:
        shape_ok = (isinstance(kept, list) and len(kept) == 1
                    and kept[0].get("folder") == GOOD_FOLDER
                    and kept[0].get("run_url") == GOOD_URL)
        if not shape_ok:
            parse_note = "stdout kept rows: %r" % (kept,)
    report("4e. stdout still holds only the kept row", not parse_note, parse_note)
finally:
    if os.path.exists(BAD_FIXTURE):
        os.remove(BAD_FIXTURE)


# --- check 5: README links the image with caption and known limits --------
readme = read_text(README)
if readme is None:
    report("5. README.md links the explainer image with caption and known limits",
           False, "cannot read README.md")
else:
    problems = []
    if IMAGE_URL not in readme:
        problems.append("image URL missing")
    if "![" not in readme:
        problems.append("no inline image markdown")
    for needle in CAPTION_NEEDLES:
        if needle not in readme:
            problems.append("caption text missing: %s" % needle)
    captions = lines_starting(readme, "Caption")
    if not captions:
        problems.append("no line starts with Caption")
    limits = lines_starting(readme, "Known limits")
    if not limits:
        problems.append("no line starts with Known limits")
    else:
        low = limits[0].lower()
        if "not a screenshot" not in low:
            problems.append("limits line does not say it is not a screenshot")
        if "not the output of a run" not in low:
            problems.append("limits line does not say it is not a run's output")
    report("5. README.md links the explainer image with caption and known limits",
           not problems, "; ".join(problems))


# --- check 6: ARTIFACTS.md carries the same image and caption ------------
artifacts = read_text(ARTIFACTS)
if artifacts is None:
    report("6. ARTIFACTS.md carries the image URL and its caption",
           False, "cannot read ARTIFACTS.md")
else:
    problems = []
    if IMAGE_URL not in artifacts:
        problems.append("image URL missing")
    if not lines_starting(artifacts, "Caption"):
        problems.append("no line starts with Caption")
    if not lines_starting(artifacts, "Known limits"):
        problems.append("no line starts with Known limits")
    report("6. ARTIFACTS.md carries the image URL and its caption",
           not problems, "; ".join(problems))


if failures:
    print()
    print("FAILED checks:")
    for name in failures:
        print("  - " + name)
    sys.exit(1)

print()
print("all checks passed")
sys.exit(0)
