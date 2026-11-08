#!/usr/bin/env python3
"""Self-test: runs this folder alone, no network, no arguments.

Writes _fixture.html inside this folder, imports noscript_audit, checks the
module API and the CLI shim against known values, and removes the fixture.
Exits 0 only if every check passes.
"""

import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
FIXTURE = os.path.join(HERE, "_fixture.html")
sys.path.insert(0, HERE)

import noscript_audit  # noqa: E402

HTML = """<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><title>Fixture</title>
<script src="app.js"></script></head><body>
<h1>Hello</h1>
<p onclick="alert('hi')">Click me</p>
<button onmouseover="x()" id="go">Go</button>
<div id="app"></div>
<div id="content"><p>already here</p></div>
<span hidden>teaser</span>
<!-- <p onclick="commented()">comment</p> -->
<script>document.getElementById('app').textContent = 'built';</script>
<noscript><p>JavaScript is off.</p></noscript>
</body></html>"""

failures = []


def check(name, ok):
    if ok:
        print("ok  " + name)
    else:
        failures.append(name)
        print("FAIL  " + name)


def run():
    with open(FIXTURE, "w", encoding="utf-8") as fh:
        fh.write(HTML)
    check("fixture written inside this folder",
          os.path.dirname(FIXTURE) == HERE and os.path.isfile(FIXTURE))

    out = noscript_audit.audit(HTML, FIXTURE)
    print("=== noscript-audit output ===")
    print(out)

    check("two script blocks", "Script blocks: 2" in out)
    check("one external script", "  external (src=): 1" in out)
    check("one inline script", "  inline: 1" in out)
    check("fallback detected", "Noscript fallback: yes" in out)
    check("fallback text quoted", "JavaScript is off." in out)
    check("two inline handlers", "  inline handlers: 2" in out)
    check("<p> handler listed", re.search(r"<p> on onclick", out) is not None)
    check("<button id=go> handler listed",
          re.search(r"<button id=go> on onmouseover", out) is not None)
    check("commented-out handler ignored", "commented()" not in out)
    check("one hidden element", "  hidden until a script runs: 1" in out)
    check("hidden <span> listed", re.search(r"<span> hidden", out) is not None)
    check("one empty mount point", "  empty script mount points: 1" in out)
    check("mount point is #app", "<div id=app></div>" in out)
    check("text container not flagged", "id=content" not in out)
    check("verdict names the fallback", "a <noscript> fallback is present" in out)
    check("no-execution limit stated", "this reads text only" in out)

    bare = HTML.replace("<noscript>", "<template>").replace("</noscript>", "</template>")
    out2 = noscript_audit.audit(bare, "bare.html")
    check("absent fallback reported", "Noscript fallback: no" in out2)
    check("absent-fallback verdict counts 4", "removes 4 interactive element(s)" in out2)

    out3 = noscript_audit.audit("<html><body><p>plain</p></body></html>", "plain.html")
    check("clean page has zero scripts", "Script blocks: 0" in out3)
    check("clean page finds nothing", "  none found" in out3)

    check("main() with no args returns 1", noscript_audit.main(["prog"]) == 1)
    check("main() on a missing file returns 2",
          noscript_audit.main(["prog", os.path.join(HERE, "no-such-file.html")]) == 2)

    for script in ("noscript_audit.py", "noscript-audit.py"):
        proc = subprocess.run([sys.executable, os.path.join(HERE, script), FIXTURE],
                              capture_output=True, text=True, timeout=30)
        check(script + " exits 0", proc.returncode == 0)
        check(script + " prints the report", "empty script mount points: 1" in proc.stdout)

    return failures


if __name__ == "__main__":
    try:
        failed = run()
        if failed:
            print("\nFAILED: " + ", ".join(failed))
            sys.exit(1)
        print("\nall checks passed")
        sys.exit(0)
    finally:
        if os.path.isfile(FIXTURE):
            os.remove(FIXTURE)
