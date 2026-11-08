# Hex to RGB explainer

A small static page that turns a hex color into an RGB triplet and shows how:

- the normalized hex and the `rgb(r, g, b)` string
- the three hex pairs and the number each one gives (e.g. `1E -> 30`)
- a color swatch
- three channel bars (R, G, B), each filled to value / 255

No network requests, no external files.

## Usage

1. Open `index.html` in a browser. It starts with `#3498DB` (52, 152, 219).
2. Type a color. The page updates as you type.
3. Accepted: `#RRGGBB`, `RRGGBB`, `#RGB`, `RGB`, any letter case. Anything else shows an error and clears the bars.

The logic is in `script.js` and is also a CommonJS module:
`normalizeHex`, `hexToRgb`, `explain`, `render(doc, input)`.

## Browser test

Open `tools/hex2rgb/index.html` in a browser and type `#3498DB` in the input.
Expected result, on the channel rows and in the static table alike:

- pair 1 `34` -> 52 (red), 20.39%
- pair 2 `98` -> 152 (green), 59.61%
- pair 3 `DB` -> 219 (blue), 85.88%

The swatch turns blue and the summary reads `#3498DB = rgb(52, 152, 219)`. With
scripting turned off, the `<noscript>` block in the same file shows the same
three pairs as a plain table, so the two views can be compared by hand.

## Self test

    python3 self_test.py

Run from this folder with no arguments. Needs Python 3 and Node on PATH. It runs `script.js` in Node, compares results with expected values, and exits 0 only if every check passes. It also checks the `<noscript>` table against what `script.js` itself computes for `#3498DB`.

## What is untested

- That the `<noscript>` table renders as intended in a real browser, and that screen readers announce the per-row `aria-label` text (a row `aria-label` is not announced by every reader; the row header cell carries the same split as a fallback).
- Real-browser rendering (layout, CSS, the live `input` event). The self-test drives `render()` with a fake document only.
- Accessibility beyond these labels.
- 4- and 8-digit hex (with alpha) are deliberately rejected, not supported.
