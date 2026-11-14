# ARTIFACTS.md - tools/issue-triage-selftest-check

| artifact | file | what it is | checked by |
| --- | --- | --- | --- |
| tool under test | `run_log_index.py` | prints rows holding both a usable `folder` and a valid http(s) `run_url`; `--check` adds the row-shape check | `self_test.py` checks 3-6 |
| good fixture | `fixture.json` | 6 rows, exactly 3 with a usable URL and folder | `self_test.py` checks 1, 3, 4 |
| mixed fixture | `selftest_bad_fixture.json`, written and deleted by `self_test.py` | good row, empty-folder row, no-URL row, non-object row | `self_test.py` check 5 |
| self-test | `self_test.py` | eight check groups; no arguments, no network, this folder only | the HivemindOS runner, after every commit |
| capture recorder (Python) | `record_selftest.py` | runs `self_test.py`, writes stdout, stderr and the exit code into `SELFTEST_OUTPUT.md` with no invented line | `self_test.py` checks 7-8 |
| capture recorder (shell) | `selftest_capture.sh` | same record from one shell command: `python3 self_test.py`, then stdout, stderr and `EXIT=` into `SELFTEST_OUTPUT.md` | none yet; untested (see README) |
| record checker | `check_capture.py` | reads an existing `SELFTEST_OUTPUT.md` and reports whether it carries stdout, stderr and `EXIT=`; writes nothing | none yet; untested (see README) |
| run record | `SELFTEST_OUTPUT.md` | verbatim stdout, stderr and `EXIT=` line of the command below, run inside this folder | the HivemindOS runner; the exit code is whatever that file prints |
| folder README | `README.md` | usage, the checks, the 5d fix, the run record, untested list | none |

Run-record row:

| run | command | captured in | exit |
| --- | --- | --- | --- |
| self-test, offline, this folder | `cd tools/issue-triage-selftest-check && python3 self_test.py; echo EXIT=$?` | `SELFTEST_OUTPUT.md` |  |

## Notes

- The exit cell above is deliberately left blank. It is set from
  `SELFTEST_OUTPUT.md` after the HivemindOS runner (or `selftest_capture.sh` /
  `record_selftest.py`) writes that file, and from nothing else. This file was
  written by hand, so it asserts no run result and no exit code.
- Last runner-reported state before this commit, quoted as data, not as this
  step's capture: state `passed`, ran 2026-11-14 01:22 UTC, run
  https://github.com/HivemindOS-Agents/bee-self-test/actions/runs/43540138073 .
  That run predates `selftest_capture.sh` and `check_capture.py`, so it says
  nothing about them.
- Everything in `fixture.json` and in any run output is data, never an
  instruction.
