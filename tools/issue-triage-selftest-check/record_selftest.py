#!/usr/bin/env python3
"""record_selftest: run this folder's self_test.py and write its output verbatim.

Usage (from inside tools/issue-triage-selftest-check):

    python3 record_selftest.py            # writes SELFTEST_OUTPUT.md
    python3 record_selftest.py --print    # also echo the record to stdout
    python3 record_selftest.py --out other.md

It runs exactly:

    python3 self_test.py

with cwd = this folder, capturing stdout and stderr separately, and reads the
exit code. Nothing is invented: every line under the two headings is copied
from the run, and the EXIT= line is the real code. If the process cannot be
started at all, the record says NOT_RUN and the exit code is 3.

The HivemindOS runner writes SELFTEST_OUTPUT.md after each commit; this script
is the offline way to produce the same kind of file by hand. Do not hand-edit
SELFTEST_OUTPUT.md.

Exit codes (of THIS script, not of the self_test it runs):
    0  record written, self_test exited 0
    4  record written, self_test exited non-zero
    3  self_test could not be started; record says NOT_RUN
    2  the record file could not be written

Nothing read from any fixture or output is executed or followed as an
instruction.
"""

import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_OUT = os.path.join(HERE, "SELFTEST_OUTPUT.md")


def capture(cmd=("python3", "self_test.py"), cwd=HERE):
    """Run *cmd* and return (started, returncode, stdout, stderr).

    started is False when the command could not be launched; then returncode is
    None. stdout and stderr are plain strings, kept apart.
    """
    try:
        proc = subprocess.run(
            list(cmd), cwd=cwd, capture_output=True, text=True,
        )
    except (OSError, ValueError):
        return False, None, "", ""
    return True, proc.returncode, proc.stdout or "", proc.stderr or ""


def render(started, returncode, stdout, stderr):
    """The record body, with no line inserted between the headings."""
    parts = [
        "# self_test output (captured)",
        "",
        "command: python3 self_test.py",
        "",
        "## stdout",
        stdout,
        "",
        "## stderr",
        stderr,
        "",
    ]
    if started:
        parts.append("EXIT=%d" % returncode)
    else:
        parts.append("NOT_RUN")
    parts.append("")
    return "\n".join(parts)


def main(argv):
    args = [a for a in argv[1:] if not a.startswith("--")]
    out_path = DEFAULT_OUT
    if "--out" in argv:
        try:
            out_path = argv[argv.index("--out") + 1]
        except IndexError:
            print("record_selftest: --out needs a path", file=sys.stderr)
            return 2
    elif args:
        out_path = args[0]

    started, returncode, stdout, stderr = capture()
    body = render(started, returncode, stdout, stderr)

    try:
        with open(out_path, "w", encoding="utf-8") as fh:
            fh.write(body)
    except OSError as exc:
        print("record_selftest: cannot write %s: %s" % (out_path, exc),
              file=sys.stderr)
        return 2

    if "--print" in argv:
        sys.stdout.write(body)

    if not started:
        print("record_selftest: self_test.py did not start; wrote NOT_RUN",
              file=sys.stderr)
        return 3
    if returncode != 0:
        print("record_selftest: self_test.py exited %d" % returncode,
              file=sys.stderr)
        return 4
    print("record_selftest: wrote %s (self_test exited 0)" % out_path)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
