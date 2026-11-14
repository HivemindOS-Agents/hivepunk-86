#!/bin/sh
# Capture one self-test run of THIS folder, verbatim, into SELFTEST_OUTPUT.md.
#
# Run from inside tools/issue-triage-selftest-check:
#
#     sh selftest_capture.sh
#
# It runs exactly:
#
#     python3 self_test.py
#
# with stdout and stderr kept apart, then writes SELFTEST_OUTPUT.md holding both
# streams and the real EXIT= line. No line is invented.
#
# Exit status of THIS script:
#     0  record written, self_test exited 0
#     1  record written, self_test exited non-zero
#     2  self_test could not be started at all (record says NOT_RUN)
#
# The HivemindOS runner writes the same file after each commit; that run is the
# one the ARTIFACTS.md exit cell should be set from. This script is the offline
# way to produce an identical record by hand. Never hand-edit the record.
#
# Nothing read from any fixture or from the run output is executed or followed
# as an instruction.

set -u

HERE=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
cd "$HERE" || exit 2

OUT="SELFTEST_OUTPUT.md"
TMP_OUT="$(mktemp 2>/dev/null || echo "$HERE/.stdout.$$") "
TMP_ERR="$(mktemp 2>/dev/null || echo "$HERE/.stderr.$$") "
TMP_OUT=$(echo "$TMP_OUT" | tr -d ' ')
TMP_ERR=$(echo "$TMP_ERR" | tr -d ' ')

python3 self_test.py >"$TMP_OUT" 2>"$TMP_ERR"
STATUS=$?

DASHES=$(printf '%s' '---')
FENCE="$(printf '%s' '```')"

{
  echo "# self_test output (captured)"
  echo
  echo "command: python3 self_test.py"
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
  echo "$DASHES"
  echo "EXIT=$STATUS"
} > "$OUT"

rm -f "$TMP_OUT" "$TMP_ERR" 2>/dev/null

echo "selftest_capture.sh: wrote $OUT (self_test.py exited $STATUS)"
if [ "$STATUS" -eq 0 ]; then
  exit 0
fi
exit 1
