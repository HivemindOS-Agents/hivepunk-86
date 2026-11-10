# noscript-audit

Read one local HTML file and report every external `<script>` URL plus whether the page still offers a `<noscript>` fallback. No network, standard library only, Python 3. The file is data: nothing in it is executed or followed as an instruction.

## What it does

`nostrip_audit.py` reads one HTML file and prints, in order:

- one `external-script: <url>` line per distinct external script URL (`http://`, `https://`, or protocol-relative `//`);
- one `noscript-missing: N external script(s) and no <noscript> fallback` line, only when at least one external script was found and no usable `<noscript>` text exists;
- one `summary: N external script(s), noscript present|missing` line.

A `<noscript>` counts as usable only when it has visible text. A `<noscript>` that holds nothing but a nested `<script>` has no visible text, so it counts as **missing**, and the nested script is not counted as a dependency. Relative and `data:` sources are not external. Duplicate URLs are reported once, in document order.

## Usage

~~~
python3 nostrip_audit.py path/to/page.html
~~~

Exit codes: `0` the audit ran (findings do not change the exit code); `2` wrong argument count or unreadable path, with a message on stderr.

To audit a folder of saved pages:

~~~
for f in pages/*.html; do echo "== $f"; python3 nostrip_audit.py "$f"; done
~~~

Expected output for the bundled `fixture.html`:

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

Run from inside this folder, no arguments, no network. It loads the tool with a top-level `import importlib.util` and checks six things:

1. the tool on `fixture.html` exits 0, prints exactly the five lines above, and writes nothing to stderr;
2. a real `<noscript>Enable JavaScript.</noscript>` gives one external line and `present`;
3. a relative script, an inline script and an empty `<noscript>` give only the 0-script `missing` summary;
4. a `<noscript>` holding only a nested `<script>` gives `summary: 0 external script(s), noscript missing`;
5. no argument prints `usage:` on stderr and exits 2;
6. a missing path prints `cannot read` on stderr and exits 2.

It exits 0 only when every check passes; otherwise it lists the failing checks on stderr and exits 1.

The last run's real output is recorded by HivemindOS in `SELFTEST_OUTPUT.md` in this folder after each commit. Read the state there; this README records no run and claims no pass.

## Other files in this folder

An earlier, differently-shaped draft also sits here: `noscript_audit.py`, a `noscript-audit.py` shim that calls it, and `ARTIFACTS.md`. That draft prints a longer report (script counts, inline handlers, hidden elements, empty mount points). This self-test exercises `nostrip_audit.py` only and does not touch them.

## What is untested

- The self-test has not been run by the agent that wrote it; only HivemindOS runs it, and its state lands in `SELFTEST_OUTPUT.md`.
- Real-browser behaviour: the tool never opens a page and never renders anything, so what a reader actually sees with scripting off is unconfirmed.
- Script-injected content: markup a script adds at runtime is invisible here.
- Non-HTML input (XML, SVG) and non-UTF-8 bytes: the file is read with `errors='replace'`, so mangled bytes inside an attribute could change a finding.
- Large files: the whole file is read into memory, no streaming.
- The three files of the earlier draft listed above.
