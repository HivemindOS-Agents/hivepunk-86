#!/usr/bin/env python3
import subprocess, json, sys, textwrap

def run_node_code(js_code):
    try:
        result = subprocess.run(['node', '-e', js_code], capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print('Node error:', e.stderr, file=sys.stderr)
        sys.exit(1)

def main():
    hex_val = '#FF00FF'
    expected = [255, 0, 255]
    js = textwrap.dedent(f"""
        const {{hexToRgb}} = require('./script.js');
        console.log(JSON.stringify(hexToRgb('{hex_val}')));
    """)
    out = run_node_code(js)
    try:
        result = json.loads(out)
    except json.JSONDecodeError:
        print('Failed to parse JSON from node output:', out, file=sys.stderr)
        sys.exit(1)
    if result != expected:
        print('Result mismatch: got', result, 'expected', expected, file=sys.stderr)
        sys.exit(1)
    # Test 3‑digit shorthand
    js = textwrap.dedent("""
        const {hexToRgb} = require('./script.js');
        console.log(JSON.stringify(hexToRgb('#FFF')));
    """)
    out = run_node_code(js)
    try:
        result = json.loads(out)
    except json.JSONDecodeError:
        print('Failed to parse JSON from node output:', out, file=sys.stderr)
        sys.exit(1)
    if result != [255, 255, 255]:
        print('Invalid hex handling mismatch: got', result, file=sys.stderr)
        sys.exit(1)
    sys.exit(0)

if __name__ == '__main__':
    main()
