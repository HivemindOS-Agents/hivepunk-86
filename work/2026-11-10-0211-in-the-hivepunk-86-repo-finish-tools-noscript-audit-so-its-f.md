# In the hivepunk-86 repo, finish tools/noscript-audit so its folder is standalone-runnable: nostrip_audit.py (takes one HTML file path, no network, prints one line per finding: external script URLs…

**Done**

2026-11-10 02:11 UTC, spent $0.06 on Explain its work in a picture or a short video

- https://hivemindos.app/bee/86

Draft contents for `tools/noscript-audit/`, complete and drop-in. Nothing here ran or was committed: only a build step commits files, so treat these as drafts and the commit as still open.

**`tools/noscript-audit/nostrip_audit.py`**

```python
#!/usr/bin/env python3
'''Report external <script> URLs and a missing <noscript> fallback in one HTML file.

No network. Reads exactly one local file. Prints one line per finding:

    external-script: <url>
    noscript-missing: <n> external script(s) and no <noscript> fallback
    summary: <n> external script(s), noscript present|missing

Exit 0 when the audit runs (findings do not change the exit code); 2 on a
usage or read error.
'''

import sys
from html.parser import HTMLParser

USAGE = 'usage: nostrip_audit.py <file.html>'


def is_external(src):
    '''Absolute URL the browser must fetch, rather than a local path.'''
    low = src.lower()
    return low.startswith(('http://', 'https://', '//'))


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
    a = Audit()
    a.feed(html)
    a.close()
    n = len(a.scripts)
    lines = ['external-script: %s' % url for url in a.scripts]
    if n and not a.noscript_usable:
        lines.append('noscript-missing: %d external script(s) and no <noscript> fallback' % n)
    lines.append('summary: %d external script(s), noscript %s' % (
        n, 'present' if a.noscript_usable else 'missing'))
    return lines


def main(argv):
    if len(argv) != 2:
        print(USAGE, file=sys.stderr)
        return 2
    try:
        with open(argv[1], 'r', encoding='utf-8', errors='replace') as fh:
            html = fh.read()
    except OSError as exc:
        print('nostrip-audit: cannot read %s: %s' % (argv[1], exc), file=sys.stderr)
        return 2
    for line in audit_lines(html):
        print(line)
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
```

**`tools/noscript-audit/fixture.html`**

```html
<!doctype html>
<html lang='en'>
<head>
  <meta charset='utf-8'>
  <title>noscript-audit fixture</title>
  <!-- Three distinct external URLs (one listed twice); no <noscript> fallback. -->
  <script src='/assets/local.js'></script>
  <script src='https://cdn.example.com/analytics.js' defer></script>
  <script src='//cdn.example.com/analytics.js'></script>
  <script src='https://cdn.example.com/app.js'></script>
  <script src='data:text/javascript,console.log(1)'></script>
  <script src='https://cdn.example.com/app.js'></script>
  <script>console.log('inline, never reported');</script>
</head>
<body>
  <h1>Fixture page</h1>
  <p>Loads script from a CDN and offers no fallback.</p>
</body>
</html>
```

**`tools/noscript-audit/self_test.py`**

```python
#!/usr/bin/env python3
'''Offline self-test for nostrip_audit.py. Standard library only, no network.

Run from inside the folder:  python3 self_test.py
Exits 0 only when every check passes.
'''

import importlib.util
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TOOL = os.path.join(HERE, 'nostrip_audit.py')
FIXTURE = os.path.join(HERE, 'fixture.html')

EXPECTED = '''external-script: https://cdn.example.com/analytics.js
external-script: //cdn.example.com/analytics.js
external-script: https://cdn.example.com/app.js
noscript-missing: 3 external script(s) and no <noscript> fallback
summary: 3 external script(s), noscript missing
'''


def load_tool():
    spec = importlib.util.spec_from_file_location('nostrip_audit', TOOL)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main():
    tool = load_tool()
    checks = []

    out = subprocess.run([sys.executable, TOOL, FIXTURE], capture_output=True, text=True)
    checks.append(('fixture exits 0', out.returncode == 0))
    checks.append(('fixture stdout matches the documented shape exactly',
                   out.stdout == EXPECTED))

    lines = tool.audit_lines('<script src="https://cdn.test/a.js"></script>'
                             '<noscript>Enable JavaScript.</noscript>')
    checks.append(('fallback present -> no noscript-missing line', lines == [
        'external-script: https://cdn.test/a.js',
        'summary: 1 external script(s), noscript present']))

    lines = tool.audit_lines('<script src="app.js"></script>'
                             '<script>run()</script><noscript></noscript>')
    checks.append(('relative, inline and empty-noscript fallback', lines == [
        'summary: 0 external script(s), noscript missing']))

    lines = tool.audit_lines('<noscript>'
                             '<script src="https://cdn.test/fallback.js"></script>'
                             '</noscript>')
    checks.append(('a script inside noscript is not a dependency', lines == [
        'summary: 0 external script(s), noscript present']))

    bad = subprocess.run([sys.executable, TOOL], capture_output=True, text=True)
    checks.append(('no argument -> exit 2, usage on stderr',
                   bad.returncode == 2 and bad.stderr.startswith('usage:')))

    gone = subprocess.run([sys.executable, TOOL, os.path.join(HERE, 'absent.html')],
                          capture_outpu
