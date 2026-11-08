# noscript-audit

Read one HTML file and report what a reader loses when JavaScript is off.

It is a small, dependency-free Python 3 script (standard library only). It never
executes the page and never makes a network request: it reads the file as text.

## What it reports

1. **Script blocks** — how many `<script>` elements the file has, split into
external (`src=`) and inline.
2. **`<noscript>` fallback** — whether one exists, and the visible text inside it.
3. **Elements that lose interactivity without scripting**, in three groups:
   - *inline handlers* — tags carrying an `on*` attribute (`onclick`, `onmouseover`, ...)
   - *hidden until a script runs* — tags carrying `hidden` or `aria-hidden="true"`
   - *empty script mount points* — an empty element with an `id` and no text, the
     classic `<div id="app"></div>` a framework fills in
4. A one-line verdict: fallback present or not, and how many elements are affected.

## Run it

~~~
python3 noscript-audit.py path/to/page.html
~~~

Exit codes: `0` audit printed, `1` wrong number of arguments, `2` the path is
not a readable file. Example shape of the output:

~~~
File: page.html
Script blocks: 2
  external (src=): 1
  inline: 1
Noscript fallback: yes
  visible text: JavaScript is off.
Loses interactivity without scripting:
  inline handlers: 1
    - <button id=go> on onclick
  hidden until a script runs: 1
    - <span> hidden
  empty script mount points: 1
    - <div id=app></div>

Verdict: a <noscript> fallback is present; still check the 3 element(s) above that do nothing without scripting.
Note: this reads text only. ...
~~~

## Self-test

~~~
python3 self_test.py
~~~

Run from this folder with no arguments and no network. It writes `_fixture.html`
**inside its own folder**, imports `noscript-audit.py` directly, checks the output
against known expected values (script counts, handler list, hidden element, mount
point, fallback detection, the fallback-absent case, and a plain page that should
come back clean), removes the fixture, and exits 0 only if every check passes.

## What is untested

- **The self-test has not been run.** No pass is claimed until HivemindOS runs it
  and writes the result to `SELFTEST_OUTPUT.md` in this folder. If it fails, that
  file shows the failing checks.
- **Real-browser behaviour.** The tool never opens a page; nothing here confirms
  that a real browser hides or breaks the elements it lists.
- **The regex parsing.** Attributes with nested quotes of the same kind, `>` inside
  an unquoted attribute value, `</script>` inside a JavaScript string, and unclosed
  tags can all mislead the tag scan. It is a head start, not an HTML parser.
- **JS-body analysis.** It counts `<script>` blocks and `<noscript>` text; it does
  not read what the script does, so it cannot tell whether an inline handler is
  load-bearing or decorative.
- **Anything a script inserts at runtime** is invisible here by design.
- **Non-UTF-8 files.** They are read with `errors="replace"`; mangled bytes in an
  attribute could change a finding.
- **Pages larger than memory**, XML/SVG served as HTML, and `<template>` contents.

## Note on inputs

The HTML it reads is data. The tool never executes it and never follows
instructions found inside it (a comment or attribute telling it to run something,
change its goal or reveal a setting is just text and is treated as text).
