#!/usr/bin/env python3
"""noscript_audit: importable module containing script audit logic.

This module implements the audit functionality used by the CLI wrapper
`noscript-audit.py` and by the self‑test. It counts `<script>` blocks, detects
whether a `<noscript>` fallback is present, and identifies elements that lose
interactivity when JavaScript is turned off.  All parsing is performed with
standard‑library regular expressions, so the module contains no external
dependencies.

The public API is:

  audit(html: str, path: str = "<string>") -> str
      Return a human‑readable report for the supplied HTML string.
  main(argv: Sequence[str] | None = None) -> int
      CLI entry point compatible with ``python3 noscript-audit.py``.

See the accompanying README for usage details.  The tool deliberately
restricts itself to a text read of the file; any content a script would
inject is invisible to the audit.
"""

import os
import re
import sys

# ---------------------------------------------------------------------------
# Regex utilities – attribute parsing must support boolean attributes such as
# ``hidden`` which have no ``=`` value.
# ---------------------------------------------------------------------------
ATTR_RE = re.compile(
    r"([a-zA-Z_:][-a-zA-Z0-9_:.]*)"      # attribute name
    r"(?:\s*=\s*(?:\"([^\"]*)\"|'
    r"([^']*)'|([^\s>]+)))?",  # optional value with quotes or unquoted
    re.I,
)

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

# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def strip_comments(html: str) -> str:
    """Remove HTML comments from the supplied string.

    The removal replaces the comment with a single space to preserve
    character offsets used by subsequent regexes.
    """
    return COMMENT_RE.sub(" ", html)


def strip_scripts(html: str) -> str:
    """Return *html* with all ``<script>`` blocks removed.

    The function removes both the opening tag and the closing tag and the
    intervening JavaScript content.
    """
    return SCRIPT_RE.sub(" ", strip_comments(html))


def visible_text(fragment: str) -> str:
    """Return the concatenated, whitespace‑normalised text of *fragment*.

    All markup is stripped; the result contains only human‑readable words.
    """
    text = STRIP_RE.sub(" ", fragment)
    return WS_RE.sub(" ", text).strip()


def parse_attrs(raw: str | None) -> dict[str, str]:
    """Parse an attribute string into a dict of *name → value*.

    Boolean attributes are returned with the empty string as the value so
    that ``"hidden" in attrs`` correctly identifies the presence of the
    attribute.
    """
    attrs: dict[str, str] = {}
    if not raw:
        return attrs
    for name, val1, val2, val3 in ATTR_RE.findall(raw):
        name_lc = name.lower()
        value = val1 or val2 or val3 or ""
        attrs[name_lc] = value
    return attrs


def scan_interactivity(html: str):
    """Scan *html* for elements that lose interactivity without JavaScript.

    Returns a tuple ``(handlers, hidden, inert)`` where each part is a list of
    dictionaries describing the elements found.
    """
    body = strip_scripts(html)
    handlers: list[dict] = []
    hidden: list[dict] = []
    inert: list[dict] = []

    for match in TAG_RE.finditer(body):
        name = (match.group(1) or match.group(3) or "").lower()
        if not name:
            continue
        if match.group(3):  # closing tag – nothing to do
            continue
        attrs = parse_attrs(match.group(2))
        on_attrs = sorted(a for a in attrs if a.startswith("on") and len(a) > 2)
        if on_attrs:
            handlers.append({"tag": name, "attrs": on_attrs, "id": attrs.get("id", "")})
        if "hidden" in attrs or attrs.get("aria-hidden", "").lower() == "true":
            hidden.append({"tag": name, "attrs": sorted(a for a in attrs if a in ("hidden", "aria-hidden")), "id": attrs.get("id", "")})
        if name not in VOID_TAGS and attrs.get("id"):
            inert.append({"tag": name, "id": attrs["id"], "filled": False})

    # Determine which inert candidates are really empty.
    out: list[dict] = []
    for item in inert:
        pattern = re.compile(
            r"<" + re.escape(item["tag"]) + r"\b[^>]*\bid\s*=\s*[\"']?"
            + re.escape(item["id"]) + r"[\"']?[^>]*>(.*?)(?=</"
            + re.escape(item["tag"]) + r"\s*>|$)", re.I | re.S)
        found = pattern.search(body)
        inner = found.group(1) if found else ""
        if visible_text(inner):
            continue
        out.append(item)
    return handlers, hidden, out


# ---------------------------------------------------------------------------
# Core audit logic
# ---------------------------------------------------------------------------

def audit(html: str, path: str = "<string>") -> str:
    """Analyse *html* and return a plain‑text report.

    The function follows the same behaviour as the CLI wrapper but returns
    the result string so it can be consumed by unit tests.
    """
    script_blocks = SCRIPT_RE.findall(html)
    external = [t for t in SCRIPT_OPEN_RE.findall(html) if re.search(r"\bsrc\s*=", t, re.I)]
    noscripts = NOSCRIPT_RE.findall(html)
    handlers, hidden, inert = scan_interactivity(html)

    lines = ["File: %s" % path]
    lines.append("Script blocks: %d" % len(script_blocks))
    lines.append("  external (src=): %d" % len(external))
    lines.append("  inline: %d" % (len(script_blocks) - len(external)))
    lines.append("Noscript fallback: %s" % ("yes" if noscripts else "no"))
    if noscripts:
        text = visible_text(" ".join(noscripts))
        lines.append("  visible text: %s" % (text[:120] if text else "(none)"))

    lines.append("Loses interactivity without scripting:")
    total = 0
    if handlers:
        lines.append("  inline handlers: %d" % len(handlers))
        for item in handlers:
            total += 1
            lines.append("    - <%s%s> on %s" % (
                item["tag"],
                (" id=%s" % item["id"]) if item["id"] else "",
                ", ".join(item["attrs"])  # attribute names only
            ))
    if hidden:
        lines.append("  hidden until a script runs: %d" % len(hidden))
        for item in hidden:
            total += 1
            lines.append("    - <%s%s> %s" % (
                item["tag"],
                (" id=%s" % item["id"]) if item["id"] else "",
                ", ".join(item["attrs"])
            ))
    if inert:
        lines.append("  empty script mount points: %d" % len(inert))
        for item in inert:
            total += 1
            lines.append("    - <%s id=%s></%s>" % (item["tag"], item["id"], item["tag"]))
    if total == 0:
        lines.append("  none found")

    lines.append("")
    if not noscripts and total:
        lines.append(
            "Verdict: scripting off removes %d interactive element(s) and no <noscript> fallback is present." % total
        )
    elif not noscripts and not total:
        lines.append("Verdict: no <noscript> fallback and no script-only interactivity found in the markup.")
    else:
        lines.append(
            "Verdict: a <noscript> fallback is present; still check the %d element(s) above that do nothing without scripting." % total
        )
    lines.append(
        "Note: this reads text only. Content a script would insert cannot be seen here, and the tag scan is regex-based, so nested quotes or unclosed tags can mislead it. Confirm in a browser with scripting off."
    )
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI wrapper – compatible with ``python3 noscript-audit.py``
# ---------------------------------------------------------------------------

def main(argv: Sequence[str] | None = None) -> int:
    argv = list(argv or sys.argv[1:])
    if len(argv) != 1:
        sys.stderr.write("Usage: python3 noscript-audit.py <path/to/file.html>\n")
        return 1
    path = argv[0]
    if not os.path.isfile(path):
        sys.stderr.write("Error: '%s' is not a file or does not exist.\n" % path)
        return 2
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as fh:
            html = fh.read()
    except OSError as exc:
        sys.stderr.write("Error: could not read '%s': %s\n" % (path, exc))
        return 2
    sys.stdout.write(audit(html, path) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
