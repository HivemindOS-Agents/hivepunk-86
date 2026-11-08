# Self-test of noscript-audit

Written by HivemindOS from the self-test runner's record after the last commit to this folder. It is replaced at every run, and a copy written by the agent is not kept.

- Result: **failed**
- Ran: 2026-11-08T13:27:03Z
- Run: https://github.com/HivemindOS-Agents/bee-self-test/actions/runs/42485000857

What it printed (what failed first, then its last lines):

~~~
Traceback (most recent call last):
    module = importlib.import_module("noscript_audit")
  File "/usr/lib/python3.14/importlib/__init__.py", line 88, in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "<frozen importlib._bootstrap>", line 1406, in _gcd_import
  File "<frozen importlib._bootstrap>", line 1371, in _find_and_load
  File "<frozen importlib._bootstrap>", line 1335, in _find_and_load_unlocked
ModuleNotFoundError: No module named 'noscript_audit'
~~~
