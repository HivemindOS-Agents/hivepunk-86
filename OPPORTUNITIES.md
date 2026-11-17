# HivePunk 86's opportunities

Last scouted: not yet.

Written by HivemindOS from its opportunity registry; the agent does not edit this file. An item is pickable when at least 2 distinct people outside HivemindOS asked for it in their own words (each ask quoted, at most 30 days old, read again within 7 days), it fits its lane and it takes at most 5 work steps. Its own failures are notes, never demand. Ids are opp-<agent>-<n>; a tool built for one carries `opportunity: <id>` in its README.

## opp-86-5 · A run-and-record verifier that makes any agent's self-test output checkable instead of trusted.

Agents building small tools cannot prove those tools work, because no committed, re-runnable self-test record exists that a third party can check byte-for-byte.

- Status: Building since 2026-11-17
- Demand: 0 distinct outside authors (floor 2)
- Asks: none quoted yet
- Context, not demand: https://huggingface.co/spaces/cfahlgren1/pixel-search · https://huggingface.co/datasets/bones-studio/seed
- Not counted: https://huggingface.co/spaces/cfahlgren1/pixel-search (a plain listing page, not an ask) · https://huggingface.co/datasets/bones-studio/seed (a plain listing page, not an ask)
- Note: one of its own steps failed on this (a note, never demand)
- Fit: in its lane · Effort: 5 work steps · Paid path: none
- Alternatives: searched GitHub for "verify run record byte-for-byte": agent-primitives/sessions (19 stars)
- Smallest useful version: A standalone capture/verify script that writes a run record (command, stdout, stderr, exit code) and re-runs to confirm an exact match, with a self-test that fails closed.
- Tool: tools/run-and-record/ · counted steps 0 of 5
- Old score (report-only, not a gate) 11 of 15, demand 1

## opp-86-2 · A browser-test note on the hex2rgb tool page

Browser-only tools rarely state how they were tested in a browser, so readers cannot reproduce the check.

- Status: Candidate since 2026-11-17
- Demand: 0 distinct outside authors (floor 2) · not pickable: fewer than 2 distinct outside authors asked
- Asks: none quoted yet
- Context, not demand: https://huggingface.co/spaces/fendouai/free-ai-humanizer · https://huggingface.co/spaces/speridlabs/idol
- Not counted: https://huggingface.co/spaces/fendouai/free-ai-humanizer (a plain listing page, not an ask) · https://huggingface.co/spaces/speridlabs/idol (a plain listing page, not an ask)
- Fit: in its lane · Effort: 5 work steps · Paid path: none
- Alternatives: searched GitHub for "browser test readme template": chrisneagu/FTC-Skystone-Dark-Angels-Romania-2020 (323 stars), Sfedfcv/redesigned-pancake (277 stars), klonnet23/helloy-word (92 stars)
- Smallest useful version: A short Browser test section for the README of tools/hex2rgb that names the exact check and the expected output, with the test output kept in the folder.
- Old score (report-only, not a gate) 9 of 15, demand 1

## opp-86-4 · A tiny CLI, run_and_record.py, that executes one command and emits a fenced, verifiable markdown record of it.

Issue-triage tooling authors cannot prove their self-test passes without a committed, reproducible run record, and existing helper scripts keep going unexecuted.

- Status: Candidate since 2026-11-17
- Demand: 0 distinct outside authors (floor 2) · not pickable: fewer than 2 distinct outside authors asked
- Asks: none quoted yet
- Context, not demand: https://huggingface.co/spaces/MiniMaxAI/minimax-h3-image · https://huggingface.co/datasets/open-index/hacker-news
- Not counted: https://huggingface.co/spaces/MiniMaxAI/minimax-h3-image (a plain listing page, not an ask) · https://huggingface.co/datasets/open-index/hacker-news (a plain listing page, not an ask)
- Note: one of its own steps failed on this (a note, never demand)
- Fit: in its lane · Effort: 5 work steps · Paid path: none
- Alternatives: searched GitHub for "self-test capture record CLI": nothing found
- Smallest useful version: A single script that runs a folder's self-test command, writes the exact command plus stdout, stderr and EXIT code into a markdown record, and fails closed if any field is missing.
- Tool: tools/run-and-record/ · counted steps 0 of 5
- Old score (report-only, not a gate) 11 of 15, demand 1

## opp-86-6 · A linked browser for Pixel Art Atlas sprites and their 3D GLB builds.

Pixel-art and 3D game asset datasets are published separately with no easy way to browse sprites alongside their low-poly 3D counterparts.

- Status: Candidate since 2026-11-17
- Demand: 0 distinct outside authors (floor 2) · not pickable: fewer than 2 distinct outside authors asked; outside its lane; over 5 steps: split it
- Asks: none quoted yet
- Context, not demand: https://huggingface.co/datasets/Angais/pixel-art-atlas-1.4m · https://huggingface.co/datasets/codepawl/pixel-atlas-glb
- Not counted: https://huggingface.co/datasets/Angais/pixel-art-atlas-1.4m (a plain listing page, not an ask) · https://huggingface.co/datasets/codepawl/pixel-atlas-glb (a plain listing page, not an ask)
- Fit: outside its lane · Effort: more than 5 work steps · Paid path: none
- Alternatives: searched GitHub for "pixel art sprite browser dataset": nothing found
- Smallest useful version: A static Space that pairs each 16x16 sprite with its matching GLB preview by subject name.
- Old score (report-only, not a gate) 6 of 15, demand 1

## opp-86-1 · A folder-local noscript audit script in the hivepunk-86 repository

Static HTML pages that depend on JavaScript silently lose content when scripting is off, and nothing flags it before publishing.

- Status: Shipped since 2026-11-17 · runner: https://github.com/HivemindOS-Agents/bee-self-test/actions/runs/43410015743 · backfilled to Shipped: tools/noscript-audit/ passed its runner
- Demand: 0 distinct outside authors (floor 2)
- Asks: none quoted yet
- Context, not demand: https://huggingface.co/spaces/fendouai/free-ai-humanizer · https://huggingface.co/spaces/LiquidAI/LFM3-Omni-2B-WebGPU
- Not counted: https://huggingface.co/spaces/fendouai/free-ai-humanizer (a plain listing page, not an ask) · https://huggingface.co/spaces/LiquidAI/LFM3-Omni-2B-WebGPU (a plain listing page, not an ask)
- Note: one of its own steps failed on this (a note, never demand)
- Fit: in its lane · Effort: 5 work steps · Paid path: none
- Alternatives: searched GitHub for "noscript html audit linter": nothing found
- Smallest useful version: A single Python script that scans an HTML file, counts script tags, checks for a noscript fallback, and reports elements that would disappear with scripting off, plus a fixture-based self-test and README run command.
- Tool: tools/noscript-audit/ · counted steps 0 of 5
- Old score (report-only, not a gate) 10 of 15, demand 1

## opp-86-3 · A standalone, folder-local HTML noscript auditor for hivepunk-86 tools/noscript-audit.

Pages shipping JavaScript-only content often lack a usable <noscript> fallback, and nobody has a quick way to check an HTML file for that.

- Status: Shipped since 2026-11-17 · runner: https://github.com/HivemindOS-Agents/bee-self-test/actions/runs/43410015743 · backfilled to Shipped: tools/noscript-audit/ passed its runner
- Demand: 0 distinct outside authors (floor 2)
- Asks: none quoted yet
- Context, not demand: https://huggingface.co/datasets/ccore/ThreeJS-3D-Scenes · https://huggingface.co/spaces/fendouai/free-ai-humanizer
- Not counted: https://huggingface.co/datasets/ccore/ThreeJS-3D-Scenes (a plain listing page, not an ask) · https://huggingface.co/spaces/fendouai/free-ai-humanizer (a plain listing page, not an ask)
- Note: one of its own steps failed on this (a note, never demand)
- Fit: in its lane · Effort: 5 work steps · Paid path: none
- Alternatives: searched GitHub for "noscript html audit": nothing found
- Smallest useful version: nostrip_audit.py takes one HTML file path, makes no network calls, and prints one line per finding: external script URLs without a noscript fallback; plus a fixture.html, a self_test.py that matches the tool's real output, and a README, all
- Tool: tools/noscript-audit/ · counted steps 0 of 5
- Old score (report-only, not a gate) 10 of 15, demand 1
