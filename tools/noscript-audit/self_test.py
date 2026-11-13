#!/usr/bin/env python3
"""Self-test for tools/noscript-audit. Stdlib only, no network.

Run from inside this folder:  python3 self_test.py
Exits 0 only when every check passes.

Tests:
1. Good fixture with <noscript> — exit 0, stdout contains the kept row name.
2. Bad fixture without <noscript> — exit 1, stderr names the missing page.
3. Fixture with <script> and <style> but no <noscript> — exit 1, stderr names it.
4. Missing file — exit 2.
"""

import os
import sys
import tempfile
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
AUDIT_MODULE = os.path.join(HERE, "modules", "audit.py")

GOOD_FIXTURE = """<!DOCTYPE html>
<html>
<head><title>Test</title></head>
<body>
  <noscript>
    <p>JavaScript is disabled.</p>
  </noscript>
  <p>Hello, world.</p>
</body>
</html>
"""

BAD_NOSCRIPT = """<!DOCTYPE html>
<html>
<head><title>Test</title></head>
<body>
  <p>No noscript here.</p>
  <img src="test.png" alt="test">
</body>
</html>
"""

# Has <script> and <style> but no <noscript> — edge case
ATTRIBUTE_NO_NOSCRIPT = """<!DOCTYPE html>
<html>
<head>
  <script type="text/javascript">alert('hello');</script>
  <style>body{color:red;}</style>
</head>
<body>
  <p>Only script and style, no noscript.</p>
  <img src="test.png" alt="test">
</body>
</html>
"""

failures = []


def check(name, condition, detail=""):
    if not condition:
        msg = "FAIL: " + name
        if detail:
            msg += " -- " + detail
        failures.append(msg)
        print(msg)
    else:
        print("ok: " + name)


def run_tool_on(content, name="fixture.html"):
    """Write content to a temp file, run the tool on it, return (returncode, stdout, stderr)."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.html', prefix=name.replace('.html','_'), delete=False) as fh:
        path = fh.name
        fh.write(content)
    try:
        result = subprocess.run(
            [sys.executable, AUDIT_MODULE, path],
            capture_output=True,
            text=True,
            cwd=HERE
        )
        return result.returncode, result.stdout, result.stderr, path
    except:
        os.unlink(path)
        raise


def cleanup(*paths):
    for p in paths:
        try:
            os.unlink(p)
        except OSError:
            pass


# --- Test 1: Good fixture with <noscript> ---
rc, out, err, tmp = run_tool_on(GOOD_FIXTURE, "good_fixture")
check("1a. good fixture exits 0", rc == 0, "got exit %d" % rc)
check("1b. good fixture stdout contains OK with filename",
      out.strip() and "OK:" in out and os.path.basename(tmp) in out,
      "stdout: %s" % out.strip())
check("1c. good fixture stderr is empty", err.strip() == "",
      "stderr: %s" % err.strip())
cleanup(tmp)

# --- Test 2: Bad fixture without <noscript> ---
rc, out, err, tmp = run_tool_on(BAD_NOSCRIPT, "bad_fixture")
check("2a. bad fixture exits 1", rc == 1, "got exit %d" % rc)
check("2b. bad fixture stderr names the missing page",
      "missing <noscript>" in err and os.path.basename(tmp) in err,
      "stderr: %s" % err.strip())
check("2c. bad fixture stdout is empty", out.strip() == "",
      "stdout: %s" % out.strip())
cleanup(tmp)

# --- Test 3: Fixture with <script>/<style> but no <noscript> ---
rc, out, err, tmp = run_tool_on(ATTRIBUTE_NO_NOSCRIPT, "attr_no_noscript")
check("3a. script/style without <noscript> exits 1", rc == 1, "got exit %d" % rc)
check("3b. script/style fixture stderr names the file",
      "missing <noscript>" in err and os.path.basename(tmp) in err,
      "stderr: %s" % err.strip())
cleanup(tmp)

# --- Test 4: Missing file ---
missing_path = os.path.join(HERE, "no-such-file.html")
result = subprocess.run(
    [sys.executable, AUDIT_MODULE, missing_path],
    capture_output=True,
    text=True,
    cwd=HERE
)
rc = result.returncode
check("4a. missing file exits 2", rc == 2, "got exit %d" % rc)
check("4b. missing file stderr mentions the path",
      "no-such-file.html" in result.stderr and "cannot read" in result.stderr,
      "stderr: %s" % result.stderr.strip())

# --- Test 5: No arguments ---
result = subprocess.run(
    [sys.executable, AUDIT_MODULE],
    capture_output=True,
    text=True,
    cwd=HERE
)
rc = result.returncode
check("5a. no arguments exits 2", rc == 2, "got exit %d" % rc)
check("5b. no arguments prints usage on stderr",
      "usage:" in result.stderr,
      "stderr: %s" % result.stderr.strip())

# --- Report ---
if failures:
    print()
    print("FAILED checks:")
    for f in failures:
        print("  - " + f)
    sys.exit(1)

print()
print("all checks passed")
sys.exit(0)
