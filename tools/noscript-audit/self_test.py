#!/usr/bin/env python3
'''Offline self-test for nostrip_audit.py. Standard library only, no network.

Run from inside this folder:  python3 self_test.py
Exits 0 only when every check passes.
'''

import importlib.util
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TOOL = os.path.join(HERE, 'nostrip_audit.py')
FIXTURE = os.path.join(HERE, 'fixture.html')

EXPECTED = (
    'external-script: https://cdn.example.com/analytics.js\n'
    'external-script: //cdn.example.com/analytics.js\n'
    'external-script: https://cdn.example.com/app.js\n'
    'noscript-missing: 3 external script(s) and no <noscript> fallback\n'
    'summary: 3 external script(s), noscript missing\n'
)

# Load the tool's own module so audit_lines() can be checked directly.
spec = importlib.util.spec_from_file_location('nostrip_audit', TOOL)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

MISSING_1 = 'noscript-missing: 1 external script(s) and no <noscript> fallback'
MISSING_2 = 'noscript-missing: 2 external script(s) and no <noscript> fallback'
SUM_0_MISSING = 'summary: 0 external script(s), noscript missing'
SUM_0_PRESENT = 'summary: 0 external script(s), noscript present'
SUM_1_MISSING = 'summary: 1 external script(s), noscript missing'
SUM_1_PRESENT = 'summary: 1 external script(s), noscript present'
SUM_2_MISSING = 'summary: 2 external script(s), noscript missing'
A_TEST = 'https://a.test/x.js'


def cli(*args):
    return subprocess.run([sys.executable, TOOL] + list(args),
                          capture_output=True, text=True)


def expect(failures, label, html, want):
    got = mod.audit_lines(html)
    if got != want:
        failures.append('%s: want %r, got %r' % (label, want, got))


def run():
    failures = []

    # 1. The tool on the in-folder fixture: exit 0, exact stdout, quiet stderr.
    out = cli(FIXTURE)
    if out.returncode != 0:
        failures.append('fixture: exit %d, expected 0' % out.returncode)
    if out.stdout != EXPECTED:
        failures.append('fixture stdout mismatch\nexpected:\n%s\ngot:\n%s'
                        % (EXPECTED, out.stdout))
    if out.stderr != '':
        failures.append('fixture stderr not empty: %r' % out.stderr)

    # 2. A usable <noscript> fallback: no noscript-missing line.
    expect(failures, 'fallback present',
           '<script src="https://cdn.test/a.js"></script>'
           '<noscript>Enable JavaScript.</noscript>',
           ['external-script: https://cdn.test/a.js', SUM_1_PRESENT])

    # 3. Relative and inline scripts are not external; an empty <noscript> is missing.
    expect(failures, 'relative/inline/empty',
           '<script src="app.js"></script>'
           '<script>run()</script><noscript></noscript>',
           [SUM_0_MISSING])

    # 4. A <noscript> holding only a nested <script> has no visible text, so the
    #    fallback counts as missing; the nested script is not a dependency.
    expect(failures, 'noscript with only a nested script',
           '<noscript>'
           '<script src="https://cdn.test/fallback.js"></script>'
           '</noscript>',
           [SUM_0_MISSING])

    # 5. No argument: usage message on stderr, exit 2.
    out = cli()
    if out.returncode != 2:
        failures.append('no argument: exit %d, expected 2' % out.returncode)
    if not out.stderr.startswith('usage:'):
        failures.append('no argument stderr: %r' % out.stderr)

    # 6. Unreadable path: message on stderr, exit 2.
    out = cli(os.path.join(HERE, 'no-such-file.html'))
    if out.returncode != 2:
        failures.append('missing file: exit %d, expected 2' % out.returncode)
    if 'cannot read' not in out.stderr:
        failures.append('missing file stderr: %r' % out.stderr)

    # 7. A URL listed twice is reported once; an upper-case scheme still counts.
    expect(failures, 'duplicate and upper-case scheme',
           '<script src="http://a.test/x.js"></script>'
           '<script src="http://a.test/x.js"></script>'
           '<script src="HTTPS://b.test/y.js"></script>',
           ['external-script: http://a.test/x.js',
            'external-script: HTTPS://b.test/y.js',
            MISSING_2, SUM_2_MISSING])

    # 8. A <noscript> holding only whitespace has no visible text: missing.
    expect(failures, 'whitespace-only noscript',
           '<script src="%s"></script><noscript>  \n\t </noscript>' % A_TEST,
           ['external-script: %s' % A_TEST, MISSING_1, SUM_1_MISSING])

    # 9. A <script> inside an HTML comment is not a dependency.
    expect(failures, 'script inside a comment',
           '<!-- <script src="https://ignored.test/x.js"></script> -->'
           '<script src="%s"></script>' % A_TEST,
           ['external-script: %s' % A_TEST, MISSING_1, SUM_1_MISSING])

    # 10. Two <noscript> blocks, one with text: the fallback is present.
    expect(failures, 'one of two noscripts has text',
           '<script src="%s"></script>'
           '<noscript></noscript>'
           '<noscript>Please enable JS.</noscript>' % A_TEST,
           ['external-script: %s' % A_TEST, SUM_1_PRESENT])

    # 11. Empty, blank and valueless src are skipped; text nested inside tags
    #     within <noscript> still counts as visible text.
    expect(failures, 'empty src and nested noscript text',
           '<script src=""></script><script src="  "></script>'
           '<script src></script>'
           '<noscript><p>Enable <b>JS</b></p></noscript>',
           [SUM_0_PRESENT])

    return failures


if __name__ == '__main__':
    problems = run()
    if problems:
        print('FAILED checks:', file=sys.stderr)
        for p in problems:
            print('  - ' + p, file=sys.stderr)
        sys.exit(1)
    print('all checks passed')
    sys.exit(0)
