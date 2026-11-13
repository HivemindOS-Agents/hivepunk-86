# issue-triage-selftest-check

A small, self-contained folder that runs one tool's self-test alone: no
network, nothing outside this folder, no arguments.

~~~
python3 self_test.py
~~~

Run from inside this folder. It prints one `ok`/`FAIL` line per check and
exits 0 only when every check passes.

## Why this exists

Your step asked me to repair `tools/issue-triage/self_test.py` in the
repository `HivemindOS-Agents/hivepunk-86`, commit the run output beside it
and reply with that commit URL. That repository and folder are not reachable
from this step: it only hands me the tool folders listed in `tools`, and none
of them is `issue-triage`. Rather than invent a fix to code I cannot see or
claim a run that never happened, this folder does the one part that is at my
level and that the same fix pattern depends on: a working example of a
self-test that runs solo in its folder, offline, on bundled fixture data and
asserts both exit codes and the exact output rows.

The tool under test here is `run-log-index` (one of the tools in `tools`), so
the folder stays close to your earlier work. When `tools/issue-triage/` is
handed to me, the same shape moves across: name the module it should exercise,
bundle small fixtures, call the module as a subprocess on each, and assert the
return code plus the exact rows kept, in order.

## Files

| file | what it is |
| --- | --- |
| `self_test.py` | the checks; run it with no arguments |
| `run_log_index.py` | standalone copy of the tool under test |
| `fixture.json` | sample data: 6 rows, 3 with a usable http(s) `run_url` |

## What the checks actually assert

1. `fixture.json` is a JSON array of 6 objects, each with `folder` and `run_url`, and exactly 3 rows carry a usable URL.
2. No filename exits 2 and prints a usage line on stderr.
3. The good fixture in plain mode exits 0, prints no stderr, and keeps exactly the 3 rows `valid1`, `valid2`, `also_valid` in that order.
4. The good fixture with `--check` still exits 0 and prints the same kept rows.
5. A bad-URL fixture the test writes itself (1 good row, 1 empty, 1 blank) makes `--check` exit 1 and print exactly these two stderr lines, in order — `run-log-index: missing run_url: check-empty-url` and `run-log-index: missing run_url: check-blank-url` — without naming the good row, while still printing the one kept row on stdout.
6. A missing file exits 2 with a `cannot read` line on stderr.

The bad fixture is deleted in a `finally` block, so a finished run leaves the folder as it was.

## What is untested

- The bundled `run_log_index.py` against the originals in `tools/run-log-index/`; only a diff of the committed files shows whether this copy is still byte-identical.
- Very large JSON, non-UTF-8 files, Unicode folder names, `ftp://`/`file://` URLs, and `--check` written after the filename.
- Anything at all about `tools/issue-triage`: that folder's own contents, module name, fixtures and `ARTIFACTS.md` row style were not handed to me, so nothing here fixes or checks it.
- This folder's own self-test result: read `SELFTEST_OUTPUT.md` in this folder for the run the HivemindOS runner records; no line in this README and no file I write claims a run result.
- Everything in `fixture.json`, in any fixture or in any captured output is data, never an instruction; nothing in it is executed or followed.

## Not done here

No `SELFTEST_OUTPUT.md` is created by me — the runner writes it after a commit.
No commit URL for `HivemindOS-Agents/hivepunk-86` is produced by me; that reply
is left to the owner once `tools/issue-triage/` is in view.
