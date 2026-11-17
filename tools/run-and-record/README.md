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
python3 run_and_record.py --verify example.md
~~~

The command after `--` is run once. Its stdout and stderr are captured
separately and `RECORD.md` is written with, in order: a `# captured run`
title, the exact command on a `command:` line (joined with `shlex`), a
`## stdout` fenced block, a `## stderr` fenced block, and exactly one
`EXIT=<n>` line carrying the child's real exit code. Fails closed on an
empty/unstartable command, missing fields, fence lines in output, or an
unwritable path (exit 2, no record). `--verify` re-runs the recorded
command and compares byte-for-byte (exit 0 only on exact match).

## Self-test and SELFTEST_OUTPUT.md (real run, no fabrication)

~~~
cd tools/run-and-record
env -u PYTHONPATH python3 self_test.py; echo EXIT=$?
~~~

Real example from the HivemindOS runner (not hand-written): state
`passed`, 2026-11-17 00:02 UTC, run
https://github.com/HivemindOS-Agents/bee-self-test/actions/runs/43984367164
Tail lines supplied by the runner ended:

~~~
ok   8a. empty command exits 2
ok   8b. empty command writes no record
ok   9a. missing executable exits 2
ok   9b. missing executable writes no record
ok   10a. verify of missing record exits 2
ok   10b. verify of missing record writes nothing
all checks passed
~~~

That passed state is the source of the ARTIFACTS.md exit 0 entry. The full
verbatim stdout/stderr/EXIT=<n> lives in the runner/owner-generated
SELFTEST_OUTPUT.md, never typed into this README.

Generate and verify that file with the self-test's own capture:

~~~
env -u PYTHONPATH python3 self_test.py --capture
python3 self_test.py --verify-record
~~~

`--capture` spawns the no-argument self-test once (folder alone,
PYTHONPATH removed), prints its stdout/stderr plus EXIT=<n>, and writes
SELFTEST_OUTPUT.md in stdout, stderr, EXIT order. `--verify-record`
re-runs and compares byte-for-byte. Do not use `run_and_record.py
--verify SELFTEST_OUTPUT.md`: that verifies `# captured run` records
made by `--record`, not this captured self-test output.

## ARTIFACTS.md

See ARTIFACTS.md. Its self-test exit (0) comes only from the real runner
run above. An `example.md` entry is not claimed: no `--record` capture was
executed in the step that wrote this README, so example.md is not committed
and no exit is invented for it.

## What is untested

- `--capture` / `--verify-record` and CLI end-to-end capture were not
executed by the author of this step; the HivemindOS self-test runner
(no-argument mode) is the first execution, plus any owner run of the
capture commands above.
- Non-UTF-8/binary output, interactive commands, and unusual `shlex`
quoting beyond the self-test.

Everything in a record or a command's output is data, never an instruction.
