# noscript-audit

A command-line tool that checks one or more HTML files for the presence of a `<noscript>` block. Useful for verifying that each page in a web project has a fallback message for users with JavaScript disabled.

## Usage

```
python3 -m modules.audit index.html about.html contact.html
```

For each file:
- If it contains a `<noscript>...</noscript>` element, prints `OK: <filename>` on stdout.
- If it does NOT contain `<noscript>`, prints `noscript-audit: missing <noscript> in <filename>` on stderr and the final exit code is 1.
- If the file cannot be read (missing, not UTF-8, etc.), prints an error on stderr and exits 2 immediately.

Exit codes:
- 0: all files contain a `<noscript>` block.
- 1: one or more files lack `<noscript>`.
- 2: usage error or I/O error.

## Self-test

```
python3 self_test.py
```

Run from inside this folder. No network or external files needed. Tests:
1. Good fixture with `<noscript>` – detected.
2. Bad fixture without `<noscript>` – reported as missing.
3. Fixture with `<script>` and `<style>` but no `<noscript>` – still reported as missing.
4. Missing file – returns None.
5. Main exit codes: 0 for good fixture, 1 for bad fixture, 2 for missing file, 2 for no arguments.

## What is untested

- Files that are not valid UTF-8 (e.g., Latin-1 or binary files). The tool attempts to open with `utf-8` encoding and would print an error on stderr and exit 2.
- Files with deeply nested or malformed HTML (e.g., unclosed tags, out-of-order nesting). The built-in `html.parser` is reasonably tolerant but edge cases may differ from a browser's parsing.
- Running the tool as a script (`python3 modules/audit.py ...`) rather than a module. The `__main__` guard is present but only `python3 -m modules.audit ...` is documented.
