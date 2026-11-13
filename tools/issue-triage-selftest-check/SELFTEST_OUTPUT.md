# Self-test of issue-triage-selftest-check

Written by HivemindOS from the self-test runner's record after the last commit to this folder. It is replaced at every run, and a copy written by the agent is not kept.

- Result: **failed**
- Ran: 2026-11-13T15:53:30Z
- Run: https://github.com/HivemindOS-Agents/bee-self-test/actions/runs/43457092174

What it printed (what failed first, then its last lines):

~~~
ok   5b. malformed stderr names the three bad rows in order
ok   5c. malformed stderr does not name the good row
FAIL 5d. malformed stdout holds only rows with valid URL and folder -- stdout: '[]\n'
ok   6a. missing file exits 2
ok   6b. missing file mentions cannot read on stderr
FAILED checks:
  - FAIL 5d. malformed stdout holds only rows with valid URL and folder -- stdout: '[]\n'
~~~
