#!/usr/bin/env python3
"""Self‑test for ``issue_fetcher.py``.

The test operates with no network access.  It creates a fixture file
``fixture.json`` containing one pull‑request and two normal issues.  It patches
``urllib.request.urlopen`` so that ``issue_fetcher.fetch_open_issues`` receives
the fixture data.  The test then runs two variants:

* calling the command through the ``main`` function and checking that the
  output contains the two formatted issue lines and nothing else;
* exercising the error paths: wrong number of args, and a fetch failure
  triggered by an ``HTTPError``.

All checks must pass for the test to exit 0.
"""
import json
import os
import sys
import io
import urllib.request

# The fixture will live in the same folder as the test
HERE = os.path.dirname(os.path.abspath(__file__))
FIXTURE_PATH = os.path.join(HERE, "fixture.json")

# Create JSON fixture – two issues and one PR
fixture_data = [
    {
        "title": "Hello world",
        "number": 1,
        "html_url": "https://github.com/owner/repo/issues/1"
    },
    {
        "title": "Second issue",
        "number": 2,
        "html_url": "https://github.com/owner/repo/issues/2"
    },
    {
        "title": "Pull request sample",
        "number": 3,
        "html_url": "https://github.com/owner/repo/pull/3",
        "pull_request": {"url": "https://api.github.com/repos/owner/repo/pulls/3"}
    }
]
with open(FIXTURE_PATH, "w", encoding="utf-8") as f:
    json.dump(fixture_data, f)

# Import the tool – path insertion ensures local import
sys.path.insert(0, os.path.join(HERE, ".."))
from issue_fetcher import fetch_open_issues, main

# --- helper to capture stdout & stderr ---
def capture(func):
    old_stdout, old_stderr = sys.stdout, sys.stderr
    buf_stdout, buf_stderr = io.StringIO(), io.StringIO()
    sys.stdout, sys.stderr = buf_stdout, buf_stderr
    try:
        ret = func()
    finally:
        sys.stdout, sys.stderr = old_stdout, old_stderr
    return ret, buf_stdout.getvalue(), buf_stderr.getvalue()

# --- patch urllib to use fixture ---
class DummyResponse:
    def __init__(self, data):
        self._data = data
        self.status = 200
    def read(self):
        return self._data
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc, tb):
        return False

original_urlopen = urllib.request.urlopen

def fake_urlopen(url):
    with open(FIXTURE_PATH, "rb") as f:
        return DummyResponse(f.read())

urllib.request.urlopen = fake_urlopen

# NOW run tests

failures = []

# 1. Successful run prints two lines
ret, out, err = capture(lambda: main(["owner/repo"]))
exp_lines = [
    "Hello world #1 https://github.com/owner/repo/issues/1",
    "Second issue #2 https://github.com/owner/repo/issues/2"
]
actual_lines = [l for l in out.splitlines() if l.strip()]
if ret != 0:
    failures.append(f"Expected exit 0, got {ret}")
if actual_lines != exp_lines:
    failures.append("Output mismatch")
    failures.append(f"Expected: {exp_lines}")
    failures.append(f"Got: {actual_lines}")

# 2. Wrong number of args
ret, out, err = capture(lambda: main(["a","b"]))
if ret != 1:
    failures.append(f"Bad-args exit {ret}, expected 1")

# 3. Fetch failure – simulate HTTPError

def raise_error(url):
    raise urllib.error.HTTPError(url, 404, "Not found", None, None)

urllib.request.urlopen = raise_error
ret, out, err = capture(lambda: main(["owner/repo"]))
if ret != 2:
    failures.append(f"Fetch error exit {ret}, expected 2")

# Restore original
urllib.request.urlopen = original_urlopen

# Clean fixture
try:
    os.remove(FIXTURE_PATH)
except OSError:
    pass

if failures:
    print("\nFailed tests:", file=sys.stderr)
    for f in failures:
        print(f, file=sys.stderr)
    sys.exit(1)
print("all checks passed")
sys.exit(0)
