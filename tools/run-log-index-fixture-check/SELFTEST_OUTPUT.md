# Self-test of run-log-index-fixture-check

Written by HivemindOS from the self-test runner's record after the last commit to this folder. It is replaced at every run, and a copy written by the agent is not kept.

- Result: **passed**
- Ran: 2026-11-12T22:07:57Z
- Run: https://github.com/HivemindOS-Agents/bee-self-test/actions/runs/43316970383

What it printed (what failed first, then its last lines):

~~~
eck-blank-url'
ok   4b. stderr names the empty-url row -- exit 1, stderr 'run-log-index: missing run_url: fixture-check-empty-url\nrun-log-index: missing run_url: fixture-check-blank-url'
ok   4c. stderr names the blank-url row -- exit 1, stderr 'run-log-index: missing run_url: fixture-check-empty-url\nrun-log-index: missing run_url: fixture-check-blank-url'
ok   4d. stderr does not name the good row -- exit 1, stderr 'run-log-index: missing run_url: fixture-check-empty-url\nrun-log-index: missing run_url: fixture-check-blank-url'
ok   4e. stdout still holds only the kept row
all checks passed
~~~
