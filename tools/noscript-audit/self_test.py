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


def cli(*args):
    return subprocess.run([sys.executable, TOOL] + list(args),
                          capture_output=True, text=True)


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
    lines = mod.audit_lines('<script src="https://cdn.test/a.js"></script>'
                            '<noscript>Enable JavaScript.</noscript>')
    want = ['external-script: https://cdn.test/a.js',
            'summary: 1 external script(s), noscript present']
    if lines != want:
        failures.append('fallback present: want %r, got %r' % (want, lines))

    # 3. Relative and inline scripts are not external; an empty <noscript> is missing.
    lines = mod.audit_lines('<script src="app.js"></script>'
                            '<script>run()</script><noscript></noscript>')
    want = ['summary: 0 external script(s), noscript missing']
    if lines != want:
        failures.append('relative/inline/empty: want %r, got %r' % (want, lines))

    # 4. A <noscript> holding only a nested <script> has no visible text, so the
    #    fallback counts as missing; the nested script is not a dependency.
    lines = mod.audit_lines('<noscript>'
                            '<script src="https://cdn.test/fallback.js"></script>'
                            '</noscript>')
    want = ['summary: 0 external script(s), noscript missing']
    if lines != want:
        failures.append('noscript with only a nested script: want %r, got %r'
                        % (want, lines))

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
