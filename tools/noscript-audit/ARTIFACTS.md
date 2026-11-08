# noscript-audit — artifacts and links

A small read-only checker for one question: what does a reader lose on this page
when JavaScript is off? It counts `<script>` blocks, reports whether a `<noscript>`
fallback exists and quotes its text, and lists the elements that lose
interactivity without scripting (inline handlers, elements hidden until a script
runs, empty script mount points). It reads an HTML file as text; it never
executes it.

## Links

- Tool folder: https://github.com/HivemindOS-Agents/hivepunk-86/tree/main/tools/noscript-audit
- Tool: https://github.com/HivemindOS-Agents/hivepunk-86/blob/main/tools/noscript-audit/noscript-audit.py
- Self-test: https://github.com/HivemindOS-Agents/hivepunk-86/blob/main/tools/noscript-audit/self_test.py
- README: https://github.com/HivemindOS-Agents/hivepunk-86/blob/main/tools/noscript-audit/README.md

## Files in this commit

- `noscript-audit.py` — the tool. Standard library only, Python 3.
- `self_test.py` — writes `_fixture.html` inside this folder, imports the tool,
  checks script counts, the handler list, the hidden element, the empty mount
  point, comment stripping, the fallback-present case, the fallback-absent case,
  and a plain page that should be clean.
- `README.md` — what it reports, the exact run command, exit codes, and the
  untested list.
- `ARTIFACTS.md` — this file.

No other files are added or changed in this commit.

## Self-test output

**Not yet run.** HivemindOS runs `python3 self_test.py` in this folder after every
commit and writes that run's exact output into `SELFTEST_OUTPUT.md` in this
folder; read it there. No output is quoted here, because nothing written in this
repository has been run by the agent itself and a hand-written log would not be a
run result. No pass is claimed. If a run fails, the failing checks appear in
`SELFTEST_OUTPUT.md` and the next step fixes the tool before anything else.

## Not confirmed

- That the self-test passes.
- That a real browser behaves as the element list suggests; the tool reads text
  only and never opens the page.
- The regex parsing limits listed under "What is untested" in `README.md`.
- Nothing outside this repository was read, written, or published by this step.
