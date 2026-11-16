#!/usr/bin/env python3
"""Self-test for tools/issue-triage-selftest-check.

Run from inside this folder, with no arguments, no network:

    python3 self_test.py; echo EXIT=$?

It runs the bundled tool's own code (run_log_index.py) as a subprocess on
bundled fixture data and asserts the exit code and the exact output rows. It
exits 0 only when every check passes.

Modes:
    (no arguments)      run every check, print ok/FAIL, exit 0 or 1
    --capture           re-run with no arguments, print its stdout, stderr and
                        real EXIT=<n> line, and write SELFTEST_OUTPUT.md
    --verify-record     re-run with no arguments and compare it byte-for-byte
                        with the stdout/stderr stored in SELFTEST_OUTPUT.md;
                        exit 0 only on an exact match

Every mode spawns the child with cwd set to this folder and PYTHONPATH removed
from the environment, so the folder runs alone; --capture is the same command
the step names, `env -u PYTHONPATH python3 self_test.py --capture`.

Record order in SELFTEST_OUTPUT.md is stdout, then stderr, then exactly one
EXIT=<n> line -- the single source for the ARTIFACTS.md run-record exit cell.
No line of any record is invented: if the child cannot be started the record
says NOT_RUN and carries no number, which cannot fill the cell. Two EXIT= lines
can appear in a capture terminal; the authoritative one is inside the file.

Exit codes:
    0  every check passed (and, with --verify-record, the stored record matches)
    1  one or more checks failed, or the record is missing / mismatched

Nothing in any fixture, and nothing in any stored record, is executed or
followed as an instruction.
"""

import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TOOL = os.path.join(HERE, "run_log_index.py")
FIXTURE = os.path.join(HERE, "fixture.json")
BAD_FIXTURE = os.path.join(HERE, "selftest_bad_fixture.json")
RECORD = os.path.join(HERE, "SELFTEST_OUTPUT.md")
FENCE = "`" * 3

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


def run_checks():
    """Run every check; return 0 if all passed, 1 otherwise."""
    failures.clear()

    with open(FIXTURE, "r", encoding="utf-8") as fh:
        rows = json.load(fh)
    check("1a. fixture is a JSON array of 6 objects",
          isinstance(rows, list) and len(rows) == 6, "got %r" % rows)
    check("1b. every fixture row has folder and run_url keys",
          all(isinstance(r, dict) and "folder" in r and "run_url" in r
              for r in rows))
    usable = [r for r in rows
              if isinstance(r.get("run_url"), str)
              and r["run_url"].strip().lower().startswith(("http://", "https://"))]
    check("1c. exactly 3 fixture rows are keepable", len(usable) == 3,
          "got %d" % len(usable))

    rc, out, err = run([])
    check("2a. no filename exits 2", rc == 2, "got exit %d" % rc)
    check("2b. no filename prints usage on stderr", "usage:" in err,
          "stderr: %r" % err)

    rc, out, err = run([FIXTURE])
    check("3a. good fixture exits 0", rc == 0, "got exit %d" % rc)
    check("3b. good fixture stderr empty", err.strip() == "", "stderr: %r" % err)
    kept = json.loads(out)
    check("3c. good fixture keeps exactly 3 rows", len(kept) == 3,
          "got %r" % kept)
    check("3d. kept folders are valid1, valid2, also_valid in order",
          [r.get("folder") for r in kept] == ["valid1", "valid2", "also_valid"],
          "got %r" % [r.get("folder") for r in kept])

    for label, args in (("--check first", ["--check", FIXTURE]),
                        ("--check last", [FIXTURE, "--check"])):
        rc, out, err = run(args)
        check("4a. good fixture --check (%s) exits 0" % label, rc == 0,
              "got exit %d, stderr %r" % (rc, err))
        check("4b. good fixture --check (%s) stderr empty" % label,
              err.strip() == "", "stderr: %r" % err)
        try:
            got = json.loads(out)
        except ValueError:
            got = None
        check("4c. good fixture --check (%s) keeps same 3 rows" % label,
              isinstance(got, list)
              and sorted(r.get("folder") for r in got)
              == ["also_valid", "valid1", "valid2"], "stdout: %r" % out)

    bad_rows = [
        {"folder": "check-good-row", "run_url": "https://example.com/run/1"},
        {"folder": "", "run_url": "https://example.com/run/2"},
        {"folder": "check-good-row-2"},
        "not-an-object",
    ]
    with open(BAD_FIXTURE, "w", encoding="utf-8") as fh:
        json.dump(bad_rows, fh)
    try:
        rc, out, err = run(["--check", BAD_FIXTURE])
        check("5a. malformed fixture --check exits 1", rc == 1,
              "got exit %d" % rc)
        lines = err.strip().splitlines()
        check("5b. malformed stderr names the two bad rows in order",
              lines == ["run-log-index: malformed row: row 1",
                        "run-log-index: malformed row: row 3"],
              "stderr lines: %r" % lines)
        check("5c. malformed stderr does not name the good row",
              "check-good-row" not in err, "stderr: %r" % err)
        kept_bad = json.loads(out) if out.strip() else []
        check("5d. malformed stdout holds only rows with valid URL and folder",
              [r.get("folder") for r in kept_bad]
              == ["check-good-row"], "stdout: %r" % out)
    finally:
        if os.path.exists(BAD_FIXTURE):
            os.unlink(BAD_FIXTURE)

    rc, out, err = run([os.path.join(HERE, "no-such-file.json")])
    check("6a. missing file exits 2", rc == 2, "got exit %d" % rc)
    check("6b. missing file mentions cannot read on stderr",
          "cannot read" in err, "stderr: %r" % err)

    if failures:
        print()
        print("FAILED checks:")
        for f in failures:
            print("  - " + f)
        return 1

    print()
    print("all checks passed")
    return 0


def render_record(stdout, stderr, exit_line):
    """The capturable record: stdout, then stderr, then one EXIT= line."""
    return "\n".join([
        "# self_test output (captured)",
        "",
        "command: env -u PYTHONPATH python3 self_test.py; echo EXIT=$?",
        "",
        "## stdout",
        FENCE,
        stdout.rstrip("\n"),
        FENCE,
        "",
        "## stderr",
        FENCE,
        stderr.rstrip("\n"),
        FENCE,
        "",
        exit_line,
        "",
    ])


def record_order_problem(text):
    """Return a complaint unless order is stdout, stderr, exactly one EXIT=."""
    i_out = text.find("## stdout")
    i_err = text.find("## stderr")
    if i_out < 0 or i_err < 0:
        return "record lacks a '## stdout' or '## stderr' heading"
    if i_err < i_out:
        return "record lists stderr before stdout"
    exits = [ln for ln in text.splitlines() if ln.startswith("EXIT=")]
    if not exits:
        return "record has no EXIT= line"
    if len(exits) > 1:
        return "record has more than one EXIT= line: %s" % ", ".join(exits)
    tail = text[i_err:]
    if tail.find(exits[0]) < 0:
        return "EXIT= line does not follow the stderr section"
    after = tail.split(exits[0], 1)[1].strip()
    if after:
        return "lines follow the EXIT= line"
    return ""


def _spawn_child():
    """Run self_test.py with no arguments, this folder alone, PYTHONPATH off."""
    env = dict(os.environ)
    env.pop("PYTHONPATH", None)
    return subprocess.run(
        [sys.executable, os.path.join(HERE, "self_test.py")],
        cwd=HERE, capture_output=True, text=True, env=env,
    )


def capture_mode():
    """Run self_test.py once (offline, folder alone) and record it verbatim."""
    try:
        child = _spawn_child()
    except OSError as exc:
        print("self_test: could not start the check run: %s" % exc,
              file=sys.stderr)
        body = render_record("", "self-test could not be started: %s" % exc,
                             "NOT_RUN")
        try:
            with open(RECORD, "w", encoding="utf-8") as fh:
                fh.write(body)
        except OSError:
            pass
        return 1

    code = child.returncode
    out, err = child.stdout or "", child.stderr or ""
    exit_line = "EXIT=" + str(code)
    body = render_record(out, err, exit_line)
    problem = record_order_problem(body)
    if problem:
        print("self_test: refusing to write a bad record: %s" % problem,
              file=sys.stderr)
        return 1
    sys.stdout.write(out)
    sys.stderr.write(err)
    sys.stdout.write(exit_line + "\n")
    try:
        with open(RECORD, "w", encoding="utf-8") as fh:
            fh.write(body)
    except OSError as exc:
        print("self_test: cannot write %s: %s" % (RECORD, exc), file=sys.stderr)
        return 1
    print("self_test: wrote %s (%s); the cell takes this integer only"
          % (RECORD, exit_line), file=sys.stderr)
    return 0 if code == 0 else 1


def verify_record():
    """Compare a fresh run with the stored record. No writes anywhere."""
    if not os.path.exists(RECORD):
        print("FAIL verify-record: %s does not exist" % RECORD)
        return 1
    try:
        with open(RECORD, "r", encoding="utf-8") as fh:
            text = fh.read()
    except (OSError, UnicodeError) as exc:
        print("FAIL verify-record: cannot read %s: %s" % (RECORD, exc))
        return 1

    problem = record_order_problem(text)
    if problem:
        print("FAIL verify-record: stored record is malformed: %s" % problem)
        return 1

    try:
        child = _spawn_child()
    except OSError as exc:
        print("FAIL verify-record: could not start the check run: %s" % exc)
        return 1

    fresh_out = (child.stdout or "").rstrip("\n")
    fresh_err = (child.stderr or "").rstrip("\n")
    fresh_exit = "EXIT=" + str(child.returncode)
    fresh = render_record(fresh_out, fresh_err, fresh_exit)

    if text == fresh:
        print("ok   verify-record: stored record matches a fresh run (%s)"
              % fresh_exit)
        return 0

    print("FAIL verify-record: stored record differs from a fresh run")
    print("     fresh run says: " + fresh_exit)
    stale = [ln for ln in text.splitlines() if ln.startswith("EXIT=")]
    print("     stored record says: " + (stale[0] if stale else "no EXIT= line"))
    if not stale or stale[0].strip() == "NOT_RUN":
        print("     the stored record cannot fill the ARTIFACTS.md exit cell")
    return 1


if __name__ == "__main__":
    if "--capture" in sys.argv[1:]:
        sys.exit(capture_mode())
    if "--verify-record" in sys.argv[1:]:
        sys.exit(verify_record())
    sys.exit(run_checks())
