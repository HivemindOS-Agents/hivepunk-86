#!/usr/bin/env python3
"""Self-test for run_and_record. Run: env -u PYTHONPATH python3 self_test.py; echo EXIT=$?"""
import os
import re
import subprocess
import sys
import tempfile
HERE = os.path.dirname(os.path.abspath(__file__))
RECORD = os.path.join(HERE, "SELFTEST_OUTPUT.md")
FENCE = "`" * 3
NESTED_ENV = "RUN_AND_RECORD_SELFTEST_NESTED"
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import run_and_record as rr
failures = []
def check(name, cond, detail=""):
    if cond:
        print("ok   " + name)
    else:
        line = "FAIL " + name + (" -- " + detail if detail else "")
        failures.append(line)
        print(line)
HELLO_CMD = [sys.executable, "-c", "print('hello')"]
FAIL_CMD = [sys.executable, "-c", "import sys; sys.stderr.write('oops\\n'); sys.exit(3)"]
def normalize_record(text):
    out_lines = []
    for line in text.splitlines():
        s = line
        if s.startswith("EXIT="):
            out_lines.append(s)
            continue
        s = re.sub(r"/(?:tmp|var/folders|private/var/folders|private/tmp)/[^\s'\")]*", "<TEMP_PATH>", s)
        s = re.sub(r"/tmp/[^\s'\")]*", "<TEMP_PATH>", s)
        if HERE and HERE in s:
            s = s.replace(HERE, "<HERE>")
        s = re.sub(r"\b\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:?\d{2})?\b", "<TIMESTAMP>", s)
        s = re.sub(r"\b\d{4}-\d{2}-\d{2}\b", "<DATE>", s)
        s = re.sub(r"\b\d{2}:\d{2}:\d{2}(?:\.\d+)?\b", "<TIME>", s)
        s = re.sub(r"\b(?:elapsed|duration|took|runtime|time)[=: ]+\d+(?:\.\d+)?\s*(?:ms|milliseconds?|s|sec|seconds?)\b", "<DURATION>", s, flags=re.I)
        s = re.sub(r"\b\d+(?:\.\d+)?\s*(?:ms|milliseconds?)\b", "<DURATION>", s, flags=re.I)
        s = re.sub(r"\b\d+(?:\.\d+)?\s*(?:seconds?|sec)\b", "<DURATION>", s, flags=re.I)
        s = re.sub(r"(runs/)(\d+)", r"\1<RUN_ID>", s)
        out_lines.append(s)
    result = "\n".join(out_lines)
    if text.endswith("\n"):
        result += "\n"
    return result
def run_checks():
    body = rr.render_record(HELLO_CMD, "hello\n", "", 0)
    i_cmd = body.find("command: ")
    i_out = body.find("## stdout")
    i_err = body.find("## stderr")
    i_exit = body.find("EXIT=0")
    check("1a. render holds command, stdout, stderr, EXIT in order", 0 <= i_cmd < i_out < i_err < i_exit, repr(body))
    check("1b. render holds the hello line", "hello" in body)
    check("1c. exactly one EXIT line", body.count("EXIT=") == 1)
    for label, args in (("empty command", ([], "", "", 0)), ("missing stdout", (HELLO_CMD, None, "", 0)), ("missing stderr", (HELLO_CMD, "", None, 0)), ("missing exit", (HELLO_CMD, "", "", None)), ("non-int exit", (HELLO_CMD, "", "", "0"))):
        try:
            rr.render_record(*args)
            raised = False
        except ValueError:
            raised = True
        check("2. render rejects " + label, raised)
    check("3. parse_command returns the rendered command", rr.parse_command(body) == HELLO_CMD, repr(rr.parse_command(body)))
    vol = "ran 2026-11-17 06:09:12 UTC in /tmp/tmp123/child elapsed: 1.23s runs/12345"
    vol2 = "ran 2027-01-02 03:04:05 UTC in /tmp/tmp999/child elapsed: 9.99s runs/99999"
    check("n1. normalize makes volatile-only differences equal", normalize_record(vol) == normalize_record(vol2), repr((normalize_record(vol), normalize_record(vol2))))
    check("n2. normalize does not mask stdout tampering", normalize_record("hello\nEXIT=0") != normalize_record("hello!\nEXIT=0"))
    check("n3. normalize does not mask EXIT tampering", normalize_record("hello\nEXIT=0") != normalize_record("hello\nEXIT=1"))
    with tempfile.TemporaryDirectory() as tmp:
        rec = os.path.join(tmp, "record.md")
        rc = rr.do_capture(HELLO_CMD, rec)
        check("4a. capture of hello exits 0", rc == 0, "got %r" % rc)
        text = open(rec, encoding="utf-8").read() if os.path.exists(rec) else ""
        check("4b. captured record holds hello and EXIT=0", "hello" in text and "EXIT=0" in text, repr(text))
        check("5. verify passes on a fresh record", rr.do_verify(rec) == 0)
        with open(rec, "a", encoding="utf-8") as fh:
            fh.write("tampered\n")
        check("6. verify fails on a tampered record", rr.do_verify(rec) == 1)
        rec2 = os.path.join(tmp, "record2.md")
        rc = rr.do_capture(FAIL_CMD, rec2)
        text2 = open(rec2, encoding="utf-8").read() if os.path.exists(rec2) else ""
        check("7a. capture returns the child exit code 3", rc == 3, "got %r" % rc)
        check("7b. record holds stderr oops and EXIT=3", "oops" in text2 and "EXIT=3" in text2, repr(text2))
        check("7c. verify passes on the exit-3 record", rr.do_verify(rec2) == 0)
        rec3 = os.path.join(tmp, "record3.md")
        rc = rr.do_capture([], rec3)
        check("8a. empty command exits 2", rc == 2, "got %r" % rc)
        check("8b. empty command writes no record", not os.path.exists(rec3))
        rec4 = os.path.join(tmp, "record4.md")
        rc = rr.do_capture(["no-such-executable-run-and-record-xyz"], rec4)
        check("9a. missing executable exits 2", rc == 2, "got %r" % rc)
        check("9b. missing executable writes no record", not os.path.exists(rec4))
        missing = os.path.join(tmp, "missing.md")
        check("10a. verify of missing record exits 2", rr.do_verify(missing) == 2)
        check("10b. verify of missing record writes nothing", not os.path.exists(missing))
        if os.environ.get(NESTED_ENV) == "1":
            print("skip 11a-11d. verify-record checks skipped in a nested run")
        else:
            try:
                seed = _spawn_child()
                seed_out, seed_err, seed_code = seed.stdout or "", seed.stderr or "", seed.returncode
            except OSError as exc:
                seed_out, seed_err, seed_code = "", str(exc), 1
            good = render_record(seed_out, seed_err, "EXIT=" + str(seed_code))
            good_path = os.path.join(tmp, "SELFTEST_OUTPUT.md")
            with open(good_path, "w", encoding="utf-8") as fh:
                fh.write(good)
            rc_good = verify_record_file(good_path)
            check("11a. verify-record passes on a known-good record", rc_good == 0, "got %r" % rc_good)
            tampered_out = render_record(seed_out + "tampered\n", seed_err, "EXIT=" + str(seed_code))
            tampered_path = os.path.join(tmp, "tampered_stdout.md")
            with open(tampered_path, "w", encoding="utf-8") as fh:
                fh.write(tampered_out)
            rc_tampered = verify_record_file(tampered_path)
            check("11b. verify-record fails on a stdout-altered record", rc_tampered == 1, "got %r" % rc_tampered)
            after = open(tampered_path, encoding="utf-8").read()
            check("11c. failed verify-record leaves the altered file untouched", after == tampered_out)
            tampered_exit = render_record(seed_out, seed_err, "EXIT=" + str(1 - seed_code if seed_code in (0, 1) else 1))
            exit_path = os.path.join(tmp, "tampered_exit.md")
            with open(exit_path, "w", encoding="utf-8") as fh:
                fh.write(tampered_exit)
            rc_exit = verify_record_file(exit_path)
            check("11d. verify-record fails on an EXIT-altered record", rc_exit == 1, "got %r" % rc_exit)
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
    return "\n".join(["# self_test output (captured)", "", "command: env -u PYTHONPATH python3 self_test.py; echo EXIT=$?", "", "## stdout", FENCE, stdout.rstrip("\n"), FENCE, "", "## stderr", FENCE, stderr.rstrip("\n"), FENCE, "", exit_line, ""])
def record_order_problem(text):
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
        return "record has more than one EXIT= line: " + ", ".join(exits)
    tail = text[i_err:]
    if tail.find(exits[0]) < 0:
        return "EXIT= line does not follow the stderr section"
    if tail.split(exits[0], 1)[1].strip():
        return "lines follow the EXIT= line"
    return ""
def _spawn_child():
    env = dict(os.environ)
    env.pop("PYTHONPATH", None)
    env[NESTED_ENV] = "1"
    return subprocess.run([sys.executable, os.path.join(HERE, "self_test.py")], cwd=HERE, capture_output=True, text=True, env=env)
def capture_mode():
    try:
        child = _spawn_child()
    except OSError as exc:
        print("self_test: could not start the check run: %s" % exc, file=sys.stderr)
        body = render_record("", "self-test could not be started: %s" % exc, "NOT_RUN")
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
        print("self_test: refusing to write a bad record: %s" % problem, file=sys.stderr)
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
    print("self_test: wrote %s (%s)" % (RECORD, exit_line), file=sys.stderr)
    return 0 if code == 0 else 1
def verify_record_file(record_path):
    if not os.path.exists(record_path):
        print("FAIL verify-record: %s does not exist" % record_path)
        return 1
    try:
        with open(record_path, "r", encoding="utf-8") as fh:
            text = fh.read()
    except (OSError, UnicodeError) as exc:
        print("FAIL verify-record: cannot read %s: %s" % (record_path, exc))
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
    fresh = render_record(child.stdout or "", child.stderr or "", "EXIT=" + str(child.returncode))
    if normalize_record(text) == normalize_record(fresh):
        print("ok   verify-record: stored record matches a fresh run (EXIT=%d)" % child.returncode)
        return 0
    print("FAIL verify-record: stored record differs from a fresh run")
    print("     fresh run says: EXIT=" + str(child.returncode))
    stale = [ln for ln in text.splitlines() if ln.startswith("EXIT=")]
    print("     stored record says: " + (stale[0] if stale else "no EXIT= line"))
    return 1
def verify_record():
    return verify_record_file(RECORD)
if __name__ == "__main__":
    if "--capture" in sys.argv[1:]:
        sys.exit(capture_mode())
    if "--verify-record" in sys.argv[1:]:
        sys.exit(verify_record())
    sys.exit(run_checks())
