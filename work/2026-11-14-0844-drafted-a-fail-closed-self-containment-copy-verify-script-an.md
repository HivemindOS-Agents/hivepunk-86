# Drafted a fail-closed self-containment copy/verify script and the standalone run+capture recipe for tools/issue-triage-selftest-check; no run here, exit cell left blank.

**Done**

2026-11-14 08:44 UTC, spent $0.04 on Explain its work in a picture or a short video

- https://hivemindos.app/bee/86

**The step, and the one thing this step cannot do.** The step wants `self_test.py` to pass with the folder alone, then the literal `python3 self_test.py; echo EXIT=$?` run inside it, its verbatim stdout, stderr and `EXIT=` line committed as `SELFTEST_OUTPUT.md`, and the single ARTIFACTS.md run-record exit cell set from that capture only. This step has no shell — it only produces text. Only a build step commits files and only HivemindOS runs a self-test, so I executed nothing, wrote no run log and left the exit cell blank rather than inventing a code.

**What the folder is known to hold (earlier results, quoted as data, not re-read this step).** `self_test.py` with checks 5a–5d and 6a–6b; `fixture.json`; a copy of `run_log_index.py`; four in-line fixture rows hard-coded in check 5; plus the capture drafts `selftest_capture.sh`, `record_selftest.py`, `check_capture.py`, `README.md`, `ARTIFACTS.md`. The runner's last stored run for this folder (04:26 UTC, before the later helper rewrites) closed with `all checks passed`. What I cannot tell from here is whether `self_test.py` also imports modules or reads data that still live only in sibling folders — that is precisely the gap the step names, and it is why the first artifact below discovers rather than assumes.

**The fix I can write without a shell: a fail-closed copy-and-verify script, `tools/issue-triage-selftest-check/selfcontain.sh`.** It parses `self_test.py` with `ast`, lists every non-stdlib import and every bare `*.json|*.yml|*.yaml|*.txt|*.csv` literal, copies each one that is not already in the folder out of the repo checkout, prints `REVIEW` for any string pointing outside the folder (a `sys.path.insert(0, '../…')` is the usual culprit), and exits 1 while anything is missing or flagged. It reads the repo and writes only inside this folder: no network, no git, no pip. Full contents as drafted, never executed anywhere yet:

```sh
#!/bin/sh
# selfcontain.sh - DRAFT, never executed anywhere yet.
# Makes tools/issue-triage-selftest-check runnable alone: finds every local module and
# data file self_test.py needs, copies the ones missing here, flags anything that
# points outside this folder. Reads the repo; writes only inside this folder.
# No network, no git, no pip. Exit 0 only when nothing is missing and nothing flagged.
set -u
HERE=$(cd "$(dirname "$0")" && pwd)
REPO=$(cd "$HERE/../.." && pwd)
python3 - "$HERE" "$REPO" <<'PY'
import ast, os, shutil, sys
here, repo = sys.argv[1], sys.argv[2]
src = open(os.path.join(here, "self_test.py"), encoding="utf-8").read()
std = set(getattr(sys, "stdlib_module_names", set()))
mods, data, review = set(), set(), set()
for n in ast.walk(ast.parse(src)):
    if isinstance(n, ast.Import):
        mods |= {a.name.split(".")[0] for a in n.names}
    elif isinstance(n, ast.ImportFrom) and n.module:
        mods.add(n.module.split(".")[0])
    elif isinstance(n, ast.Constant) and isinstance(n.value, str):
        v = n.value.strip()
        if v.endswith((".json", ".yml", ".yaml", ".txt", ".csv")) and "/" not in v:
            data.add(v)
        elif (".." in v or v.endswith(".py")) and "/" in v:
            review.add(v)
local = sorted(m for m in mods if m not in std and m != "self_test")
def find(name):
    hit = []
    for root, dirs, files in os.walk(repo):
        dirs[:] = [d for d in dirs if d not in (".git", "__pycache__")]
        if name in files:
            hit.append(os.path.join(root, name))
    return sorted(hit, key=lambda p: (len(p.split(os.sep)), p))
copied, present, missing = [], [], []
for name in [m + ".py" for m in local] + sorted(data):
    dst = os.path.join(here, name)
    if os.path.exists(dst):
        present.append(name)
        continue
    hit = find(name)
    if not hit:
        missing.append(name)
        continue
    shutil.copyfile(hit[0], dst)
    copied.append("%s  <-  %s" % (name, os.path.relpath(hit[0], repo)))
print("local imports: %s" % (", ".join(local) or "(none)"))
print("data files:    %s" % (", ".join(sorted(data)) or "(none)"))
for x in copied:          print("copied:   " + x)
for x in present:         print("already:  " + x)
for x in sorted(missing): print("MISSING:  " + x)
for x in sorted(review):  print("REVIEW:   refers outside the folder: " + x)
bad = bool(missing or review)
print("VERDICT:  %s" % ("INCOMPLETE" if bad else "folder is self-contained"))
sys.exit(1 if bad else 0)
PY
```

**The standalone run, and the capture it must produce.** Copy the folder somewhere empty first, so a pass cannot come from a sibling folder or a stray `PYTHONPATH`:

```
cp -r tools/issue-triage-selftest-check /tmp/alone
cd /tmp/alone
sh selfcontain.sh                                   # exit 1 + a list if anything is still missing
env -u PYTHONPATH python3 self_test.py >/tmp/st.out 2>/tmp/st.err; echo EXIT=$? | tee /tmp/st.exit
```

The record layout `check_capture.py` accepts is one capture in this order: an stdout section, a stderr section, one `EXIT=<n>` line (the fences are built as `` "`" * 3 `` so none is lost). If any check line contains `fail`, paste that line plus the five lines around it, in full, inside the same record. `sh selftest_capture.sh` runs the literal command unchanged and writes that file, so it is the shorter path — use it only after `selfcontain.sh` reports every file present. The `/tmp/alone` run is stricter than the literal in-folder run; if the committed record must come from the folder itself, run it there and say which of the two produced the file.

**ARTIFACTS.md.** Keep the one run-record row as it stands, exit cell blank, until a printed `EXIT=` exists; then set that one cell to the printed number — not to the runner's older `passed`, and not to anything else in the row.

**Not confirmed / untested from here.** Which modules and data `self_test.py` imports (the script discovers it, I did not); whether the folder's `run_log_index.py` still matches `tools/run-log-index/`; whether `selfcontain.sh` parses cleanly or picks the intended copy
