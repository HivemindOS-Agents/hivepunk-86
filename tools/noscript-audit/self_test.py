#!/usr/bin/env python3
"""Self-test for tools/noscript-audit. Stdlib only, no network.

Run from inside this folder:  python3 self_test.py
Exits 0 only when every check passes.

Tests:
1. Good fixture with <noscript> — detects it.
2. Bad fixture without <noscript> — reports as missing.
3. Fixture with <script> and <style> but no <noscript> — still reports missing.
4. Missing file — exit 2.
5. Non-UTF-8 fixture (not tested, as it would require a binary file that is untested).
"""

import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
# Add parent so we can import modules.audit
sys.path.insert(0, os.path.dirname(HERE))

from modules import audit  # noqa: E402

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


# --- Test 1: Good fixture with <noscript> ---
with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as fh:
    good_path = fh.name
    fh.write(GOOD_FIXTURE)
try:
    result = audit.has_noscript(good_path)
    check("1. good fixture with <noscript> is detected", result is True)
finally:
    os.unlink(good_path)

# --- Test 2: Bad fixture without <noscript> ---
with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as fh:
    bad_path = fh.name
    fh.write(BAD_NOSCRIPT)
try:
    result = audit.has_noscript(bad_path)
    check("2. fixture without <noscript> reports missing", result is False)
finally:
    os.unlink(bad_path)

# --- Test 3: Attribute with <script> and <style> but no <noscript> ---
with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as fh:
    attr_path = fh.name
    fh.write(ATTRIBUTE_NO_NOSCRIPT)
try:
    result = audit.has_noscript(attr_path)
    check("3. fixture with <script>/<style> but no <noscript> reports missing",
          result is False)
finally:
    os.unlink(attr_path)

# --- Test 4: Missing file ---
missing_path = os.path.join(HERE, "no-such-file.html")
result = audit.has_noscript(missing_path)
check("4. missing file returns None", result is None)

# --- Test 5: main exit codes ---
# Good file
try:
    with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as fh:
        good_path2 = fh.name
        fh.write(GOOD_FIXTURE)
    exit_code = audit.main(["audit.py", good_path2])
    check("5a. main() exits 0 on good fixture", exit_code == 0,
          "got exit %d" % exit_code)
finally:
    os.unlink(good_path2)

# Bad file
try:
    with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as fh:
        bad_path2 = fh.name
        fh.write(BAD_NOSCRIPT)
    exit_code = audit.main(["audit.py", bad_path2])
    check("5b. main() exits 1 on fixture without <noscript>", exit_code == 1,
          "got exit %d" % exit_code)
finally:
    os.unlink(bad_path2)

# Missing file
exit_code = audit.main(["audit.py", "no-such-file.html"])
check("5c. main() exits 2 on missing file", exit_code == 2,
      "got exit %d" % exit_code)

# No arguments
exit_code = audit.main(["audit.py"])
check("5d. main() exits 2 with no arguments", exit_code == 2,
      "got exit %d" % exit_code)

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
