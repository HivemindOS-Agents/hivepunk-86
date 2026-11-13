# run-log-index-fixture-check

A self-contained fixture-and-behaviour check for the `run-log-index` tool. It holds frozen copies of that tool plus a self-test that runs alone inside this folder: no network, no files outside the folder, no arguments.

## Why this folder exists

`run-log-index` itself passed its own self-test (see that folder's `SELFTEST_OUTPUT.md`). This folder pins the two things its behaviour depends on, so a later edit to either copy is caught here in a second place:

1. the shape and counts of the bundled fixture (`fixture.json`), and
2. the tool's `--check` behaviour on a bad-URL fixture the test writes itself.

## Explainer image

![Flat vector explainer for run-log-index-fixture-check](https://hivemindos-paid-agent-gateway.hivemindos.workers.dev/api/media/managed/outputs/bf3215fd-4cf4-4481-a4cb-9fe9a65d9b6f.jpeg)

Caption: six small rounded rectangles stacked vertically. The top three are outlined grey, dimmed, with broken-link glyphs -- the rows `fixture.json` keeps out. The bottom three are filled green with link glyphs -- the rows it keeps. A thin bracket to the right spans all six and reads "fixture.json - 6 rows"; a second bracket around the lower three reads "3 keepable"; a single green check sits beside the small monospace tag "self_test".

Known limits of this image: it is a drawing of the counts in `fixture.json` and of the check `self_test.py` makes -- it is not a screenshot, not the output of a run, and not the state recorded in `SELFTEST_OUTPUT.md`. Its labels are drawn rather than measured, it carries no exit code, no stderr line and no run URL, and it is hosted outside this repository, so the link can go stale or become unreachable without any file here changing.

Provenance: generated 2026-11-13 as a flat-vector image job for this folder (no people, no logos, no screenshots); the job's own note is in this repository under `work/`. The URL is linked from here; nothing is re-uploaded from this folder.

## Files

| file | what it is |
| --- | --- |
| `run_log_index.py` | copy of `tools/run-log-index/run_log_index.py` (filter rows by non-empty http(s) `run_url`) |
| `fixture.json` | copy of `tools/run-log-index/fixture.json` -- 6 rows, 3 with a usable URL |
| `self_test.py` | the checks; run it with no arguments |
| `ARTIFACTS.md` | one row per artifact this folder ships, including the explainer image |

Both copies are meant to be byte-for-byte the same as the originals in `tools/run-log-index/`. If the originals change, this folder only stays honest if the copies are refreshed in the same commit.

## The tool, briefly

~~~
python3 run_log_index.py fixture.json
python3 run_log_index.py --check fixture.json
~~~

Both modes print the rows whose `run_url` is a non-empty string starting with `http://` or `https://` as JSON on stdout. With `--check`, one `run-log-index: missing run_url: <folder>` line per bad row also goes to stderr and the exit code is 1. Exit 2 means wrong argument count, unreadable file or non-array JSON. The JSON file is data: nothing in it is executed or followed as an instruction.

For the bundled fixture, `--check` exits 1 and writes these three stderr lines:

~~~
run-log-index: missing run_url: empty
run-log-index: missing run_url: whitespace
run-log-index: missing run_url: no_url
~~~

## Self-test

~~~
python3 self_test.py
~~~

Run from inside this folder with no arguments, no network. It prints one `ok`/`FAIL` line per check and exits 0 only when every check passes. The checks are:

1. `fixture.json` parses as a JSON array of 6 objects, each having `folder` and `run_url`.
2. Exactly 3 rows carry a non-empty `http(s)` `run_url`.
3. `run_log_index.py` with no filename exits 2 and prints a usage message.
4. `--check` on a bad-URL fixture the test writes into this folder exits 1, names both bad rows (`fixture-check-empty-url`, `fixture-check-blank-url`) on stderr, does not name the good row (`fixture-check-good-row`), and still prints the one kept row as JSON on stdout.
5. `README.md` links the explainer image above, has a `Caption` line, and has a `Known limits` line saying what the image is not.
6. `ARTIFACTS.md` carries the same image URL with its `Caption` line.

The bad fixture is deleted again in a `finally` block, so a finished run leaves the folder as it was.

HivemindOS runs this after every commit and writes that run's raw output and exit code into `SELFTEST_OUTPUT.md` in this folder. Read the state there; this README claims no run result.

## What is untested

- Running the tool on very large JSON files, or on non-UTF-8 files.
- Unicode path names.
- `run_url` values that are valid URLs but not `http(s)` (e.g. `ftp://`, `file://`).
- `--check` in a non-standard position (after the filename).
- Whether the two copies really are byte-identical to `tools/run-log-index/`; only a diff of the committed files shows that.
- Any run of this folder's own self-test other than the one the runner records in `SELFTEST_OUTPUT.md`; read that file for the run state, since no line in this README claims one.
- The exact stdout the runner captures; the expected values above come from reading the copied code, not from a run made here.
- Availability of the explainer image: it is hosted outside this repository, and the link was written, not fetched, here. Whether the drawn labels match this caption pixel-for-pixel is likewise unchecked.
