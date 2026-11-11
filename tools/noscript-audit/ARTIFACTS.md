# Superseded

This file described an earlier, differently shaped draft of the noscript-audit
tool and linked to that draft as "the tool". The draft and its shim are marked
superseded (noscript_audit.py, noscript-audit.py); neither carries audit logic
any more. This note is kept only as a marker, so an old link does not look live.

Two claims that used to sit here were wrong and are removed: that
noscript-audit.py was the tool, and that self_test.py writes a _fixture.html
inside this folder.

The artifact of record is the four files in this folder:

- nostrip_audit.py - reads one local HTML file, standard library only, no
  network. Prints one external-script: <url> line per distinct external script
  URL (http://, https://, protocol-relative //), a noscript-missing: line when
  external scripts exist and no <noscript> holding visible text does, then a
  summary: line. Exit 0 when the audit runs, 2 on usage or read error.
- fixture.html - the sample page the self-test runs the tool on.
- self_test.py - the offline self-test. Run it from inside this folder:
  python3 self_test.py
- README.md - what it does, how to run it, and what is untested.
- SELFTEST_OUTPUT.md - written by HivemindOS with the real output of a
  self-test run after each commit. Read the run state there; nothing committed
  in this repository is itself a captured run.

Deleting these three markers (noscript_audit.py, noscript-audit.py,
ARTIFACTS.md) would leave exactly the four files plus SELFTEST_OUTPUT.md. That
needs a commit that removes files, which this step cannot make.
