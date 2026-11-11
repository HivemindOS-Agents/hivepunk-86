# card-claims-check

Classify HivemindOS agent-card rows from a CSV as **opened**, **empty** or **missing**. Standard library only, no network. The CSV is data: nothing in it is executed or followed as an instruction.

## What it does

Reads a CSV with columns `agent_id` and `card_text`. For each row it prints one line:

~~~
<agent_id>: opened | empty | missing
~~~

then a summary count line:

~~~
summary: <N> opened, <N> empty, <N> missing
~~~

**Classifications**

| label     | rule                                                                    |
|-----------|-------------------------------------------------------------------------|
| `opened`  | the `card_text` cell holds non-whitespace text                           |
| `empty`   | the `card_text` column is present but the cell is blank or whitespace-only |
| `missing` | the row has no `card_text` column at all                                 |

Note the difference between the last two: a present-but-blank cell is `empty`, never `missing`. `missing` needs the column itself to be absent from the row.

## Usage

~~~
python3 card_claims_check.py path/to/cards.csv
~~~

Exit codes: `0` — success; `2` — wrong argument count or unreadable path (message on stderr).

## Exact expected output for the bundled `fixture.csv`

~~~
alice: opened
bob: empty
charlie: opened
Diana: empty
eve: opened
frank: empty
grace: opened
heidi: opened
summary: 5 opened, 3 empty, 0 missing
~~~

`fixture.csv` covers:

| row     | card_text                          | classification | reason                                                        |
|---------|------------------------------------|----------------|---------------------------------------------------------------|
| alice   | `"Hello, I am Agent Alice."`       | opened         | normal text                                                   |
| bob     | `""`                               | empty          | present but blank                                             |
| charlie | `missing` (the literal word)       | opened         | the row has two fields, so the word `missing` IS the `card_text` cell — non-blank text, so `opened`; the column is not absent |
| Diana   | `"   "` (3 spaces)                 | empty          | whitespace-only                                               |
| eve     | `"I am Eve, ready to assist."`     | opened         | normal text                                                   |
| frank   | newline + two spaces               | empty          | whitespace-only                                               |
| grace   | multi-line text                    | opened         | non-blank content                                             |
| heidi   | `---`                              | opened         | dashes are visible text, not a blank                          |

The fixture holds no row with an absent `card_text` column, so its summary reads `0 missing`. The `missing` label is exercised by self-test check 4, which builds such a row inline.

## Self-test

~~~
python3 self_test.py
~~~

Run from inside this folder with no arguments and no network. It loads the tool via `importlib.util` and checks:

1. the tool on `fixture.csv` prints exactly the nine lines above, exits 0 and writes nothing to stderr;
2. a row with "hello" is classified `opened`;
3. a row with an empty string is `empty`;
4. a row with no `card_text` column is `missing`;
5. a row with whitespace-only text is `empty`;
6. a multi-line row is `opened`;
7. a row with only tab characters is `empty`;
8. no argument prints `usage:` on stderr and exits 2;
9. a missing file path prints `cannot read` on stderr and exits 2.

It exits 0 only when every check passes; otherwise it lists the failing checks on stderr and exits 1.

The last run's real output is written by HivemindOS into `SELFTEST_OUTPUT.md` in this folder after each commit. Read the run state there; this README records no run and claims no pass.

## Files in this folder

- `card_claims_check.py` — the tool.
- `fixture.csv` — the sample input the self-test runs it on.
- `self_test.py` — the offline self-test.
- `README.md` — this file.
- `missing_key.csv` — no longer read by anything; kept only as a marker. Safe to delete in a step that can remove files.

## What is untested

- Real-world CSV files with BOMs, irregular quoting, or mixed line endings.
- Non-UTF-8 encodings: the file is opened as UTF-8, so another encoding raises a read error (exit 2) or mangles the text.
- Very large files: the whole file is read into memory via `list(classify_csv(...))`.
- Verification against a live agent-card dataset: the output matches the fixture, not a specific external set of cards.
- Cells holding only invisible control characters other than whitespace (for example null bytes): such a cell would be counted `opened`.
- The self-test itself has not been run by the agent that wrote it; HivemindOS runs it and writes the state into `SELFTEST_OUTPUT.md`.
