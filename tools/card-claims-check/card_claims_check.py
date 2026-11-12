#!/usr/bin/env python3
"""card-claims-check: classify HivemindOS agent-card rows as opened, empty or missing.

Usage:  python3 card_claims_check.py <file.csv>

Reads a CSV with columns (agent_id, card_text). For each row, prints one line:
    <agent_id>: opened | empty | missing

Classifications:
  - opened:   card_text has non-whitespace content
  - empty:    card_text is present but blank or whitespace-only
  - missing:  the row has no card_text column at all (an empty string is empty, not missing)

Exit 0 on success; 2 on usage or read error.
"""

import csv
import sys

USAGE = "usage: card_claims_check.py <file.csv>"


def classify_row(row):
    """Return (agent_id, label) for one CSV row dict.

    Handles rows where 'card_text' may be missing entirely (missing),
    present-but-empty (empty), or has non-blank text (opened).
    """
    agent_id = row.get("agent_id", "").strip()
    card_text = row.get("card_text", None)
    if card_text is None:
        label = "missing"
    elif card_text.strip() == "":
        label = "empty"
    else:
        label = "opened"
    return agent_id, label


def classify_csv(path):
    """Yield (agent_id, label) for every row in the CSV at *path*."""
    with open(path, "r", encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            yield classify_row(row)


def main(argv):
    if len(argv) != 2:
        print(USAGE, file=sys.stderr)
        return 2
    try:
        results = list(classify_csv(argv[1]))
    except (OSError, csv.Error) as exc:
        print("card-claims-check: cannot read %s: %s" % (argv[1], exc), file=sys.stderr)
        return 2
    counts = {"opened": 0, "empty": 0, "missing": 0}
    for agent_id, label in results:
        print("%s: %s" % (agent_id, label))
        counts[label] += 1
    print("summary: %d opened, %d empty, %d missing" % (
        counts["opened"], counts["empty"], counts["missing"]))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
