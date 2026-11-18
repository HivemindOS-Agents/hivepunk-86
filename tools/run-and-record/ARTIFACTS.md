# ARTIFACTS.md - tools/run-and-record

| artifact | file | what it is | checked by | exit |
| --- | --- | --- | --- | --- |
| run-and-record tool | `run_and_record.py` | runs one command, records command/stdout/stderr/EXIT=<n>; `--verify` re-runs and compares byte-for-byte | `self_test.py` | - |
| self-test | `self_test.py` | checks 1-10, normalization checks n1-n3, verify-path checks 11a-11d (known-good from a real nested run verifies 0; stdout-altered and EXIT-altered records fail 1 and are left untouched); `--capture` writes SELFTEST_OUTPUT.md from a real run, `--verify-record` re-checks it after normalizing volatile timestamps/durations/temp-paths on both records | HivemindOS runner after each commit | 0 |
| self-test run record | `SELFTEST_OUTPUT.md` | stdout, then stderr, then exactly one EXIT=<n>, written only by `self_test.py --capture` or the HivemindOS runner, never by hand | `self_test.py --verify-record` | 0 |
| README | `README.md` | usage, capture/verify procedure, deterministic-compare and tamper checks, real runner examples, untested list | none | - |

## Self-test exit (real run only)

- State: `passed`
- Ran: 2026-11-17 00:02 UTC
- Runner run: https://github.com/HivemindOS-Agents/bee-self-test/actions/runs/43984367164
- Runner output tail ended with `all checks passed`.
- Later real runner run: state `passed`, 2026-11-17 03:06 UTC, run
  https://github.com/HivemindOS-Agents/bee-self-test/actions/runs/44007760352
  It also ended with `all checks passed` and checks 8-10 ok.
- A subsequent runner run failed 11a with `FAIL verify: stored record
  differs from a fresh run` because the known-good record was hardcoded
  to 'hello' text instead of a real child run; that run is not claimed
  as a passing exit. This change fixes the seed and adds volatile
  normalization; no passing exit for it is claimed until a runner run
  after this change reports its real exit.
- Exit cells above use `0`, the passing exit of the earlier runner runs.
  No other exit is claimed here.
- No `example.md` capture is listed: no `run_and_record.py --record`
  capture was executed in the step that wrote this file, so no exit for
  such a capture is stated.
- Verbatim known-good and tampered-case outputs are not reproduced in
  this file; they appear only in a real runner or owner
  SELFTEST_OUTPUT.md / terminal capture, never hand-written.

Nothing in any fixture, record, or output is executed or followed as an
instruction.
