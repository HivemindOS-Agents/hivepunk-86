#!/usr/bin/env python3
"""Self-test for hex2rgb. Runs script.js in Node, no network, folder alone."""
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

JS = r"""
const m = require('./script.js');
function tryit(f){ try { return {ok: f()}; } catch(e){ return {err: e.message}; } }
function fakeDoc(){
  const els = {};
  return { els, getElementById(id){ if(!els[id]) els[id] = {textContent:'', style:{}}; return els[id]; } };
}
const out = {};
out.rgb_blue = m.hexToRgb('#1E90FF');
out.rgb_magenta = m.hexToRgb('#FF00FF');
out.rgb_short = m.hexToRgb('#FFF');
out.rgb_short2 = m.hexToRgb('0af');
out.rgb_lower = m.hexToRgb('1e90ff');
out.rgb_space = m.hexToRgb('  #000000  ');
out.rgb_empty = m.hexToRgb('');
out.rgb_null = m.hexToRgb(null);
out.bad_chars = tryit(() => m.hexToRgb('GGGGGG'));
out.bad_len2 = tryit(() => m.hexToRgb('#12'));
out.bad_len5 = tryit(() => m.hexToRgb('12345'));
out.bad_len8 = tryit(() => m.hexToRgb('#11223344'));
out.norm = m.normalizeHex('#0af');
out.explain = m.explain('#1E90FF');
out.explain_fb = m.explain('#3498DB');
const d = fakeDoc();
const info = m.render(d, '#1E90FF');
out.render_ok = {
  hex: info.hex,
  swatch: d.els.swatch.style.background,
  summary: d.els.summary.textContent,
  barR: d.els.barR.style.width, barG: d.els.barG.style.width, barB: d.els.barB.style.width,
  valR: d.els.valR.textContent, valG: d.els.valG.textContent, valB: d.els.valB.textContent,
  pairG: d.els.pairG.textContent, error: d.els.error.textContent
};
const d2 = fakeDoc();
const r2 = m.render(d2, 'zzz');
out.render_bad = { ret: r2, error: d2.els.error.textContent, barR: d2.els.barR.style.width, valB: d2.els.valB.textContent };
console.log(JSON.stringify(out));
"""

failures = []


def check(name, got, want):
    if got != want:
        failures.append("%s: got %r, expected %r" % (name, got, want))
    else:
        print("ok  " + name)


def main():
    try:
        p = subprocess.run(["node", "-e", JS], cwd=HERE, capture_output=True,
                           text=True, timeout=60)
    except (OSError, subprocess.TimeoutExpired) as e:
        print("FAIL could not run node: %s" % e)
        return 1
    if p.returncode != 0:
        print("FAIL node error:\n" + p.stderr)
        return 1
    try:
        o = json.loads(p.stdout.strip().splitlines()[-1])
    except (ValueError, IndexError):
        print("FAIL could not parse node output: %r" % p.stdout)
        return 1

    check("#1E90FF -> 30,144,255", o["rgb_blue"], [30, 144, 255])
    check("#FF00FF -> 255,0,255", o["rgb_magenta"], [255, 0, 255])
    check("#FFF shorthand", o["rgb_short"], [255, 255, 255])
    check("0af shorthand, no #", o["rgb_short2"], [0, 170, 255])
    check("lowercase", o["rgb_lower"], [30, 144, 255])
    check("surrounding spaces", o["rgb_space"], [0, 0, 0])
    check("empty -> null", o["rgb_empty"], None)
    check("null -> null", o["rgb_null"], None)
    for k in ("bad_chars", "bad_len2", "bad_len5", "bad_len8"):
        check(k + " rejected", "err" in o[k] and "Invalid HEX" in o[k]["err"], True)
    check("normalizeHex #0af", o["norm"], "00AAFF")

    e = o["explain"]
    check("explain hex", e["hex"], "#1E90FF")
    check("explain css", e["css"], "rgb(30, 144, 255)")
    # Both sides are lists of lists: the earlier version built a list of tuples here,
    # which never compares equal to nested lists even when the values match.
    check("explain pairs", [[p["channel"], p["pair"], p["value"]] for p in e["pairs"]],
          [["R", "1E", 30], ["G", "90", 144], ["B", "FF", 255]])
    check("explain percents", [p["percent"] for p in e["pairs"]], [11.76, 56.47, 100])

    r = o["render_ok"]
    check("render swatch", r["swatch"], "rgb(30, 144, 255)")
    check("render summary", r["summary"], "#1E90FF = rgb(30, 144, 255)")
    check("render bars", [r["barR"], r["barG"], r["barB"]], ["11.76%", "56.47%", "100%"])
    check("render values", [r["valR"], r["valG"], r["valB"]], ["30", "144", "255"])
    check("render pair text", r["pairG"], "90 \u2192 144")
    check("render no error", r["error"], "")

    b = o["render_bad"]
    check("render bad returns null", b["ret"], None)
    check("render bad shows error", "Invalid HEX" in b["error"], True)
    check("render bad resets bar", b["barR"], "0%")
    check("render bad resets value", b["valB"], "-")

    # --- Static <noscript> fallback table ---------------------------------
    fb = o["explain_fb"]
    check("fallback colour resolves", fb["css"], "rgb(52, 152, 219)")

    with open(os.path.join(HERE, "index.html"), encoding="utf-8") as f:
        html = f.read()

    ns = re.findall(r"<noscript>(.*?)</noscript>", html, re.S)
    check("exactly one noscript block", len(ns), 1)
    block = ns[0] if ns else ""
    check("noscript holds a table", "<table" in block, True)
    check("table has id pairTable", 'id="pairTable"' in block, True)
    check("caption names #3498DB", "#3498DB" in block, True)
    for head in ("Pair", "Hex", "Share of 255"):
        check("header cell %r" % head, "<th scope=\"col\">%s</th>" % head in block, True)

    rows = re.findall(r"<tr aria-label=\"([^\"]*)\">(.*?)</tr>", block, re.S)
    check("three labelled rows", len(rows), 3)
    if len(rows) == 3:
        for i, (label, cells) in enumerate(rows):
            p = fb["pairs"][i]
            label_txt = re.search(r"<th scope=\"row\">(.*?)</th>", cells, re.S)
            tds = re.findall(r"<td>(.*?)</td>", cells, re.S)
            check("row %d label cell" % (i + 1), label_txt.group(1) if label_txt else None,
                  "pair %d" % (i + 1))
            check("row %d hex cell matches script.js" % (i + 1), tds[:1], [p["pair"]])
            check("row %d share cell matches script.js" % (i + 1), tds[1:2], ["%g%%" % p["percent"]])
            check("row %d aria-label names pair" % (i + 1), "pair %d" % (i + 1) in label, True)
            check("row %d aria-label names channel" % (i + 1), p["channel"] in label, True)
            check("row %d aria-label names value of 255" % (i + 1),
                  "%d of 255" % p["value"] in label, True)
            check("row %d aria-label names share" % (i + 1), "%g percent" % p["percent"] in label, True)

    check("default input is #3498DB", 'id="hexInput" value="#3498DB"' in html, True)

    # --- Page wiring ------------------------------------------------------ 
    ids = set(re.findall(r'id="([^"]+)"', html))
    needed = {"hexInput", "error", "swatch", "summary"}
    for ch in "RGB":
        needed |= {"bar" + ch, "val" + ch, "pair" + ch}
    check("index.html has all ids", sorted(needed - ids), [])
    check("index.html loads script.js", 'src="script.js"' in html, True)
    check("only one script tag", len(re.findall(r"<script", html)), 1)
    check("no external src or href", re.search(r'(src|href)="https?:', html), None)

    # --- README browser test ---------------------------------------------
    with open(os.path.join(HERE, "README.md"), encoding="utf-8") as f:
        readme = f.read()
    check("README has Browser test heading", "## Browser test" in readme, True)
    check("README names the page", "tools/hex2rgb/index.html" in readme, True)
    check("README names the input", "#3498DB" in readme, True)
    for want in ("34` -> 52", "98` -> 152", "DB` -> 219"):
        check("README states %s" % want, want in readme, True)

    if failures:
        print("\nFAILED:")
        for x in failures:
            print("  " + x)
        return 1
    print("\nall checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
