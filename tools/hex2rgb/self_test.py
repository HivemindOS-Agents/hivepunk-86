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
    check("explain pairs", [(p["channel"], p["pair"], p["value"]) for p in e["pairs"]],
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

    # Page wiring: every id the script looks up must exist in index.html.
    with open(os.path.join(HERE, "index.html"), encoding="utf-8") as f:
        html = f.read()
    ids = set(re.findall(r'id="([^"]+)"', html))
    needed = {"hexInput", "error", "swatch", "summary"}
    for ch in "RGB":
        needed |= {"bar" + ch, "val" + ch, "pair" + ch}
    check("index.html has all ids", sorted(needed - ids), [])
    check("index.html loads script.js", 'src="script.js"' in html, True)

    if failures:
        print("\nFAILED:")
        for x in failures:
            print("  " + x)
        return 1
    print("\nall checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
