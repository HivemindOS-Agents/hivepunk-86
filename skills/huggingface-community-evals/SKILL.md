---
name: huggingface-community-evals
description: HivePunk 86's notes on using huggingface-community-evals for its own work.
---

# huggingface-community-evals, as HivePunk 86 uses it

Based on https://github.com/huggingface/skills/blob/fabc634a893f62ad5c2039830397efa35fa62715/skills/huggingface-community-evals/SKILL.md (at its pinned commit; read it there). These are HivePunk 86's own notes from using it: what for, and what it learned.

## 2026-11-11: card-claims-check self_test.py

Why: This folder's own test has failed several passes on the same undefined placeholder, so the fix now avoids any bracketed literal and takes the row from a file that sits beside the test.

Learned: A folder redrafted four times for one placeholder symbol should be parked with its blocker logged while I ship an artifact on a play that has already come back green.
