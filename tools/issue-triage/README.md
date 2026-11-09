# issue-triage

A tiny helper that lists open issues of a public GitHub repository.

## What it does

* Performs a read‑only GET against the GitHub REST API for
  ``/repos/<owner>/<repo>/issues``.
* Filters out pull‑requests (items that contain a ``pull_request`` key).
* Prints one line per normal issue in the form
  ``<title> #<number> <html_url>``.

The tool is intentionally lightweight – it uses only the Python standard
library and requires no authentication; the public API endpoint validates the
request.

## Usage

```bash
python3 issue_fetcher.py [owner/repo]
```

If *owner/repo* is omitted the default
``HivemindOS-Agents/bee-scouts`` is used.

**Exit codes** – `0` success, `1` usage error, `2` fetch/parse failure.

## Folder‑local self‑test

Run `python3 self_test.py` in this folder.  The test creates a local fixture,
patches `urllib.request.urlopen` to return that fixture data, and verifies:

* output contains exactly the two normal issues and nothing else;
* the pull‑request is filtered out;
* failure paths (too many arguments, fetch error) exit the expected codes.

The test never touches the network and can be run on any machine.

## What is untested

* Network‑real behaviour – the real GitHub API may change the JSON shape.
* Rate‑limiting or authentication errors.
* Handling of pagination beyond 100 items (the script fetches only one page).
