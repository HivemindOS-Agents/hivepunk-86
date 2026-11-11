# card-claims-check

Classify HivemindOS agent-card rows from a CSV as **opened**, **empty** or **missing**. Standard library only, no network.

## What it does

Reads a CSV with columns `agent_id` and `card_text`. For each row prints one line:

    <agent_id>: opened | empty | missing

Then a summary count line:

    summary: <N> opened, <N> empty, <N> missing

**Classifications**

| label     | rule                                                                 |
|-----------|----------------------------------------------------------------------|
| `opened`  | `card_text` has non-whitespace content (one or more printable chars) |
| `empty`   | `card_text` exists but is blank or whitespace-only                   |
| `missing` | `card_text` is absent (empty string or the column is missing)       |

## Usage

    python3 card_claims_check.py path/to/cards.csv

Exit codes: `0` — success; `2` — wrong argument count or unreadable path (message on stderr).

## Exact expected output for the bundled `fixture.csv`

    alice: opened
    bob: empty
    charlie: missing
    Diana: empty
    eve: opened
    frank: empty
    grace: opened
    heidi: opened
    summary: 3 opened, 3 empty, 1 missing

`fixture.csv` covers:

| row     | card_text                           | classification | reason                                   |
|---------|-------------------------------------|----------------|------------------------------------------|
| alice   | `"Hello, I am Agent Alice."`       | opened         | normal text                              |
| bob     | `""`                                | empty          | blank string                             |
| charlie | `missing` (literal word in CSV)    | missing        | no `card_text` column at all             |
| Diana   | `"   "` (3 spaces)                 | empty          | whitespace-only                          |
| eve     | `"I am Eve, ready to assist."`     | opened         | normal text                              |
| frank   | `"\n  "` (newline + 2 spaces)     | empty          | whitespace-only                          |
| grace   | multi-line text                     | opened         | non-blank content                        |
| heidi   | `---`                               | opened         | dashes are visible text (not a blank)    |

## Self-test

    python3 self_test.py

Run from inside this folder with no arguments. It loads the tool via `importlib.util` and checks:

1. the tool on `fixture.csv` produces exactly the 9 lines above, exit 0, quiet stderr;
2. a row with "hello" is classified `opened`;
3. a row with an empty string is `empty`;
4. a row missing the `card_text` key is `missing`;
5. a row with whitespace-only text is `empty`;
6. a multi-line row is `opened`;
7. a row with only tab characters is `empty`;
8. no argument prints `usage:` on stderr and exits 2;
9. a missing file path prints `cannot read` on stderr and exits 2.

It exits 0 only when every check passes.

## What is untested

- Real-world CSV files with BOMs, irregular quoting, or mixed line endings.
- Non-UTF-8 encodings (the CSV reader uses the default system encoding).
- Very large files (the whole file is read into memory via `list(classify_csv(...))`).
- Verification against a live agent-card dataset: the tool's output matches the fixture, not a specific external set of cards.
- The case where `card_text` contains only invisible control characters other than whitespace (e.g. null bytes).
