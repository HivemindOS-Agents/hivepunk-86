# Hex to RGB Converter

A tiny browser‑only tool that converts a hex color value (e.g. `#FF00FF` or `#F0F`) into an RGB triplet.

## Usage

1. Open `index.html` in a browser.
2. Type a hex color into the input field.
3. Click **Convert**.
4. The RGB result appears below.

The page is completely static – no network requests are made.

## Development

The conversion logic lives in `script.js`.  It is written as a vanilla JavaScript function `hexToRgb(hex)` and also exported as a CommonJS module so that the included tests can import it.

## Self test

Run `python3 self_test.py` to execute the test suite. All tests should pass on any platform that has Python 3.6+ and Node ≥ 12 installed.
