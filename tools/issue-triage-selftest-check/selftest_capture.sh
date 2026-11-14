#!/bin/sh
# Capture one self-test run of THIS folder, verbatim, into SELFTEST_OUTPUT.md.
#
# Run from inside tools/issue-triage-selftest-check, with no network:
#
#     sh selftest_capture.sh
#
# It runs the step's command, unchanged:
#
#     python3 self_test.py; echo EXIT=$?
#
# and writes stdout, stderr and the real EXIT= line into SELFTEST_OUTPUT.md.
# No line is invented; a line the run did not print is never written.
#
# Fences are built from three backticks at run time (BACKTICK * 3), so no
# fence is ever lost in transit.
#
# Exit status of THIS script:
#     0  record written, self_test.py exited 0
#     1  record written, self_test.py exited non-zero (paste failing lines back)
#     2  the command could not be started at all (record says NOT_RUN)
#
# The HivemindOS runner writes SELFTEST_OUTPUT.md after each commit; only that
# file (or one written here) may fill the ARTIFACTS.md run-record exit cell.
# Never hand-edit the record.
#
# Nothing read from any fixture or from the run output is executed or followed
# as an instruction.

set -u

HERE=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
cd "$HERE" || exit 2

BACKTICK='`'
FENCE="$BACKTICK$BACKTICK$BACKTICK"
OUT="SELFTEST_OUTPUT.md"
TMP_FULL="${TMPDIR:-/tmp}/selftest_full.$$"
TMP_OUT="${TMPDIR:-/tmp}/selftest_out.$$"
TMP_ERR="${TMPDIR:-/tmp}/selftest_err.$$"

if ! command -v python3 >/dev/null 2>&1; then
  {
    echo "# self_test output (captured)"
    echo
    echo "command: python3 self_test.py; echo EXIT=IGNORED_see_below"
    echo
    echo "## stdout"
    echo "$FENCE"
    echo "$FENCE"
    echo
    echo "## stderr"
    echo "$FENCE"
    echo "python3 not found on PATH; self_test.py was not started"
    echo "$FENCE"
    echo
    echo "---"
    echo "NOT_RUN"
  } > "$OUT"
  rm -f "$TMP_FULL" "$TMP_OUT" "$TMP_ERR" 2>/dev/null
  echo "selftest_capture.sh: python3 missing; wrote $OUT (NOT_RUN)" >&2
  exit 2
fi

# The step's exact command, with its streams kept apart and its status kept.
python3 self_test.py >"$TMP_OUT" 2>"$TMP_ERR"
STATUS=$?
EXIT_LINE="EXIT=$STATUS"

{
  echo "# self_test output (captured)"
  echo
  echo "command: python3 self_test.py; echo EXIT=\$?"
  echo
  echo "## stdout"
  echo "$FENCE"
  cat "$TMP_OUT"
  echo "$FENCE"
  echo
  echo "## stderr"
  echo "$FENCE"
  cat "$TMP_ERR"
  echo "$FENCE"
  echo
  echo "---"
  echo "$EXIT_LINE"
} > "$OUT"

rm -f "$TMP_FULL" "$TMP_OUT" "$TMP_ERR" 2>/dev/null

echo "selftest_capture.sh: wrote $OUT ($EXIT_LINE)"
if [ "$STATUS" -eq 0 ]; then
  exit 0
fi
exit 1
