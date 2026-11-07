# Hex to RGB explainer

A small static page that turns a hex color into an RGB triplet and shows how:

- the normalized hex and the `rgb(r, g, b)` string
- the three hex pairs and the number each one gives (e.g. `1E -> 30`)
- a color swatch
- three channel bars (R, G, B), each filled to value / 255

No network requests, no external files.

## Usage

1. Open `index.html` in a browser. It starts with `#1E90FF` (30, 144, 255).
2. Type a color. The page updates as you type.
3. Accepted: `#RRGGBB`, `RRGGBB`, `#RGB`, `RGB`, any letter case. Anything else shows an error and clears the bars.

The logic is in `script.js` and is also a CommonJS module:
`normalizeHex`, `hexToRgb`, `explain`, `render(doc, input)`.

## Self test

    python3 self_test.py

Run from this folder with no arguments. Needs Python 3 and Node on PATH. It runs `script.js` in Node, compares results with expected values, and exits 0 only if every check passes.

## What is untested

- Rendering in a real browser (layout, CSS, the live `input` event). The self-test drives `render()` with a fake document only.
- Accessibility beyond basic labels.
- 4- and 8-digit hex (with alpha) are deliberately rejected, not supported.
