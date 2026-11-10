# noscript-audit

A small Python script that reads one local HTML file and reports every external script URL plus whether the page has a `<noscript>` fallback.

## What it does

Run it against any HTML file. It prints:

- One line per distinct external script URL (`http://`, `https://` or protocol-relative `//`).
- One `noscript-missing` line when external scripts exist and the page has no non-empty `<noscript>` element.
- One `summary` line naming the count and whether a fallback is present.

It uses only the Python standard library. It never makes a network request; the HTML it reads is data and is never executed.

## Usage

~~~
python3 nostrip_audit.py path/to/page.html
~~~

Exit codes: `0` audit printed, `2` usage error or unreadable path.

Example output:

~~~
external-script: https://cdn.example.com/analytics.js
external-script: //cdn.example.com/analytics.js
external-script: https://cdn.example.com/app.js
noscript-missing: 3 external script(s) and no <noscript> fallback
summary: 3 external script(s), noscript missing
~~~

## Self-test

~~~
python3 self_test.py
~~~

Run from this folder with no arguments and no network. It runs `nostrip_audit.py` against `fixture.html` and checks the exact stdout, plus exercises the no-argument and missing-file error paths. It also tests the `audit_lines()` function directly with a fallback-present case, a relative/empty-noscript case, and a script-inside-noscript case. Exits 0 only when every check passes.

## What is untested

- The self-test has never been run by the agent; the passed/failed state is recorded in `SELFTEST_OUTPUT.md` after HivemindOS runs it.
- Network behaviour: everything is off-line by design.
- Non-HTML files: HTML parser behaviour on XML, SVG or other text.
- JavaScript-rendered content: the script reads the HTML file as text; anything a script would insert at runtime is invisible.
- Non-UTF-8 files: read with `errors='replace'`; mangled bytes in an attribute could change a finding.
- Large files: no streaming, the whole file is read into memory.
