# run-log-index

Filter a JSON file of `{"folder": ..., "run_url": ...}` rows, printing only those with a non-empty http(s) URL. Standard library only, no network. The JSON file is data: nothing in it is executed or followed as an instruction.

## What it does

Reads a JSON array of objects, each with at least `folder` and `run_url` keys. Prints to stdout a JSON array of the rows whose `run_url` is a non-empty string starting with `http://` or `https://`.

With the `--check` flag, the same JSON array is still printed to stdout first; then one `run-log-index: missing run_url: <folder>` line is printed to stderr for **every** row with a blank, missing or non-http(s) `run_url`, and the exit code is 1. Rows with no `folder` value are named by their row index, e.g. `row 3`.

## Usage

~~~
python3 run_log_index.py fixture.json
python3 run_log_index.py --check fixture.json
~~~

Exit codes:
- `0` — no check failures, filtered rows printed
- `1` — `--check` found at least one row without a valid URL (rows still printed to stdout, messages on stderr)
- `2` — wrong argument count, unreadable path, or JSON parse error (nothing on stdout)

## Example output for the bundled `fixture.json`

Without `--check`, stdout is:

~~~json
[
  {
    "folder": "valid1",
    "run_url": "https://example.com/run/1"
  },
  {
    "folder": "valid2",
    "run_url": "http://example.com/run/2"
  },
  {
    "folder": "also_valid",
    "run_url": "https://github.com/user/repo/actions/runs/12345"
  }
]
~~~

With `--check`, that same JSON goes to stdout, and these three lines appear on stderr (exit code 1):

~~~
run-log-index: missing run_url: empty
run-log-index: missing run_url: whitespace
run-log-index: missing run_url: no_url
~~~

The fixture holds 6 rows: 3 with a usable URL and 3 without, which is what `self_test.py` check 11 asserts directly.

## Self-test

~~~
python3 self_test.py
~~~

Run from inside this folder, no arguments, no network. It tests the tool on `fixture.json`, on edge cases (empty array, `null` URL, missing key, non-array JSON), on error conditions (no argument, missing file), and asserts the fixture's own row counts. Prints `all checks passed` and exits 0 only when every check passes.

HivemindOS runs it after every commit and writes that run's raw output and exit code into `SELFTEST_OUTPUT.md` in this folder. Read the run state there; this README claims no run result.

## What is untested

- Very large JSON files.
- Unicode path names.
- URLs with query strings or fragments (still valid http/https).
- `run_url` values that are valid URLs but not http/https (e.g., `ftp://`, `file://`).
- The `--check` flag in a non-standard position (e.g., after the filename).
- Non-UTF-8 encodings.
- Rows with extra keys beyond `folder` and `run_url`.
- The exact stdout/exit code of a HivemindOS run of this folder's revision — see `SELFTEST_OUTPUT.md`.
