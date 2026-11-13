#!/usr/bin/env python3
"""noscript-audit: check one or more HTML files for the presence of a <noscript> block.

Usage:
    python3 -m modules.audit file.html [file.html ...]

Reads each HTML file, parses it with the built-in html.parser, and checks for
a <noscript>...</noscript> element anywhere in the document tree.

For each file:
- If the file contains a <noscript> block, prints "OK: <path>" on stdout.
- If the file does NOT contain a <noscript> block, prints
  "noscript-audit: missing <noscript> in <path>" on stderr.

Exit codes:
    0  all files contain a <noscript> block
    1  one or more files lack a <noscript> block
    2  usage or read error
"""

import html.parser
import sys


class NoscriptFinder(html.parser.HTMLParser):
    """A parser that sets self.found = True when it sees a <noscript> start tag."""

    def __init__(self):
        super().__init__()
        self.found = False

    def handle_starttag(self, tag, attrs):
        if tag.lower() == "noscript":
            self.found = True


def has_noscript(path):
    """Return True if the HTML file at *path* contains a <noscript> element.

    Ignores the content of <script>, <style> or other tags — only the tag name
    is checked. Nothing in the file is executed or followed as an instruction.
    """
    parser = NoscriptFinder()
    try:
        with open(path, "r", encoding="utf-8") as fh:
            parser.feed(fh.read())
    except (OSError, UnicodeError) as exc:
        print("noscript-audit: cannot read %s: %s" % (path, exc), file=sys.stderr)
        return None
    parser.close()
    return parser.found


def main(argv):
    if len(argv) < 2:
        print("usage: python3 -m modules.audit file.html ...", file=sys.stderr)
        return 2

    files = argv[1:]
    exit_code = 0

    for path in files:
        result = has_noscript(path)
        if result is None:
            exit_code = 2
            continue
        if result:
            print("OK: %s" % path)
        else:
            print("noscript-audit: missing <noscript> in %s" % path, file=sys.stderr)
            exit_code = 1

    return exit_code


if __name__ == "__main__":
    sys.exit(main(sys.argv))
