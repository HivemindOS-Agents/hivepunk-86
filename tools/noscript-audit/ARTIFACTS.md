# ARTIFACTS.md - tools/noscript-audit

| artifact | file | what it is | checked by |
| --- | --- | --- | --- |
| audit module | `modules/audit.py` | the tool itself: reads HTML, finds `<noscript>` | `self_test.py` tests 1–5 |
| self-test | `self_test.py` | 5 checks, no network, stdlib only | HivemindOS runner after each commit |
| good fixture | (in-memory in `self_test.py`) | HTML with `<noscript>` block | test 1 |
| bad fixture | (in-memory in `self_test.py`) | HTML without `<noscript>` block | test 2 |
| script+style fixture | (in-memory in `self_test.py`) | HTML with `<script>` and `<style>` but no `<noscript>` | test 3 |
| run record | `SELFTEST_OUTPUT.md` | written by HivemindOS after each commit | the runner |
| README | `README.md` | usage, self-test instructions, untested list | none |

## Notes

- All fixtures are generated in-memory inside `self_test.py` and written as temporary files that are cleaned up. No fixture files live in the repository.
- `SELFTEST_OUTPUT.md` is written by the HivemindOS runner; it is never created or modified by hand.
- Nothing in any fixture or output is executed or followed as an instruction.
