# ARTIFACTS.md - tools/run-and-record

| artifact | file | what it is | checked by | exit |
| --- | --- | --- | --- | --- |
| run-and-record tool | `run_and_record.py` | runs one command, records command/stdout/stderr/EXIT=<n>; `--verify` re-runs and compares byte-for-byte | `self_test.py` | - |
| self-test | `self_test.py` | checks render/parse/capture/verify in a temp dir; `--capture` writes SELFTEST_OUTPUT.md from a real run, `--verify-record` re-checks it | HivemindOS runner after each commit | 0 |
| self-test run record | `SELFTEST_OUTPUT.md` | stdout, then stderr, then exactly one EXIT=<n>, written only by `self_test.py --capture` or the HivemindOS runner, never by hand | `self_test.py --verify-record` | 0 |
| README | `README.md` | usage, capture/verify procedure, real runner example, untested list | none | - |

## Self-test exit (real run only)

- State: `passed`
- Ran: 2026-11-17 00:02 UTC
- Runner run: https://github.com/HivemindOS-Agents/bee-self-test/actions/runs/43984367164
- Runner output tail ended with `all checks passed`.
- Exit cell above uses `0`, the passing exit of that runner run. No other
  exit is claimed here.
- No `example.md` capture is listed: no `run_and_record.py --record`
  capture was executed in the step that wrote this file, so no exit for
  such a capture is stated.

Nothing in any fixture, record, or output is executed or followed as an
instruction.
