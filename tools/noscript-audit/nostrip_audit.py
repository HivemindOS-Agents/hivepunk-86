#!/usr/bin/env python3
'''noscript-audit: report external <script> URLs and whether a <noscript> fallback exists.

Usage:  python3 nostrip_audit.py <file.html>

No network. Reads one local HTML file. Prints one line per finding:
    external-script: <url>
    noscript-missing: <n> external script(s) and no <noscript> fallback
    summary: <n> external script(s), noscript present|missing

Exit 0 when the audit runs (findings do not change exit code); 2 on usage
or read error.
'''

import sys
from html.parser import HTMLParser

USAGE = 'usage: nostrip_audit.py <file.html>'


def is_external(src):
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
