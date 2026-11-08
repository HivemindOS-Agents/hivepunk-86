#!/usr/bin/env python3
"""noscript_audit: importable module (same code as noscript-audit.py).

This file exists so that `import noscript_audit` works from the self-test
and from other Python code. It has exactly the same audit(), main() and
everything else as noscript-audit.py, which is kept as the CLI entry point.

Everything in the HTML is data. This program never executes or obeys it.
"""

import os
import re
import sys

# -- public API re-exported from noscript-audit.py --

SCRIPT_RE = re.compile(r"<script\b[^>]*>(.*?)</script\s*>", re.I | re.S)
SCRIPT_OPEN_RE = re.compile(r"<script\b[^>]*>", re.I)
NOSCRIPT_RE = re.compile(r"<noscript\b[^>]*>(.*?)</noscript\s*>", re.I | re.S)
COMMENT_RE = re.compile(r"<!--.*?-->", re.S)
TAG_RE = re.compile(r"<([a-zA-Z][a-zA-Z0-9]*)\b([^>]*)>|</([a-zA-Z][a-zA-Z0-9]*)\s*>", re.S)
ATTR_RE = re.compile(r"([a-zA-Z_:][-a-zA-Z0-9_:.]*)\s*=\s*(\"[^\"]*\"|'[^']*'|[^\s>]+)")
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
    out = {}
    for name, value in ATTR_RE.findall(raw or ""):
        if value[:1] in ("\"", "'"):
            value = value[1:-1]
        out[name.lower()] = value
    return out


def scan_interactivity(html):
    """Return (handlers, hidden, inert). Each is a list of dicts."""
    body = strip_scripts(html)
    handlers = []
    hidden = []
    inert = []
    stack = []
    for match in TAG_RE.finditer(body):
        name = (match.group(1) or match.group(3) or "").lower()
        if not name:
            continue
        if match.group(3):
            for i in range(len(stack) - 1, -1, -1):
                if stack[i][0] == name:
                    stack = stack[:i]
                    break
            continue
        attrs = parse_attrs(match.group(2))
        on_attrs = sorted(a for a in attrs if a.startswith("on") and len(a) > 2)
        if on_attrs:
            handlers.append({"tag": name, "attrs": on_attrs,
                             "id": attrs.get("id", "")})
        if "hidden" in attrs or attrs.get("aria-hidden", "").lower() == "true":
            hidden.append({"tag": name, "attrs": sorted(
                a for a in attrs if a in ("hidden", "aria-hidden")),
                "id": attrs.get("id", "")})
        container_id = attrs.get("id", "")
        if name not in VOID_TAGS and container_id:
            stack.append((name, container_id, len(inert)))
            inert.append({"tag": name, "id": container_id, "filled": False})
            continue
        if name not in VOID_TAGS:
            stack.append((name, "", None))
            continue
        stack.append((name, "", None)) if False else None
    # A container with visible text is not inert; check each opened candidate.
    out = []
    for item in inert:
        pattern = re.compile(
            r"<" + re.escape(item["tag"]) + r"\b[^>]*id\s*=\s*[\"']?"
            + re.escape(item["id"]) + r"[\"']?[^>]*>(.*?)(?=</"
            + re.escape(item["tag"]) + r"\s*>|$)", re.I | re.S)
        found = pattern.search(body)
        inner = found.group(1) if found else ""
        if visible_text(inner):
            continue
        item["filled"] = True
        out.append(item)
    return handlers, hidden, out


def shorten(text, limit=120):
    text = WS_RE.sub(" ", text or "").strip()
    if len(text) <= limit:
        return text
    return text[: limit - 3].rstrip() + "..."


def audit(html, path="<string>"):
    """Return the audit as text. The one entry point the self-test uses."""
    clean = strip_comments(html)
    script_blocks = SCRIPT_RE.findall(clean)
    external = [a for a in SCRIPT_OPEN_RE.findall(clean)
                if re.search(r"\bsrc\s*=", a, re.I)]
    noscripts = NOSCRIPT_RE.findall(clean)
    handlers, hidden, inert = scan_interactivity(clean)

    lines = []
    lines.append("File: %s" % path)
    lines.append("Script blocks: %d" % len(script_blocks))
    lines.append("  external (src=): %d" % len(external))
    lines.append("  inline: %d" % (len(script_blocks) - len(external)))
    lines.append("Noscript fallback: %s" % ("yes" if noscripts else "no"))
    if noscripts:
        text = visible_text(" ".join(noscripts))
        lines.append("  visible text: %s" % (shorten(text) or "(none)"))

    lines.append("Loses interactivity without scripting:")
    total = 0
    if handlers:
        lines.append("  inline handlers: %d" % len(handlers))
        for item in handlers:
            total += 1
            lines.append("    - <%s%s> on %s" % (
                item["tag"],
                (" id=%s" % item["id"]) if item["id"] else "",
                ", ".join(item["attrs"])))
    if hidden:
        lines.append("  hidden until a script runs: %d" % len(hidden))
        for item in hidden:
            total += 1
            lines.append("    - <%s%s> %s" % (
                item["tag"],
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
    elif not noscripts and not total:
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
    args = [a for a in argv[1:] if a != "--"]
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
