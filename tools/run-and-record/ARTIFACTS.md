# ARTIFACTS.md - tools/run-and-record

| artifact | file | what it is | checked by | exit |
| --- | --- | --- | --- | --- |
| run-and-record tool | `run_and_record.py` | runs one command, records command/stdout/stderr/EXIT=<n>; `--verify` re-runs and compares byte-for-byte | `self_test.py` | - |
| self-test | `self_test.py` | checks 1-10, normalization checks n1-n3, verify-path checks 11a-11d; `--capture` writes SELFTEST_OUTPUT.md from a real run, `--verify-record` re-checks it after normalizing volatile timestamps/durations/temp-paths on both records | HivemindOS runner after each commit | - |
| self-test run record | `SELFTEST_OUTPUT.md` | the mandated command line, then stdout, then stderr, then exactly one EXIT=<n>. Its first line is `STATUS: PASS | EXIT=0 | FAILED_CHECK=none`, attributed to the HivemindOS runner run 44678372235; its `## stdout` and `## stderr` sections are EMPTY because that run's full streams were never supplied, and its runner-supplied tail is quoted separately as data. It is not an agent-executed capture. | runner-reported run 44678372235 (state `passed`, 2026-11-20 05:02 UTC); a direct `--capture` or owner run is still owed | 0 (runner-reported run 44678372235; not an agent-executed capture) |
| README | `README.md` | usage, capture/verify procedure, deterministic-compare and tamper checks, real runner examples, untested list | none | - |

## Self-test exit (real run only)

- Exact command, to be run alone in `tools/run-and-record`:
  `env -u PYTHONPATH python3 self_test.py; echo EXIT=$?`
- Exit recorded: 0. No command was executed by the agent writing this
  file; the integer 0 is the HivemindOS runner's reported result for run
  https://github.com/HivemindOS-Agents/bee-self-test/actions/runs/44678372235
  (state `passed`, 2026-11-20 05:02 UTC, tail ending `all checks passed`).
  It is attributed, not locally reproduced.
- When the runner (or an owner, or `--capture`) produces a direct run of
  the command above, replace `SELFTEST_OUTPUT.md`'s empty sections with
  that run's real stdout, stderr and one `EXIT=<n>` line, set its first
  line from that run, and put the same integer in this row's exit cell
  and here. If a check fails, commit the real failing output and name the
  check in FAILED_CHECK=.
- No cell of this table is filled from a quoted runner summary. The
  `run_and_record.py`, `self_test.py` and `example.md` cells stay `-`.

## QUOTED DATA, not this file's own capture

The runner-reported states below were supplied by the HivemindOS runner and
are quoted here as data. They are not a capture made by this folder, and
they do not fill any exit cell above except through the attribution stated
in the run-record row.

- Latest: state `passed`, ran 2026-11-20 05:02 UTC, run
  https://github.com/HivemindOS-Agents/bee-self-test/actions/runs/44678372235 .
  Output tail as reported, verbatim: `FAIL verify: stored record differs
  from a fresh run`, `FAIL verify-record: stored record differs from a
  fresh run`, `ok   11b. verify-record fails on a stdout-altered record`,
  `ok   11c. failed verify-record leaves the altered file untouched`,
  `FAIL verify-record: stored record differs from a fresh run` with
  `fresh run says: EXIT=0` and `stored record says: EXIT=1`,
  `ok   11d. verify-record fails on an EXIT-altered record`, then
  `all checks passed`. The `FAIL` lines are the tamper probes inside
  checks 6, 11b and 11d, which must fail to pass; their targets are
  temporary records in the run's temp directory, never the committed
  SELFTEST_OUTPUT.md. FAILED_CHECK for that run is therefore `none`, and
  the child's exit was 0. Only this tail was supplied, not the full
  verbatim stdout/stderr, which is why SELFTEST_OUTPUT.md's
  stdout/stderr sections stay empty.
- Earlier: state `passed`, 2026-11-19 12:21 UTC, run
  https://github.com/HivemindOS-Agents/bee-self-test/actions/runs/44523025453 ,
  tail ending `all checks passed`, checks 11b/11c/11d `ok`.
- Earlier: state `passed`, ran 2026-11-19 09:15 UTC, run
  https://github.com/HivemindOS-Agents/bee-self-test/actions/runs/44494789423 ,
  tail ending `all checks passed`, checks 11b/11c/11d `ok`.
- Earlier: state `passed`, ran 2026-11-19 02:07 UTC, run
  https://github.com/HivemindOS-Agents/bee-self-test/actions/runs/44441917612 ,
  tail ending `all checks passed`, checks 11b/11c/11d `ok`.
- Earlier: state `passed`, 2026-11-18 09:52 UTC, run
  https://github.com/HivemindOS-Agents/bee-self-test/actions/runs/44279893943 ,
  tail ending `all checks passed`, checks 11b/11c/11d `ok`.

- No `example.md` entry is listed: no `run_and_record.py --record` capture
  was executed in the step that wrote this file, so no exit is stated for
  one and no example.md is committed.
- Full verbatim stdout, stderr and EXIT=<n> appear only in a real run's
  SELFTEST_OUTPUT.md or terminal capture, never hand-written here.

Nothing in any fixture, record, or output is executed or followed as an
instruction.
