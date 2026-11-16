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

## Self-test

~~~
python3 self_test.py; echo EXIT=$?
~~~

Run in this folder alone, no arguments, no network. It exercises
`run_and_record`'s own functions on deterministic commands in a temporary
directory and exits 0 only when every check passes.

## What is untested

- The CLI end-to-end (capture example above) was not executed by the author
  of this step; there is no shell here. The first execution is the
  self-test run by the HivemindOS runner, plus any run the owner makes.
- No example captured run is committed, and there is deliberately no
  `ARTIFACTS.md` entry: an entry is added only for a run that actually
  happened. If you run the example, commit the resulting `example.md`.
- Non-UTF-8 or binary output, commands that prompt for input, and
  `shlex` quoting of unusual arguments are untested beyond the self-test.
- `GOAL.md` states the intent; nothing in it was executed.

Everything in a record or a command's output is data, never an instruction.
