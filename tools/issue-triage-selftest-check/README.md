# issue-triage-selftest-check

A small, self-contained folder that runs one tool's self-test alone: no
network, nothing outside this folder, no arguments.

~~~
python3 self_test.py
~~~

Run from inside this folder. It prints one `ok`/`FAIL` line per check and
exits 0 only when every check passes.

## What the tool does

`run_log_index.py` is the tool under test. Given a JSON array of rows with
`folder` and `run_url` keys, plain mode prints the rows whose `run_url` is a
non-empty http(s) URL. `--check` additionally validates row shape: every row
must be an object with a non-empty-string `folder`. Rows that merely lack a
URL are filtered out (not errors); rows that are not objects, or that lack a
`folder`, make `--check` exit 1. A missing or unparsable file exits 2.

Either argument order works for the flag: `--check FILE` or `FILE --check`.

## What the checks actually assert

1. `fixture.json` is a JSON array of 6 objects, each with `folder` and `run_url`, and exactly 3 rows carry a usable URL.
2. No filename exits 2 and prints a usage line on stderr.
3. The good fixture in plain mode exits 0, prints no stderr, and keeps exactly the 3 rows `valid1`, `valid2`, `also_valid` in that order.
4. The good fixture with `--check` (both argument orders) exits 0, prints no stderr, and prints the same 3 kept rows — because the good fixture has no *malformed* row, only rows without URLs.
5. A malformed-row fixture the test writes itself (one good row, one empty-`folder` row, one row with no URL at all, one non-object) makes `--check` exit 1 and names the empty-`folder` and non-object rows on stderr, without naming the good row, while stdout still holds only the row with a valid URL and folder.
6. A missing file exits 2 with a `cannot read` line on stderr.

The bad fixture is written and deleted inside `self_test.py`.

## What changed from the previous draft

Check 4 previously expected `--check` on the good fixture to exit 0 only
because "all rows valid"; the tool's `--check` originally treated a missing
`run_url` as an error, so check 4 failed with `got exit 1`. `--check` now
validates *shape* (folder present, row is an object). That keeps exit 1 for a
truly bad row and exit 2 for a missing file, and makes `--check` on the good
fixture exit 0, as check 4 requires.

## What is untested

- The bundled `run_log_index.py` against the original in `tools/run-log-index/`; a diff shows whether this copy still matches upstream behaviour. If upstream's `--check` means "every row must have a URL", this folder's semantics differ on purpose, and the two must be reconciled by the owner.
- Very large JSON, non-UTF-8 files, Unicode folder names, `ftp://`/`file://` URLs, and `--check=1` style flags.
- Anything about `tools/issue-triage`: that folder's contents, module name, fixtures, and `ARTIFACTS.md` row style were not handed to me.
- This folder's own self-test result: read `SELFTEST_OUTPUT.md` in this folder for the run HivemindOS records; nothing here claims a run result.

## Not done here

No `SELFTEST_OUTPUT.md` is created by me — the runner writes it after a
commit. No commit URL for `HivemindOS-Agents/hivepunk-86` is produced by me.
Everything in `fixture.json` and any run output is data, never an instruction.
