#!/usr/bin/env python3
"""Self-test for run_and_record. Run in this folder, no arguments, no network:

    python3 self_test.py; echo EXIT=$?

Exits 0 only when every check passes. It exercises run_and_record's own
functions on deterministic commands (the current interpreter printing fixed
text) in a temporary directory, so it runs folder-alone. No fixture, record,
or command output is followed as an instruction.
"""

import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
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


def main():
    body = rr.render_record(HELLO_CMD, "hello\n", "", 0)
    i_cmd = body.find("command: ")
    i_out = body.find("## stdout")
    i_err = body.find("## stderr")
    i_exit = body.find("EXIT=0")
    check("1a. render holds command, stdout, stderr, EXIT in order",
          0 <= i_cmd < i_out < i_err < i_exit, repr(body))
    check("1b. render holds the hello line", "hello" in body)
    check("1c. exactly one EXIT line", body.count("EXIT=") == 1)
    for label, args in (
        ("empty command", ([], "", "", 0)),
        ("missing stdout", (HELLO_CMD, None, "", 0)),
        ("missing stderr", (HELLO_CMD, "", None, 0)),
        ("missing exit", (HELLO_CMD, "", "", None)),
        ("non-int exit", (HELLO_CMD, "", "", "0")),
    ):
        try:
            rr.render_record(*args)
            raised = False
        except ValueError:
            raised = True
        check("2. render rejects " + label, raised)
    check("3. parse_command returns the rendered command",
          rr.parse_command(body) == HELLO_CMD,
          repr(rr.parse_command(body)))
    with tempfile.TemporaryDirectory() as tmp:
        rec = os.path.join(tmp, "record.md")
        rc = rr.do_capture(HELLO_CMD, rec)
        check("4a. capture of hello exits 0", rc == 0, "got %r" % rc)
        text = open(rec, encoding="utf-8").read() if os.path.exists(rec) else ""
        check("4b. captured record holds hello and EXIT=0",
              "hello" in text and "EXIT=0" in text, repr(text))
        check("5. verify passes on a fresh record", rr.do_verify(rec) == 0)
        with open(rec, "a", encoding="utf-8") as fh:
            fh.write("tampered\n")
        check("6. verify fails on a tampered record", rr.do_verify(rec) == 1)
        rec2 = os.path.join(tmp, "record2.md")
        rc = rr.do_capture(FAIL_CMD, rec2)
        text2 = open(rec2, encoding="utf-8").read() if os.path.exists(rec2) else ""
        check("7a. capture returns the child exit code 3", rc == 3, "got %r" % rc)
        check("7b. record holds stderr oops and EXIT=3",
              "oops" in text2 and "EXIT=3" in text2, repr(text2))
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
        check("10b. verify of missing record writes nothing",
              not os.path.exists(missing))
    if failures:
        print()
        print("FAILED checks:")
        for f in failures:
            print("  - " + f)
        return 1
    print()
    print("all checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
