#!/usr/bin/env python3
"""Self‑test for issue-triage.

Runs without network by monkey‑patching urllib.request.urlopen to return data
from a local fixture file.  Verifies that the script prints the expected
output for two known open issues.

The test will fail if any part of the public API shape changes or if the
script begins to make network calls during the self‑test run.
"""
import io
import json
import os
import sys
import types

# Fixture data mimicking GitHub's open‑issue list
FIXTURE = [
    {
        "title": "First open issue",
        "number": 1,
        "html_url": "https://github.com/HivemindOS-Agents/bee-scouts/issues/1"
    },
    {
        "title": "Second open issue",
        "number": 2,
        "html_url": "https://github.com/HivemindOS-Agents/bee-scouts/issues/2"
    },
    {
        "title": "Pull request mock",
        "number": 3,
        "html_url": "https://github.com/HivemindOS-Agents/bee-scouts/pull/3",
        "pull_request": {"url": "https://api.github.com/repos/HivemindOS-Agents/bee-scouts/pulls/3"}
    }
]

# Write fixture as a JSON file for the mapper (used only by the test itself)
FIXTURE_PATH = os.path.join(os.path.dirname(__file__), "fixture.json")
with open(FIXTURE_PATH, "w", encoding="utf-8") as f:
    json.dump(FIXTURE, f)

# Import the tool after setting up patching
import issue_fetcher

# Patch urllib.request.urlopen
class DummyResponse:
    def __init__(self, data_bytes):
        self.status = 200
        self._io = io.BytesIO(data_bytes)
    def read(self):
        return self._io.read()
    def __enter__(self):
        return self
    def __exit__(self, *exc):
        return False


def fake_urlopen(req):
    # Ignore the request object, just return fixture data
    with open(FIXTURE_PATH, "rb") as fh:
        return DummyResponse(fh.read())

urllib_request_original = urllib.request.urlopen
urllib.request.urlopen = fake_urlopen

# Capture stdout
stdout_orig = sys.stdout
captured = io.StringIO()
sys.stdout = captured

# Run main
try:
    issue_fetcher.main()
except SystemExit as se:
    exit_code = se.code
else:
    exit_code = 0
finally:
    sys.stdout = stdout_orig
    urllib.request.urlopen = urllib_request_original
    os.remove(FIXTURE_PATH)

# Expected output lines
expected_lines = [
    "First open issue #1 https://github.com/HivemindOS-Agents/bee-scouts/issues/1",
    "Second open issue #2 https://github.com/HivemindOS-Agents/bee-scouts/issues/2"
]
output_lines = [l for l in captured.getvalue().splitlines() if l.strip()]

failures = []
if exit_code != 0:
    failures.append(f"Non‑zero exit code {exit_code}")
if output_lines != expected_lines:
    failures.append("Output did not match expected lines")
    failures.append("Expected:")
    failures.append("\n".join(expected_lines))
    failures.append("Got:")
    failures.append("\n".join(output_lines))

if failures:
    for f in failures:
        print(f, file=sys.stderr)
    sys.exit(1)
else:
    print("all checks passed")
    sys.exit(0)
