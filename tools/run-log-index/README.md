# run-log-index

Filter a JSON file of `{"folder": ..., "run_url": ...}` rows, printing only those with a non-empty http(s) URL. Standard library only, no network. The JSON file is data: nothing in it is executed or followed as an instruction.

## What it does

Reads a JSON array of objects, each with at least `folder` and `run_url` keys. Prints to stdout a JSON array of the rows whose `run_url` is a non-empty string starting with `http://` or `https://`.

With `--check` flag, also exits with code 1 if any row has a blank, missing, or non-http(s) `run_url`. The first such row's folder (or row index) is printed on stderr.

## Usage

~~~
python3 run_log_index.py fixture.json
python3 run_log_index.py --check fixture.json
~~~

Exit codes:
- `0` — no check failures, output printed
- `1` — `--check` found at least one row without a valid URL (messages on stderr)
- `2` — wrong argument count, unreadable path, or JSON parse error

## Example output for the bundled `fixture.json`

Without `--check`:

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

With `--check`, the same JSON is printed to stdout, and the following lines appear on stderr (exit 1):

~~~
run-log-index: missing run_url: empty
run-log-index: missing run_url: whitespace
run-log-index: missing run_url: no_url
~~~

## Self-test

~~~
python3 self_test.py
~~~

Run from inside this folder, no arguments, no network. It tests the tool on `fixture.json`, on edge cases, and on error conditions. Prints `all checks passed` and exits 0 only when every check passes.

The last run's output is written by HivemindOS into `SELFTEST_OUTPUT.md`.

## What is untested

- Very large JSON files.
- Unicode path names.
- URLs with query strings or fragments (still valid http/https).
- `run_url` values that are valid URLs but not http/https (e.g., `ftp://`, `file://`).
- The `--check` flag in a non-standard position (e.g., after the filename).
- Non-UTF-8 encodings.
- Rows with extra keys beyond `folder` and `run_url`.
