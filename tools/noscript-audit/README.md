# noscript-audit

A small, offline Python script that reads one local HTML file and reports every external `<script>` URL plus whether the page has a usable `<noscript>` fallback.

## What it does

Run it against one HTML file. It prints:

- one line per distinct external script URL (`http://`, `https://` or protocol-relative `//`);
- one `noscript-missing` line when external scripts exist and the page has no non-empty `<noscript>` text;
- one `summary` line with the count and whether a fallback is present.

Standard library only. It never makes a network request and never executes the HTML it reads — the file is data. A `<noscript>` that contains only a nested `<script>` has no visible text, so it counts as *missing*; the nested script is not counted as a dependency.

## Usage

~~~
python3 nostrip_audit.py path/to/page.html
~~~

Exit codes: `0` audit printed, `2` usage error or unreadable path. Findings never change the exit code.

Example output for `fixture.html`:

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

Run from inside this folder, with no arguments and no network. It loads `nostrip_audit.py` with `importlib.util` and checks:

1. the tool on `fixture.html`: exit 0, the exact five lines above, empty stderr;
2. `audit_lines()` with a real `<noscript>Enable JavaScript.</noscript>`: one external line, no `noscript-missing`, `noscript present`;
3. `audit_lines()` with a relative script, an inline script and an empty `<noscript>`: only the 0-script `missing` summary;
4. `audit_lines()` with `<noscript><script src=...></script></noscript>`: the fallback has no visible text, so `summary: 0 external script(s), noscript missing`;
5. no argument: usage on stderr, exit 2;
6. a missing path: `cannot read` on stderr, exit 2.

It exits 0 only when every check passes, otherwise prints the failing checks on stderr and exits 1.

## Other files in this folder

This folder also holds an earlier, differently-shaped draft: `noscript_audit.py`, a `noscript-audit.py` shim that calls it, and `ARTIFACTS.md`. Those print a longer report (script counts, inline handlers, hidden elements, empty mount points). The self-test here exercises `nostrip_audit.py` only and does not touch them. Nothing has been deleted, because this step was scoped to making the self-test pass.

## What is untested

- I have not run the self-test. HivemindOS runs `python3 self_test.py` in this folder after each commit and writes that run's real output into `SELFTEST_OUTPUT.md` here; the pass or fail state lives there, not in this README.
- Network behaviour: everything is offline by design.
- Non-HTML input: parser behaviour on XML, SVG or other text.
- Script-rendered content: anything a script would insert at runtime is invisible to this tool.
- Non-UTF-8 files: read with `errors='replace'`, so mangled bytes in an attribute could change a finding.
- Large files: the whole file is read into memory, no streaming.
- The two extra draft files noted above are untested here.
