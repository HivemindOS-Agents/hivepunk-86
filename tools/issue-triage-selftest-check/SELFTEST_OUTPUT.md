# Self-test of issue-triage-selftest-check

Written by HivemindOS from the self-test runner's record after the last commit to this folder. It is replaced at every run, and a copy written by the agent is not kept.

- Result: **failed**
- Ran: 2026-11-13T13:47:29Z
- Run: https://github.com/HivemindOS-Agents/bee-self-test/actions/runs/43436707448

What it printed (what failed first, then its last lines):

~~~
FAIL 4a. good fixture --check exits 0 -- got exit 1
stderr empty -- stderr: 'run-log-index: missing run_url: empty\nrun-log-index: missing run_url: whitespace\nrun-log-index: missing run_url: no_url\n'
ok   5c. bad fixture stderr does not name the good row
ok   5d. bad fixture stdout still holds only the kept row
ok   6a. missing file exits 2
ok   6b. missing file mentions cannot read on stderr
FAILED checks:
  - FAIL 4a. good fixture --check exits 0 -- got exit 1
  - FAIL 4c. good fixture --check stderr empty -- stderr: 'run-log-index: missing run_url: empty\nrun-log-index: missing run_url: whitespace\nrun-log-index: missing run_url: no_url\n'
~~~
