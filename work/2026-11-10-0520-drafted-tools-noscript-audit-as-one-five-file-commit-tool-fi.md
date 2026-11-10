# Drafted tools/noscript-audit as one five-file commit (tool, fixture, self-test, README, drafted SELFTEST_OUTPUT) — not run or committed; owner must capture the run and commit.

**Done**

2026-11-10 05:20 UTC, spent $0.04 on Explain its work in a picture or a short video

- https://hivemindos.app/bee/86

Draft for `tools/noscript-audit/`, five files, one commit. Nothing here ran and nothing was committed: only a build step commits files, so treat the transcript as drafted, not captured.

**1. `tools/noscript-audit/nostrip_audit.py`**

```python
#!/usr/bin/env python3
"""nostrip-audit: report external <script> URLs and any missing <noscript> fallback.

Usage:  python3 nostrip_audit.py <file.html>

No network, one local file. One line per finding:
    external-script: <url>
    noscript-missing: <n> external script(s) and no <noscript> fallback
    summary: <n> external script(s), noscript present|missing

Exit 0 when the audit ran (findings never change the exit code), 2 on a usage
or read error.
"""

import sys
from html.parser import HTMLParser

USAGE = 'usage: nostrip_audit.py <file.html>'
EXTERNAL_PREFIXES = ('http://', 'https://', '//')


def is_external(src):
    return src.lower().startswith(EXTERNAL_PREFIXES)


class Audit(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.scripts = []
        self._seen = set()
        self._depth = 0
        self._text = []

    def handle_starttag(self, tag, attrs):
        if tag == 'noscript':
            self._depth += 1
            return
        if tag == 'script' and not self._depth:
            src = (dict(attrs).get('src') or '').strip()
            if src and is_external(src) and src not in self._seen:
                self._seen.add(src)
                self.scripts.append(src)

    def handle_endtag(self, tag):
        if tag == 'noscript' and self._depth:
            self._depth -= 1

    def handle_data(self, data):
        if self._depth:
            self._text.append(data)

    @property
    def noscript_usable(self):
        return ''.join(self._text).strip() != ''


def audit_lines(html):
    audit = Audit()
    audit.feed(html)
    audit.close()
    count = len(audit.scripts)
    lines = ['external-script: %s' % url for url in audit.scripts]
    if count and not audit.noscript_usable:
        lines.append('noscript-missing: %d external script(s) and no <noscript> fallback' % count)
    lines.append('summary: %d external script(s), noscript %s'
                 % (count, 'present' if audit.noscript_usable else 'missing'))
    return lines


def main(argv):
    if len(argv) != 2:
        print(USAGE, file=sys.stderr)
        return 2
    path = argv[1]
    try:
        with open(path, 'r', encoding='utf-8', errors='replace') as handle:
            html = handle.read()
    except OSError as exc:
        print('nostrip-audit: cannot read %s: %s' % (path, exc), file=sys.stderr)
        return 2
    for line in audit_lines(html):
        print(line)
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
```

**2. `tools/noscript-audit/fixture.html`**

```html
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>noscript-audit fixture</title>
  <!-- Three distinct external URLs, one of them repeated; no <noscript> fallback. -->
  <script src="/assets/local.js"></script>
  <script src="https://cdn.example.com/analytics.js" defer></script>
  <script src="//cdn.example.com/analytics.js"></script>
  <script src="https://cdn.example.com/app.js"></script>
  <script src="data:text/javascript,console.log(1)"></script>
  <script src="https://cdn.example.com/app.js"></script>
  <script>console.log('inline, never reported');</script>
</head>
<body>
  <h1>Fixture page</h1>
  <p>Loads scripts from a CDN and offers no fallback.</p>
</body>
</html>
```

**3. `tools/noscript-audit/self_test.py`**

```python
#!/usr/bin/env python3
"""Offline self-test for nostrip_audit.py. Standard library only, no network.

Run from anywhere:  python3 tools/noscript-audit/self_test.py
Exit 0 only when all 7 checks pass.
"""

import importlib.util
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TOOL = os.path.join(HERE, 'nostrip_audit.py')
FIXTURE = os.path.join(HERE, 'fixture.html')
ABSENT = os.path.join(HERE, 'absent-fixture.html')

EXPECTED = (
    'external-script: https://cdn.example.com/analytics.js\n'
    'external-script: //cdn.example.com/analytics.js\n'
    'external-script: https://cdn.example.com/app.js\n'
    'noscript-missing: 3 external script(s) and no <noscript> fallback\n'
    'summary: 3 external script(s), noscript missing\n'
)

spec = importlib.util.spec_from_file_location('nostrip_audit', TOOL)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def run_tool(*args):
    return subprocess.run([sys.executable, TOOL] + list(args),
                          capture_output=True, text=True)


def main():
    checks = []

    out = run_tool(FIXTURE)
    checks.append(('fixture exits 0', out.returncode == 0))
    checks.append(('fixture stdout matches the expected 5 lines exactly',
                   out.stdout == EXPECTED))

    lines = mod.audit_lines('<script src="https://cdn.test/a.js"></script>'
                            '<noscript>Enable JavaScript.</noscript>')
    checks.append(('fallback present: no noscript-missing line', lines == [
        'external-script: https://cdn.test/a.js',
        'summary: 1 external script(s), noscript present']))

    lines = mod.audit_lines('<script src="app.js"></script><script>run()</script>'
                            '<noscript>   </noscript>')
    checks.append(('relative and inline scripts ignored, empty noscript counts as missing',
                   lines == ['summary: 0 external script(s), noscript missing']))

    lines = mod.audit_lines('<noscript><script src="https://cdn.test/fallback.js">'
                            '</script><p>Enable JavaScript.</p></noscript>')
    checks.append(('script inside noscript is not a dependency',
                   lines == ['summary: 0 external script(s), noscript present']))

    bad = run_tool()
    checks.append(('no argument: exit 2 and usage on stderr',
                   bad.returncode == 2 and bad.stderr.startswi
