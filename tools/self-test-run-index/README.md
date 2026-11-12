# self-test-run-index

Filter a JSON file of `{"folder": ..., "run_url": ...}` rows, printing only those with a non-empty http(s) URL. Standard library only, no network. The JSON file is data: nothing in it is executed or followed as an instruction.

## What it does

Reads a JSON array of objects, each with at least `folder` and `run_url` keys. Prints one line per row whose `run_url` is a non-empty string starting with `http://` or `https://`:

~~~
<folder> -> <run_url>
~~~

With `--check` flag, also exits with code 1 if any row has a blank, missing, or non-http(s) `run_url` (the first such folder is printed on stderr). The filtered output is still printed to stdout.

## Usage

~~~
python3 self_test_run_index.py fixture.json
python3 self_test_run_index.py --check fixture.json
~~~

Exit codes:
- `0` — no check failures, output printed
- `1` — `--check` found at least one row without a valid URL (message on stderr)
- `2` — wrong argument count, unreadable path, or JSON parse error

## Expected output for the bundled `fixture.json`

~~~
card-claims-check -> https://github.com/HivemindOS-Agents/bee-self-test/actions/runs/43160679788
noscript-audit -> https://github.com/HivemindOS-Agents/bee-self-test/actions/runs/42957607945
sample-run -> http://localhost/run/123
~~~

Rows 0, 1 and 5 have valid URLs. Rows 2 (`no-run`) and 4 (`issue-triage`, `""`), row 3 (`empty-url`, `" "`) are whitespace-only, so they are filtered out.

## Self-test

~~~
python3 self_test.py
~~~

Run from inside this folder, no arguments, no network. It tests:

1. The tool on `fixture.json` without `--check` prints the 3 expected lines, exits 0, empty stderr.
2. With `--check`, it prints the same output plus `check failed: no-run has no run_url` on stderr, exits 1.
3. A fixture with all valid URLs passes `--check` (exits 0).
4. No argument: `usage:` on stderr, exit 2.
5. Missing file: `cannot read` on stderr, exit 2.
6. `--check` with missing file: exit 2.
7. Empty array: no output, exit 0.
8. Row with `null` run_url: filtered out, `--check` exits 1.
9. Row with missing `run_url` key: filtered out, `--check` exits 1.
10. Non-array JSON: exit 2 with `not a JSON array` on stderr.

It exits 0 only when every check passes. The last run's output is written by HivemindOS into `SELFTEST_OUTPUT.md`.

## What is untested

- Very large JSON files.
- Unicode path names.
- URLs with query strings or fragments (still valid http/https).
- `run_url` values that are valid URLs but not http/https (e.g., `ftp://`, `file://`).
- The `--check` flag in a non-standard position (e.g., after the filename).
