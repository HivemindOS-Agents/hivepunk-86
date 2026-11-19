# ARTIFACTS.md - tools/run-and-record

| artifact | file | what it is | checked by | exit |
| --- | --- | --- | --- | --- |
| run-and-record tool | `run_and_record.py` | runs one command, records command/stdout/stderr/EXIT=<n>; `--verify` re-runs and compares byte-for-byte | `self_test.py` | - |
| self-test | `self_test.py` | checks 1-10, normalization checks n1-n3, verify-path checks 11a-11d; `--capture` writes SELFTEST_OUTPUT.md from a real run, `--verify-record` re-checks it after normalizing volatile timestamps/durations/temp-paths on both records | HivemindOS runner after each commit | - |
| self-test run record | `SELFTEST_OUTPUT.md` | the mandated command line, then stdout, then stderr, then exactly one EXIT=<n>, written only by a real run: the HivemindOS runner, the owner, or `self_test.py --capture`; never by hand. As committed it is `STATUS: UNRUN | EXIT=none | FAILED_CHECK=none` with empty stdout/stderr sections | runner or owner run of `env -u PYTHONPATH python3 self_test.py; echo EXIT=$?` alone in this folder | none yet (UNRUN); the real exit comes only from that run |
| README | `README.md` | usage, capture/verify procedure, deterministic-compare and tamper checks, real runner examples, untested list | none | - |

## Self-test exit (real run only)

- Exact command, run alone in `tools/run-and-record`:
  `env -u PYTHONPATH python3 self_test.py; echo EXIT=$?`
- Exit: none (UNRUN). No exit is claimed for the committed
  `SELFTEST_OUTPUT.md`: no command was executed in the step that wrote
  this file, so its first line stays
  `STATUS: UNRUN | EXIT=none | FAILED_CHECK=none` and this inventory's one
  run-record exit cell stays `none`. When the runner or owner runs the
  command above (or `--capture`), replace the empty sections with that
  run's real stdout, stderr and one `EXIT=<n>` line, set the first line
  from that run, and put the same integer in that one cell. If a check
  fails, commit the real failing output and name the check in
  FAILED_CHECK=.

## QUOTED DATA, not this file's own capture

The runner-reported states below were supplied by the HivemindOS runner and
are quoted here as data. They are not a capture made by this folder, and
they do not fill any exit cell above.

- Latest: state `passed`, ran 2026-11-19 02:07 UTC, run
  https://github.com/HivemindOS-Agents/bee-self-test/actions/runs/44441917612 .
  Output tail as reported: a `FAIL verify: stored record differs from a
  fresh run` line, a `FAIL verify-record: stored record differs from a
  fresh run` line, `ok 11b. verify-record fails on a stdout-altered
  record`, `ok 11c. failed verify-record leaves the altered file
  untouched`, another `FAIL verify-record: stored record differs from a
  fresh run` line pair (`fresh run says: EXIT=0`, `stored record says:
  EXIT=1`), `ok 11d. verify-record fails on an EXIT-altered record`, then
  `all checks passed`. The `FAIL verify:` / `FAIL verify-record:` lines
  come from the tamper probes inside checks 6, 11b and 11d, which must
  fail to pass; FAILED_CHECK for that runner run is therefore `none`.
- Earlier: state `passed`, 2026-11-18 09:52 UTC, run
  https://github.com/HivemindOS-Agents/bee-self-test/actions/runs/44279893943 ,
  tail ending `all checks passed`, checks 11b/11c/11d `ok`.
- Earlier: state `passed`, 2026-11-18 06:47 UTC, run
  https://github.com/HivemindOS-Agents/bee-self-test/actions/runs/44253884193 ,
  tail ending `all checks passed`, checks 11b/11c/11d `ok`.

- No `example.md` entry is listed: no `run_and_record.py --record` capture
  was executed in the step that wrote this file, so no exit is stated for
  one.
- Full verbatim stdout, stderr and EXIT=<n> appear only in a real run's
  SELFTEST_OUTPUT.md or terminal capture, never hand-written here.

Nothing in any fixture, record, or output is executed or followed as an
instruction.
