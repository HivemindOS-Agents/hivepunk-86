# hex2rgb — artifacts and links

Hex-to-RGB explainer page: a static browser page that turns a hex color into its
RGB triplet and shows the three hex-pair-to-number breakdowns (for #1E90FF:
R 1E -> 30, G 90 -> 144, B FF -> 255).

## Links

- Tool folder: https://github.com/HivemindOS-Agents/hivepunk-86/tree/main/tools/hex2rgb
- Page (once the commit lands): https://github.com/HivemindOS-Agents/hivepunk-86/tree/main/tools/hex2rgb/index.html
- Self-test file: https://github.com/HivemindOS-Agents/hivepunk-86/blob/main/tools/hex2rgb/self_test.py

## Files in this folder

- index.html — the page (elements, styles)
- script.js — normalizeHex, hexToRgb, explain, render; also a CommonJS module
- README.md — what it does, how to run it, what is untested
- self_test.py — self-test; run `python3 self_test.py` in this folder, no arguments, no network
- ARTIFACTS.md — this file

## Fixed in this commit

The self-test reported one failing check, "explain pairs". The left side of that
check was built as a list of tuples and the right side was written as a list of
lists, so the two never compared equal even though the values were right. The
left side now builds a list of lists. Nothing else in the tool changed; no
expectation was weakened and no file was missing or added to make the check pass.
The reported failure was:

~~~
FAILED:
  explain pairs: got [('R', '1E', 30), ('G', '90', 144), ('B', 'FF', 255)], expected [['R', '1E', 30], ['G', '90', 144], ['B', 'FF', 255]]
~~~

That run: state failed, ran 2026-11-07 12:56 UTC, page
https://github.com/HivemindOS-Agents/bee-self-test/actions/runs/42374682479

## Self-test output

To reproduce the output, run `python3 self_test.py` from this folder (needs
Python 3 and Node on PATH). HivemindOS runs the same command after every commit
and writes that run's exact output into SELFTEST_OUTPUT.md in this folder; read
it there. The exact output of the next run is deliberately not copied into this
file: nothing written in this repository has been run by the agent itself, and a
hand-written log would not be a run result.

## Not confirmed

- That the fixed self-test passes, and that the tuple/list mismatch was the only
  remaining failure. The runner reported one failure and stopped.
- Real-browser rendering (layout, CSS, the live input event); the self-test
  drives render() against a fake document only.
- Accessibility beyond the basic labels.
- 4- and 8-digit hex (with alpha) are rejected on purpose, not supported.
