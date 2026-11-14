# Self-test of issue-triage-selftest-check

Written by HivemindOS from the self-test runner's record after the last commit to this folder. It is replaced at every run, and a copy written by the agent is not kept.

- Result: **passed**
- Ran: 2026-11-14T04:26:57Z
- Run: https://github.com/HivemindOS-Agents/bee-self-test/actions/runs/43556684955

What it printed (what failed first, then its last lines):

~~~
ok   5a. malformed fixture --check exits 1
ok   5b. malformed stderr names the three bad rows in order
ok   5c. malformed stderr does not name the good row
ok   5d. malformed stdout holds only rows with valid URL and folder
ok   6a. missing file exits 2
ok   6b. missing file mentions cannot read on stderr
all checks passed
~~~
