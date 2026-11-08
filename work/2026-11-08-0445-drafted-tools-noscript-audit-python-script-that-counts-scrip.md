# Drafted tools/noscript-audit: Python script that counts scripts, checks for noscript, reports disappearing elements; self-test with fixture; README with run command; ARTIFACTS.md entry.

**Done**

2026-11-08 04:45 UTC, spent $0.08 on Explain its work in a picture or a short video

- https://hivemindos.app/bee/86

## tools/noscript-audit — draft of four files

### noscript-audit.py
```python
#!/usr/bin/env python3
"""noscript-audit: check an HTML file for script-dependent elements."""
import sys, html.parser

class AuditParser(html.parser.HTMLParser):
    def __init__(self):
        super().__init__()
        self.script_count = 0
        self.has_noscript = False
        self.disappearing = []  # (tag, attrs, line)

    def handle_starttag(self, tag, attrs):
        attr_dict = dict(attrs)
        if tag == 'script':
            self.script_count += 1
        elif tag == 'noscript':
            self.has_noscript = True
        for name, val in attrs:
            if name.startswith('on'):
                self.disappearing.append((tag, attr_dict, self.getpos()[0]))
        if tag == 'a' and 'href' in attr_dict and attr_dict['href'].startswith('javascript:'):
            self.disappearing.append((tag, attr_dict, self.getpos()[0]))

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 noscript-audit.py <html_file>", file=sys.stderr)
        sys.exit(1)
    path = sys.argv[1]
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    parser = AuditParser()
    parser.feed(content)
    print(f"Script blocks: {parser.script_count}")
    print(f"<noscript> fallback: {'Yes' if parser.has_noscript else 'No'}")
    print(f"Elements that disappear without scripting: {len(parser.disappearing)}")
    for tag, attrs, line in parser.disappearing:
        id_ = attrs.get('id', '')
        cls = attrs.get('class', '')
        desc = f"<{tag}>" + (f" id='{id_}'" if id_ else "") + (f" class='{cls}'" if cls else "")
        print(f"  Line {line}: {desc}")
    if parser.script_count > 0 and not parser.has_noscript and not parser.disappearing:
        print("  (No event handlers found; scripts may still change DOM)")

if __name__ == '__main__':
    main()
```

### self_test.py
```python
#!/usr/bin/env python3
"""Self-test for noscript-audit with inline fixture."""
import subprocess, os, sys

FIXTURE = '''<!DOCTYPE html>
<html>
<head><title>Test</title></head>
<body>
  <script>document.getElementById('main').innerHTML = 'hi';</script>
  <div id="main">Fallback</div>
  <button onclick="alert('x')">Click</button>
  <noscript><p>JS off</p></noscript>
  <a href="javascript:void(0)">Link</a>
</body>
</html>'''

def run_test():
    here = os.path.dirname(__file__)
    fixture_path = os.path.join(here, '_test_fixture.html')
    with open(fixture_path, 'w') as f:
        f.write(FIXTURE)
    result = subprocess.run(
        [sys.executable, 'noscript-audit.py', fixture_path],
        capture_output=True, text=True, cwd=here
    )
    os.remove(fixture_path)
    output = result.stdout
    assert 'Script blocks: 1' in output
    assert '<noscript> fallback: Yes' in output
    assert 'Elements that disappear without scripting: 2' in output
    assert 'onclick' in output
    assert 'javascript:void(0)' in output
    print('All self-test assertions passed.')

if __name__ == '__main__':
    run_test()
```

### README.md
```markdown
# noscript-audit

Small dependency-free Python 3 script that audits an HTML file for elements that depend on JavaScript.

## Usage

```bash
python3 noscript-audit.py path/to/file.html
```

## What it reports

- Count of `<script>` blocks
- Whether a `<noscript>` fallback exists
- One line per element that disappears without scripting (event handlers like `onclick`, `javascript:` links)

## Self-test

```bash
python3 self_test.py
```

Creates a tiny fixture, runs the audit, checks output.
```

### ARTIFACTS.md
```markdown
# tools/noscript-audit

- **noscript-audit.py**: Main script (dependency-free Python 3).
- **self_test.py**: Self-test with inline fixture.
- **README.md**: This file.
- **ARTIFACTS.md**: This entry.

Created: 2026-11-08.
Counts script tags, checks for `<noscript>`, reports event handler elements.
Self-test expects 1 script, noscript present, 2 disappearing elements (button onclick, javascript: link).
```

All four files go in `tools/noscript-audit/`. Commit together.

What I could not confirm: I did not run `python3 self_test.py` — nothing I write is executed. I did not verify the fixture HTML parses exactly or that the script handles multiple event handler attributes correctly. Left for the owner: commit the four files and run the self-test to confirm output matches expectations.
