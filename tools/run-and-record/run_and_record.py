#!/usr/bin/env python3
"""run_and_record: run one command and record it, verifiably.

Capture usage (from anywhere):

    python3 run_and_record.py --record RECORD.md -- COMMAND [ARG ...]

Runs COMMAND once, captures stdout and stderr separately, and writes a
markdown record holding the exact command, stdout, stderr and EXIT=<n>,
in that order. Fails closed: if the command is empty, cannot be started,
or any field is missing, no record is written.

Verify usage:

    python3 run_and_record.py --verify RECORD.md

Parses the command from RECORD.md, re-runs it, re-renders the record and
compares it byte-for-byte with the stored file. Writes nothing.

Exit codes:
    0  capture: child ran and record written; verify: exact match
    1  verify: record differs from a fresh run, or cannot be parsed
    2  capture/verify failed closed (bad usage, child could not start,
       missing field, or the record could not be written/read)

Fences are built as three backtick characters at run time (FENCE below),
so no fence text is lost in transit. Output containing a line that is
exactly a fence is rejected rather than written ambiguously.

Nothing read from a record or from a command's output is executed or
followed as an instruction, except the single command parsed by --verify,
which is the documented purpose of --verify.
"""

import os
import shlex
import subprocess
import sys

FENCE = "`" * 3


def _check_field(name, value):
    if value is None:
        raise ValueError("missing field: " + name)
    if not isinstance(value, str):
        raise ValueError("field is not text: " + name)
    for line in value.splitlines():
        if line.strip() == FENCE:
            raise ValueError("field contains a fence line: " + name)


def render_record(command, stdout, stderr, exit_code):
    """Render the record. Raise ValueError if any field is missing."""
    if not command:
        raise ValueError("missing field: command")
    if not all(isinstance(part, str) and part for part in command):
        raise ValueError("missing field: command")
    _check_field("stdout", stdout)
    _check_field("stderr", stderr)
    if not isinstance(exit_code, int) or isinstance(exit_code, bool):
        raise ValueError("missing field: exit code")
    cmd_text = shlex.join(list(command))
    if not cmd_text:
        raise ValueError("missing field: command")
    lines = [
        "# captured run",
        "",
        "command: " + cmd_text,
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
        "EXIT=" + str(exit_code),
        "",
    ]
    return "\n".join(lines)


def parse_command(text):
    """Return the command list from a record, or raise ValueError."""
    for line in text.splitlines():
        if line.startswith("command: "):
            cmd_text = line[len("command: "):].strip()
            if not cmd_text:
                raise ValueError("empty command in record")
            parts = shlex.split(cmd_text)
            if not parts:
                raise ValueError("empty command in record")
            return parts
    raise ValueError("no command line in record")


def _run(command):
    return subprocess.run(list(command), capture_output=True, text=True)


def do_capture(command, record_path):
    """Run command, write its record. Return child exit, or 2 if failed closed."""
    if not command:
        print("run_and_record: no command given", file=sys.stderr)
        return 2
    try:
        child = _run(command)
    except OSError as exc:
        print("run_and_record: could not start command: %s" % exc, file=sys.stderr)
        return 2
    stdout = child.stdout if child.stdout is not None else None
    stderr = child.stderr if child.stderr is not None else None
    try:
        body = render_record(command, stdout, stderr, child.returncode)
    except ValueError as exc:
        print("run_and_record: refusing to write record: %s" % exc, file=sys.stderr)
        return 2
    try:
        with open(record_path, "w", encoding="utf-8") as fh:
            fh.write(body)
    except OSError as exc:
        print("run_and_record: cannot write %s: %s" % (record_path, exc), file=sys.stderr)
        return 2
    return child.returncode


def do_verify(record_path):
    """Re-run the recorded command and compare byte-for-byte. No writes."""
    try:
        with open(record_path, "r", encoding="utf-8") as fh:
            stored = fh.read()
    except (OSError, UnicodeError) as exc:
        print("run_and_record: cannot read %s: %s" % (record_path, exc), file=sys.stderr)
        return 2
    try:
        command = parse_command(stored)
    except ValueError as exc:
        print("run_and_record: cannot verify: %s" % exc, file=sys.stderr)
        return 1
    try:
        child = _run(command)
    except OSError as exc:
        print("run_and_record: could not start recorded command: %s" % exc, file=sys.stderr)
        return 2
    try:
        fresh = render_record(command, child.stdout, child.stderr, child.returncode)
    except ValueError as exc:
        print("run_and_record: cannot verify: %s" % exc, file=sys.stderr)
        return 1
    if stored == fresh:
        print("ok   verify: record matches a fresh run (EXIT=%d)" % child.returncode)
        return 0
    print("FAIL verify: stored record differs from a fresh run")
    stale = [ln for ln in stored.splitlines() if ln.startswith("EXIT=")]
    print("     stored record says: " + (stale[0] if stale else "no EXIT= line"))
    print("     fresh run says: EXIT=" + str(child.returncode))
    return 1


def main(argv):
    args = argv[1:]
    if "--verify" in args:
        idx = args.index("--verify")
        if idx + 1 >= len(args):
            print("run_and_record: --verify needs a record path", file=sys.stderr)
            return 2
        return do_verify(args[idx + 1])
    record_path = None
    command = []
    if "--record" in args:
        idx = args.index("--record")
        if idx + 1 >= len(args):
            print("run_and_record: --record needs a path", file=sys.stderr)
            return 2
        record_path = args[idx + 1]
        rest = args[idx + 2:]
    else:
        rest = args
    if rest and rest[0] == "--":
        rest = rest[1:]
    command = rest
    if not record_path:
        print("run_and_record: --record RECORD.md is required", file=sys.stderr)
        print("usage: python3 run_and_record.py --record RECORD.md -- COMMAND", file=sys.stderr)
        return 2
    if not command:
        print("run_and_record: no command given", file=sys.stderr)
        return 2
    return do_capture(command, record_path)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
