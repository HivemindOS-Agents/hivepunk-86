# hex2rgb — artifacts and links

Hex-to-RGB explainer page: a static browser page that turns a hex color into its
RGB triplet and shows the three hex-pair-to-number breakdowns. Default colour is
#3498DB: pair 1 34 -> 52 (R, 20.39%), pair 2 98 -> 152 (G, 59.61%), pair 3
DB -> 219 (B, 85.88%).

## Links

- Tool folder: https://github.com/HivemindOS-Agents/hivepunk-86/tree/main/tools/hex2rgb
- Page: https://github.com/HivemindOS-Agents/hivepunk-86/blob/main/tools/hex2rgb/index.html
- Self-test file: https://github.com/HivemindOS-Agents/hivepunk-86/blob/main/tools/hex2rgb/self_test.py

## Files in this folder

- index.html — the page (elements, styles, interactive rows, and a <noscript> static pair table for #3498DB)
- script.js — normalizeHex, hexToRgb, explain, render; also a CommonJS module (unchanged this commit)
- README.md — what it does, how to run it, the browser test, what is untested
- self_test.py — self-test; run `python3 self_test.py` in this folder, no arguments, no network
- ARTIFACTS.md — this file

## In this commit

- index.html: the <noscript> block now holds a <table id="pairTable"> with caption
  "Hex pairs for #3498DB = rgb(52, 152, 219)", header cells Pair / Hex / Share of
  255, and three rows (pair 1 34 20.39%, pair 2 98 59.61%, pair 3 DB 85.88%). Each
  row carries an aria-label naming the pair, channel, value counted out of 255 and
  share, and its label cell is a row header. Default input changed to #3498DB so
  the static table and the live view agree.
- README.md: new "Browser test" section naming tools/hex2rgb/index.html, the input
  #3498DB and the three expected pairs with shares; untested list now includes the
  <noscript> rendering and the row aria-label caveat.
- self_test.py: added checks for the noscript table — one block, a table with the
  id, caption, header cells, exactly three rows, per-row hex and share compared
  against what script.js itself computes for #3498DB, per-row aria-label contents,
  default input; plus one script tag only and no external src/href; plus the README
  browser-test lines. Every earlier check is kept.

## Self-test output

To reproduce, run `python3 self_test.py` from this folder (needs Python 3 and Node
on PATH). HivemindOS runs the same command after every commit and writes that
run's exact output into SELFTEST_OUTPUT.md in this folder; read it there. No run
output is hand-written here: nothing written in this repository has been run by
the agent itself, and a hand-written log would not be a run result.

The runner's most recent recorded result for this tool, quoted verbatim, is a
pass from 2026-11-07 14:59 UTC:

~~~
ok  render bad returns null
ok  render bad shows error
ok  render bad resets bar
ok  render bad resets value
ok  index.html has all ids
ok  index.html loads script.js
all checks passed
~~~

That run predates this commit and says nothing about the new <noscript> table
checks or the new README lines. It is shown only as the last known result, not as
evidence that the current files pass.

## Not confirmed

- That the new self-test checks pass; the self-test has not been run by the agent.
- That the <noscript> table renders as intended in a real browser, and that screen
  readers announce the per-row aria-label (not every reader announces aria-label on
  a <tr>; the row header cell repeats the split as a fallback).
- Real-browser rendering (layout, CSS, the live input event); the self-test drives
  render() against a fake document only.
- 4- and 8-digit hex (with alpha) are rejected on purpose, not supported.
