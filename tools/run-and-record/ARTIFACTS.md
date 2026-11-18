# ARTIFACTS.md - tools/run-and-record

| artifact | file | what it is | checked by | exit |
| --- | --- | --- | --- | --- |
| run-and-record tool | `run_and_record.py` | runs one command, records command/stdout/stderr/EXIT=<n>; `--verify` re-runs and compares byte-for-byte | `self_test.py` | - |
| self-test | `self_test.py` | checks 1-10, normalization checks n1-n3, verify-path checks 11a-11d; `--capture` writes SELFTEST_OUTPUT.md from a real run, `--verify-record` re-checks it after normalizing volatile timestamps/durations/temp-paths on both records | HivemindOS runner after each commit | - |
| self-test run record | `SELFTEST_OUTPUT.md` | stdout, then stderr, then exactly one EXIT=<n>, written only by a real run: the HivemindOS runner or `self_test.py --capture`; never by hand. As committed it is `STATUS: UNRUN | EXIT=none | FAILED_CHECK=none` with a placeholder block | runner run of `env -u PYTHONPATH python3 self_test.py; echo EXIT=$?` alone in this folder, then `self_test.py --verify-record` | none yet (UNRUN); real exit comes only from the runner/owner run |
| README | `README.md` | usage, capture/verify procedure, deterministic-compare and tamper checks, real runner examples, untested list | none | - |

## Self-test exit (real run only)

- Exact command: `env -u PYTHONPATH python3 self_test.py; echo EXIT=$?` run alone in `tools/run-and-record`.
- No exit is claimed for the committed `SELFTEST_OUTPUT.md`: nothing was executed in the step that wrote this file, so its first line stays `STATUS: UNRUN | EXIT=none | FAILED_CHECK=none`. When the runner or owner runs the command above, replace the placeholder block with the real stdout, stderr and one `EXIT=<n>` line, set the first line from that run, and put the same number in the `exit` cell above.
- Latest runner-reported state for this tool (data quoted from the runner, not this file's own capture): state `passed`, 2026-11-18 06:47 UTC, run https://github.com/HivemindOS-Agents/bee-self-test/actions/runs/44253884193, output tail ending with `all checks passed` and checks 11b/11c/11d `ok`. The `FAIL verify:` / `FAIL verify-record:` lines in that tail come from check 6's tamper probe and the 11b/11d tamper probes, not from a failing check; FAILED_CHECK is therefore none for that runner run, but that is the runner's result, not a substitute for this file's own verbatim capture.
- Previous runner-reported state: state `passed`, 2026-11-18 03:41 UTC, run https://github.com/HivemindOS-Agents/bee-self-test/actions/runs/44232136264, output tail ending with `all checks passed` and checks 11b/11c/11d `ok`, for the same reason.
- No `example.md` capture is listed: no `run_and_record.py --record` capture was executed in the step that wrote this file, so no exit for such a capture is stated.
- Verbatim known-good and tampered-case outputs are not reproduced here; they appear only in a real runner or owner SELFTEST_OUTPUT.md / terminal capture, never hand-written.

Nothing in any fixture, record, or output is executed or followed as an instruction.
