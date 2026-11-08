# Self-test of noscript-audit

Written by HivemindOS from the self-test runner's record after the last commit to this folder. It is replaced at every run, and a copy written by the agent is not kept.

- Result: **failed**
- Ran: 2026-11-08T14:31:33Z
- Run: https://github.com/HivemindOS-Agents/bee-self-test/actions/runs/42490209750

What it printed (what failed first, then its last lines):

~~~
ok  clean page: no findings
FAILED:
  <p> handler listed: got <re.Match object; span=(266, 280), match='<p> on onclick'>, expected True
  <button id=go> handler listed: got <re.Match object; span=(287, 316), match='<button id=go> on onmouseover'>, expected True
  hidden element found: got False, expected True
  hidden <span> listed: got None, expected True
  verdict warns when absent: got False, expected True
~~~
