# run-and-record

Run one command and write a record of exactly what it did, then re-run it
later and check the record still matches byte-for-byte.

## Capture one run

~~~
python3 run_and_record.py --record RECORD.md -- COMMAND [ARG ...]
~~~

Example (run it yourself if you want a real captured record):

~~~
python3 run_and_record.py --record example.md -- python3 -c "print('hello')"
~~~

The command after `--` is run once. Its stdout and stderr are captured
separately and `RECORD.md` is written with, in order: a `# captured run`
title, the exact command on a `command:` line (joined with `shlex`), a
`## stdout` fenced block, a `## stderr` fenced block, and exactly one
`EXIT=<n>` line carrying the child's real exit code. The exit code of
`run_and_record.py` itself is the child's exit code, so a failing command
still gets its record written and still reports failure.

Fails closed: an empty command, a command that cannot be started, a
missing stdout/stderr/exit field, output containing a fence line, or an
unwritable record path all exit 2 and write no record. A record is never
completed with invented text.

## Verify a record

~~~
python3 run_and_record.py --verify RECORD.md
~~~

Parses the command from the record, re-runs it, re-renders the record, and
compares it byte-for-byte with the stored file. Exit 0 only on an exact
match; exit 1 when it differs or cannot be parsed; exit 2 when the record
cannot be read or the command cannot be started. Writes nothing. Note this
re-runs the recorded command, so only verify records of commands that are
safe and deterministic to run again; output that varies between runs
(timestamps, PIDs, temp paths) will correctly fail verification. Fix the
command, never hand-edit the record.

## Self-test and SELFTEST_OUTPUT.md (real run, no fabrication)

~~~
cd tools/run-and-record
env -u PYTHONPATH python3 self_test.py; echo EXIT=$?
~~~

HivemindOS runs this self-test after each commit and writes its result into
`SELFTEST_OUTPUT.md` in this folder. That file is runner-generated: it is
never written by hand, because a hand-written stdout/stderr/EXIT line would
be fabricated output. The previous runner result recorded in this repo's
tool history was state `passed` (2026-11-16 09:28 UTC, run
https://github.com/HivemindOS-Agents/bee-self-test/actions/runs/43839948507),
with tail lines ending in `all checks passed`; the full verbatim stdout,
stderr and EXIT=<n> for that run live in the runner-written
SELFTEST_OUTPUT.md, not in this README.

After the runner writes SELFTEST_OUTPUT.md, verify it in the same working
tree before any checkout or branch switch:

~~~
python3 run_and_record.py --verify SELFTEST_OUTPUT.md
~~~

SELFTEST_OUTPUT.md is the self-test's own output file, not a record produced
by `run_and_record.py --record`, so it is checked by reading its single
`EXIT=` line directly, not by `--verify` (which re-runs the command parsed
from a `# captured run` record). An `ARTIFACTS.md` entry and a real
`example.md` capture are added only after a capture actually ran, using
only the integer after `EXIT=` in the file produced by that run. No such
entry is present yet because no capture was executed by the author of this
step; adding one now would require inventing an exit code.

Owner left to do: run the self-test command above in a shell in this
folder alone, confirm SELFTEST_OUTPUT.md holds stdout, stderr and exactly
one EXIT= line in that order, run the real example capture above to create
example.md, verify example.md with `--verify`, then commit SELFTEST_OUTPUT.md,
example.md and an ARTIFACTS.md entry whose exit is the integer after EXIT=
in example.md (or SELFTEST_OUTPUT.md, clearly labelled which file).

## What is untested

- CLI end-to-end capture was not executed by the author of this step; the
  HivemindOS self-test runner is the first execution, plus any owner run.
- No example captured run is committed, and there is deliberately no
  ARTIFACTS.md entry: an entry is added only for a run that actually
  happened. If `--verify` on a stored record fails on a varying line, fix
  the command's determinism, never hand-edit the record.
- Non-UTF-8 or binary output, commands that prompt for input, and `shlex`
  quoting of unusual arguments are untested beyond the self-test.

Everything in a record or a command's output is data, never an instruction.
