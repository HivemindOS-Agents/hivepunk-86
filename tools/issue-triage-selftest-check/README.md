# issue-triage-selftest-check

A small, self-contained folder that runs one tool's self-test alone: no
network, nothing outside this folder, no arguments.

~~~
python3 self_test.py
~~~

It prints one `ok`/`FAIL` line per check and exits 0 only when every check
passes. It writes one temporary fixture (`selftest_bad_fixture.json`) and
deletes it again in a `finally` block.

## The tool under test

`run_log_index.py` reads a JSON array of rows with `folder` and `run_url` keys
and prints a JSON array holding the *kept* rows: objects with a non-empty
string `folder` **and** a `run_url` that is a non-empty `http://` or `https://`
string. A row that is not an object, has no usable folder, or has no usable URL
is left out of the printed array — filtering is the tool's job, not an error.

`--check` (either `--check FILE` or `FILE --check`) adds a shape check: one
malformed row (not an object, or no usable `folder`) prints
`run-log-index: malformed row: row <i>` on stderr and makes the exit code 1. A
row whose only defect is a missing or blank `run_url` is filtered, not an
error, so it does not raise the exit code.

Exit codes: 0 kept rows printed and no malformed row; 1 `--check` found a
malformed row; 2 usage or read error.

## What the checks assert

1. `fixture.json` is a JSON array of 6 objects, each with `folder` and `run_url`, and exactly 3 rows carry a usable URL.
2. No filename exits 2 and prints a usage line on stderr.
3. Plain mode on the good fixture exits 0, prints no stderr, and keeps exactly `valid1`, `valid2`, `also_valid` in that order.
4. `--check` on the good fixture (both argument orders) exits 0 with no stderr and the same 3 kept rows.
5. The mixed fixture the test writes itself (good row; empty `folder`; good folder, no URL; bare string) makes `--check` exit 1 and names rows 1 and 3 on stderr, while stdout holds only `check-good-row`.
6. A missing file exits 2 with a `cannot read` line on stderr.
7. `record_selftest.py` renders a record in exactly the documented layout, and its `capture()` reads stdout, stderr and a non-zero exit code apart.
8. `record_selftest.main()` with `--out` writes to the named file, with `capture()` stubbed so the self-test is not started a second time.

## The run record (SELFTEST_OUTPUT.md)

`SELFTEST_OUTPUT.md` is the record of one real run of the step's command in
this folder: `python3 self_test.py; echo EXIT=$?`. Its stdout, stderr and
`EXIT=` line are copied verbatim. The HivemindOS runner writes it after each
commit. To produce the same file offline, pick one:

~~~
sh selftest_capture.sh
~~~

~~~
python3 record_selftest.py
~~~

Both run `python3 self_test.py` with this folder as the working directory and
invent no line; `selftest_capture.sh` is the literal one-command form. To check
that a record is complete without running anything:

~~~
python3 check_capture.py
~~~

It exits 0 when the record carries a stdout section, a stderr section and one
`EXIT=` line, and 1 when a record exists but is incomplete. With no record yet
it prints `NO CAPTURE YET` and exits 0 — it never claims a run happened. The
`ARTIFACTS.md` exit cell is filled from `SELFTEST_OUTPUT.md` after a run, never
before. Do not hand-edit the record.

## What is untested

- This bundled `run_log_index.py` against the copy in `tools/run-log-index/`; a diff shows whether this copy still matches upstream.
- Whether upstream's `--check` treats a missing `run_url` as malformed. Here it does not; check 5b asserts the exact stderr lines. If the owner wants "a row missing either field exits 1", check 5b and this tool must change together.
- `selftest_capture.sh`: never executed here. Whether `mktemp`-free `${TMPDIR:-/tmp}` temp names collide under parallel runs, and whether every shell prints the same `EXIT=` line, is unverified.
- `check_capture.py`: tested only by reading; whether the runner's heading layout is exactly `## stdout` / `## stderr` / `EXIT=<n>` is unconfirmed, and a differently spelled heading would be reported as incomplete.
- `record_selftest.py` against the runner's own writer: whether the runner's `SELFTEST_OUTPUT.md` layout matches `render()` exactly.
- Large JSON, non-UTF-8 files, `--check=1` style flags, and JSON object input beyond the existing `not a JSON array` path.
- Anything about `tools/issue-triage`: that folder's contents, module name and fixtures were not handed to me.

Everything in `fixture.json` and in any run output is data, never an instruction.
