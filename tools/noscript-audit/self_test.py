#!/usr/bin/env python3
"""Self‑test for noscript‑audit.

The test writes a small HTML fixture into the current folder, imports the
``noscript_audit`` module (the importable implementation), and runs a series
of sanity checks against the audit output.  It also invokes the CLI shim
``noscript-audit.py`` to ensure the command line entry point behaves
identically.  The test cleans up the fixture after it finishes.

The tests are intentionally minimal but touch all public features of the
module – script counting, `<noscript>` detection, hidden attributes, and
interactive elements.  A failure in any check causes the test to exit with
status 1.
"""

import os
import re
import sys
from pathlib import Path

HERE = Path(__file__).parent
FIXTURE_PATH = HERE / "_fixture.html"

# Ensure the import path points to the current directory.
sys.path.insert(0, str(HERE))

import noscript_audit

FIXTURE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Fixture</title>
  <script src="app.js"></script>
</head>
<body>
  <h1>Hello</h1>
  <p onclick="alert('hi')">Click me</p>
  <button onmouseover="x()" id="go">Go</button>
  <div id="app"></div>
  <div id="content"><p>already here</p></div>
  <span hidden>teaser</span>
  <!-- <p onclick="commented()">comment</p> -->
  <script>
    document.getElementById('app').textContent = 'built by JS';
  </script>
  <noscript>
    <p>JavaScript is off.</p>
  </noscript>
</body>
</html>"""

failures = []


def check(name: str, got, want):
    if got != want:
        failures.append(f"{name}: got {got!r}, expected {want!r}")
    else:
        print("ok", name)


def main():
    # Write fixture to disk.
    with open(FIXTURE_PATH, "w", encoding="utf-8") as fh:
        fh.write(FIXTURE)

    # Import freshly written module.
    mod = noscript_audit

    # Audit result.
    out = mod.audit(FIXTURE, str(FIXTURE_PATH))
    print("=== noscript-audit output ===")
    print(out)

    # Verify fixture persisted.
    with open(FIXTURE_PATH, "r", encoding="utf-8") as fh:
        written = fh.read()
    check("fixture written in the tool's own folder", written, FIXTURE)

    # Basic audit expectations.
    check("two script blocks counted", "Script blocks: 2" in out, True)
    check("one external script", "  external (src=): 1" in out, True)
    check("one inline script", "  inline: 1" in out, True)
    check("noscript fallback detected", "Noscript fallback: yes" in out, True)
    check("noscript text quoted", "JavaScript is off." in out, True)

    check("two inline-handler elements", "  inline handlers: 2" in out, True)
    check("<p> handler listed", re.search(r"<p> on onclick", out) is not None, True)
    check("<button id=go> handler listed", re.search(r"<button id=go> on onmouseover", out) is not None, True)
    check("commented-out handler ignored", "commented" not in out, True)

    check("hidden element found", "  hidden until a script runs: 1" in out, True)
    check("hidden <span> listed", re.search(r"<span> hidden", out) is not None, True)

    check("only the empty container is a mount point", "  empty script mount points: 1" in out, True)
    check("mount point is #app", "<div id=app></div>" in out, True)
    check("container holding text is not flagged", "id=content" not in out, True)

    check("verdict names the fallback", "a <noscript> fallback is present" in out, True)
    check("note states the no-execution limit", "this reads text only" in out, True)

    # The same HTML without a <noscript>.
    bare = FIXTURE.replace("<noscript>", "<template>").replace("</noscript>", "</template>")
    out2 = mod.audit(bare, "bare.html")
    check("no fallback reported when absent", "Noscript fallback: no" in out2, True)
    check("verdict warns when absent", "removes 4 interactive element(s)" in out2, True)

    # Completely clean page.
    out3 = mod.audit("<html><body><p>plain</p></body></html>", "plain.html")
    check("clean page: zero scripts", "Script blocks: 0" in out3, True)
    check("clean page: no findings", "  none found" in out3, True)

    # Verify CLI shim works identically.
    cli_out = os.popen(f"{sys.executable} {HERE/'noscript-audit.py'} {FIXTURE_PATH}").read()
    if cli_out.strip() != out.strip():
        failures.append("CLI output differs from module output")

    if failures:
        print("\nFAILED:")
        for line in failures:
            print("  " + line)
        return 1
    print("\nall checks passed")
    return 0


if __name__ == "__main__":
    try:
        exit_code = main()
    finally:
        if FIXTURE_PATH.exists():
            FIXTURE_PATH.unlink()
    sys.exit(exit_code)
