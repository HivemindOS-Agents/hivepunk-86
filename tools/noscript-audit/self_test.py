#!/usr/bin/env python3
"""Self-test for noscript-audit. Writes its fixture inside its own folder,
imports the tool's own code, compares output with expected values, and exits 0
only when every check passes. No arguments, no network.
"""

import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
FIXTURE_PATH = os.path.join(HERE, "_fixture.html")

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


def check(name, got, want):
    if got != want:
        failures.append("%s: got %r, expected %r" % (name, got, want))
    else:
        print("ok  " + name)


def main():
    sys.path.insert(0, HERE)
    with open(FIXTURE_PATH, "w", encoding="utf-8") as handle:
        handle.write(FIXTURE)

    import importlib
    module = importlib.import_module("noscript_audit")
    out = module.audit(FIXTURE, FIXTURE_PATH)
    print("=== noscript-audit output ===")
    print(out)
    print("=== end output ===")

    with open(FIXTURE_PATH, "r", encoding="utf-8") as handle:
        written = handle.read()
    check("fixture written in the tool's own folder", written, FIXTURE)

    check("two script blocks counted", "Script blocks: 2" in out, True)
    check("one external script", "external (src=): 1" in out, True)
    check("one inline script", "inline: 1" in out, True)
    check("noscript fallback detected", "Noscript fallback: yes" in out, True)
    check("noscript text quoted", "JavaScript is off." in out, True)

    check("two inline-handler elements", "inline handlers: 2" in out, True)
    check("<p> handler listed", re.search(r"<p> on onclick", out), True)
    check("<button id=go> handler listed", re.search(r"<button id=go> on onmouseover", out), True)
    check("commented-out handler ignored", "commented" in out, False)

    check("hidden element found", "hidden until a script runs: 1" in out, True)
    check("hidden <span> listed", re.search(r"<span> hidden", out), True)
    check("only the empty container is a mount point",
          "empty script mount points: 1" in out, True)
    check("mount point is #app", "<div id=app></div>" in out, True)
    check("container holding text is not flagged", "id=content" in out, False)
    check("verdict names the fallback", "a <noscript> fallback is present" in out, True)
    check("note states the no-execution limit",
          "reads text only" in out, True)

    # The same HTML with the fallback removed must flip both findings.
    bare = FIXTURE.replace("<noscript>", "<template>").replace("</noscript>", "</template>")
    out2 = module.audit(bare, "bare.html")
    check("no fallback reported when absent", "Noscript fallback: no" in out2, True)
    check("verdict warns when absent",
          "removes 4 interactive element(s) and no <noscript> fallback" in out2, True)

    # A page that is already complete without scripting must come back clean.
    out3 = module.audit("<html><body><p>plain</p></body></html>", "plain.html")
    check("clean page: zero scripts", "Script blocks: 0" in out3, True)
    check("clean page: no findings", "  none found" in out3, True)

    if failures:
        print("\nFAILED:")
        for line in failures:
            print("  " + line)
        return 1
    print("\nall checks passed")
    return 0


if __name__ == "__main__":
    code = main()
    if os.path.exists(FIXTURE_PATH):
        os.remove(FIXTURE_PATH)
    sys.exit(code)
