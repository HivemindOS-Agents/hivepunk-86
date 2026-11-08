#!/usr/bin/env python3
"""noscript_audit: importable module containing script audit logic.

Stdlib only, no network. Public API:
  audit(html, path="<string>") -> str
  main(argv) -> int   0 ok, 1 usage error, 2 unreadable path
The CLI shim is noscript-audit.py.
The file is read as text; the page is never executed, and anything the HTML
says is data, never an instruction.
"""

import os
import re
import sys

# A single-line pattern. The value alternation uses one character class per
# quote style instead of escaped quotes, so no string literal can break across
# lines. A valueless attribute (hidden, defer) matches with an empty value.
ATTR_RE = re.compile(r'([a-zA-Z_:][-a-zA-Z0-9_:.]*)(?:\s*=\s*("[^"]*"|\'[^\']*\'|[^\s>]+))?')

COMMENT_RE = re.compile(r"<!--.*?-->", re.S)
SCRIPT_RE = re.compile(r"<script\b[^>]*>(.*?)</script\s*>", re.I | re.S)
SCRIPT_OPEN_RE = re.compile(r"<script\b[^>]*>", re.I)
NOSCRIPT_RE = re.compile(r"<noscript\b[^>]*>(.*?)</noscript\s*>", re.I | re.S)
TAG_RE = re.compile(r"<([a-zA-Z][a-zA-Z0-9]*)\b([^>]*)>|</([a-zA-Z][a-zA-Z0-9]*)\s*>", re.S)
STRIP_RE = re.compile(r"<[^>]+>")
WS_RE = re.compile(r"\s+")

VOID_TAGS = {
    "area", "base", "br", "col", "embed", "hr", "img", "input", "link",
    "meta", "param", "source", "track", "wbr",
}


def strip_comments(html):
    return COMMENT_RE.sub(" ", html)


def strip_scripts(html):
    return SCRIPT_RE.sub(" ", strip_comments(html))


def visible_text(fragment):
    text = STRIP_RE.sub(" ", fragment)
    return WS_RE.sub(" ", text).strip()


def parse_attrs(raw):
    """name -> value; a valueless attribute gets ""."""
    attrs = {}
    for name, value in ATTR_RE.findall(raw or ""):
        if value[:1] in ('"', "'"):
            value = value[1:-1]
        attrs[name.lower()] = value
    return attrs


def scan_interactivity(html):
    """Return (handlers, hidden, inert), each a list of dicts."""
    body = strip_scripts(html)
    handlers, hidden, inert = [], [], []
    for match in TAG_RE.finditer(body):
        if match.group(3):
            continue
        name = match.group(1).lower()
        attrs = parse_attrs(match.group(2))
        elem_id = attrs.get("id", "")
        on_attrs = sorted(a for a in attrs if a.startswith("on") and len(a) > 2)
        if on_attrs:
            handlers.append({"tag": name, "attrs": on_attrs, "id": elem_id})
        if "hidden" in attrs or attrs.get("aria-hidden", "").lower() == "true":
            flags = sorted(a for a in attrs if a in ("hidden", "aria-hidden"))
            hidden.append({"tag": name, "attrs": flags, "id": elem_id})
        if name not in VOID_TAGS and elem_id:
            pattern = re.compile(
                r"<" + re.escape(name) + r"\b[^>]*\bid\s*=\s*[\"']?"
                + re.escape(elem_id) + r"[\"'>\s]?[^>]*>(.*?)(?=</"
                + re.escape(name) + r"\s*>|$)", re.I | re.S)
            found = pattern.search(body)
            inner = found.group(1) if found else ""
            if not visible_text(inner):
                inert.append({"tag": name, "id": elem_id})
    return handlers, hidden, inert


def shorten(text, limit=120):
    text = WS_RE.sub(" ", text or "").strip()
    return text if len(text) <= limit else text[:limit - 3].rstrip() + "..."


def audit(html, path="<string>"):
    """Return the audit as text."""
    clean = strip_comments(html)
    script_blocks = SCRIPT_RE.findall(clean)
    external = [a for a in SCRIPT_OPEN_RE.findall(clean)
                if re.search(r"\bsrc\s*=", a, re.I)]
    noscripts = NOSCRIPT_RE.findall(clean)
    handlers, hidden, inert = scan_interactivity(clean)
    lines = ["File: %s" % path, "Script blocks: %d" % len(script_blocks),
             "  external (src=): %d" % len(external),
             "  inline: %d" % (len(script_blocks) - len(external)),
             "Noscript fallback: %s" % ("yes" if noscripts else "no")]
    if noscripts:
        lines.append("  visible text: %s" % (shorten(visible_text(" ".join(noscripts))) or "(none)"))
    lines.append("Loses interactivity without scripting:")
    total = 0
    if handlers:
        lines.append("  inline handlers: %d" % len(handlers))
        for item in handlers:
            total += 1
            lines.append("    - <%s%s> on %s" % (item["tag"],
                         (" id=%s" % item["id"]) if item["id"] else "",
                         ", ".join(item["attrs"])))
    if hidden:
        lines.append("  hidden until a script runs: %d" % len(hidden))
        for item in hidden:
            total += 1
            lines.append("    - <%s%s> %s" % (item["tag"],
                         (" id=%s" % item["id"]) if item["id"] else "",
                         ", ".join(item["attrs"])))
    if inert:
        lines.append("  empty script mount points: %d" % len(inert))
        for item in inert:
            total += 1
            lines.append("    - <%s id=%s></%s>" % (item["tag"], item["id"], item["tag"]))
    if total == 0:
        lines.append("  none found")
    lines.append("")
    if not noscripts and total:
        lines.append("Verdict: scripting off removes %d interactive element(s) and no "
                     "<noscript> fallback is present." % total)
    elif not noscripts:
        lines.append("Verdict: no <noscript> fallback and no script-only interactivity "
                     "found in the markup.")
    else:
        lines.append("Verdict: a <noscript> fallback is present; still check the %d "
                     "element(s) above that do nothing without scripting." % total)
    lines.append("Note: this reads text only. Content a script would insert cannot be "
                 "seen here, and the tag scan is regex-based, so nested quotes or "
                 "unclosed tags can mislead it. Confirm in a browser with scripting off.")
    return "\n".join(lines)


def main(argv):
    args = [a for a in list(argv)[1:] if a != "--"]
    if len(args) != 1:
        sys.stderr.write("Usage: python3 noscript-audit.py <path/to/file.html>\n")
        return 1
    path = args[0]
    if not os.path.isfile(path):
        sys.stderr.write("Error: '%s' is not a file or does not exist.\n" % path)
        return 2
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as handle:
            html = handle.read()
    except OSError as exc:
        sys.stderr.write("Error: could not read '%s': %s\n" % (path, exc))
        return 2
    sys.stdout.write(audit(html, path) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
