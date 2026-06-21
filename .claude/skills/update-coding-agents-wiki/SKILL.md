---
name: update-coding-agents-wiki
description: Find genuinely-relevant new AI coding/data-analysis tools AND re-verify every existing tool (especially data-protection policy, pricing, renames, discontinuations) against vendors' current pages, then rebuild the site. Use when asked to update, grow, maintain, refresh, re-sweep, or fact-check the coding agents wiki, add tools, or re-check data policies / keep it current.
---

# Update the AI Coding & Data Agents Wiki

Keep this **privacy-first, ELIXIR-CZ** wiki (`~/Desktop/wiki/Coding_Agents`) **current, correct, and trustworthy**. **Read `CLAUDE.md` first** — schema, the model, the omission policy, and the non-negotiables. This is safety-critical: a wrong data-policy cell can lead a researcher to mishandle health/genetic data.

> Two modes: **quick update** (a few known tools / a targeted re-check) and **full re-sweep** (discover + re-verify everything). Both obey the rules below.

## ⛔ Rules that override everything
1. **Currency:** NEVER rely on training memory or stale/cached docs. Confirm every fact against the vendor's **own current** pages (docs, pricing, privacy/trust/DPA) via **live web search at run time**. Products rename, get acquired, change policy, or shut down weekly — assume your priors are out of date. Stamp `verified` = today; keep `sources`.
2. **Data policy = safety-critical:** read the vendor's own privacy/DPA/trust page (not blogs/summaries/memory). Capture tier nuance (default vs the plan/toggle that unlocks the safe option). **Default conservative when unsure; never guess optimistically.**
3. **Maintenance = discover AND re-check everything** — every existing tool, every pass.
4. **Curated, not exhaustive** — honour the omission policy; don't re-add cut categories.

## 0. Orient
- Read `CLAUDE.md`; load `tools.json`. Note the schema and controlled vocab (`type`, `openness`, `data_handling`, `capability`, `suitability` ok/cfg/no, `tier_gate`, `established`).
- Build the set of existing names + obvious aliases (normalized) to dedupe and to drive the re-check pass.

## 1. Re-verify EVERY existing tool (do this every time — not optional)
For each current tool, web-check against the vendor's own current pages and update the record:
- **Status:** still active? **renamed / acquired / merged / discontinued?** (set `status`, `current_name`; drop or fold the dead — e.g. a tool that shut down, or one retired in favour of a successor.)
- **Data policy (highest priority):** does it train on data? by tier? ZDR available? self-host/on-prem/air-gap? data residency (EU)? compliance (SOC 2 / ISO 27001 / ISO 42001 / HIPAA-BAA / GDPR / FedRAMP)? Re-derive `data_handling` (best option) + `data_handling_note` + `tier_gate`. **Downgrade any optimistic claim that no longer holds.**
- **Pricing / academic, capability, deployment** — refresh.
- Re-derive **suitability** (see §3). Update `verified`, `sources`, `confidence`.

## 2. Discover relevant new tools
Search per segment for tools NOT already listed: commercial IDE/editor agents · terminal/CLI agents · cloud/autonomous coding agents · open-source & self-hostable/local · AI data-analysis & notebook agents · privacy-focused/on-prem/EU-hosted. Prioritise well-known, currently-available, 2025–2026 tools relevant to **researcher coding + data analysis**. **Apply the omission policy** — skip code-review bots, app-builders, science agents (other wiki), knowledge/lit tools, abandoned/thin/niche-enterprise tools.

## 3. Verify & classify each candidate (adversarial, conservative)
- Confirm it's real, current, and in scope. **OSS quality gate = maintenance health (last-commit recency / not archived), NOT stars** — drop abandoned repos (no commits ~9–12 months) even if popular. Drop thin forks-of-forks with no distinct value.
- `type`, `openness`, `deployment`, `model_backend`, `capability` (+ `backend_dependent`/"↔ model" for BYO-model tools).
- **`data_handling`** = best available; write the **`tier_gate`** (what plan/toggle unlocks it; "" only for default/local-safe).
- **`suitability`** per ELIXIR class, DEFAULT CONSERVATIVE:
  - `nonsensitive`: ok unless defunct.
  - `personal` (pseudonymised, GDPR): ok if local/self-host or clear no-train + DPA by default; cfg if it needs a privacy toggle / enterprise tier; no if consumer cloud that may train/retain.
  - `special-category` (health/genetic/clinical): **✓/⚠ ONLY for infrastructure you control** (local/self-host/on-prem/air-gapped). **Pure cloud = ✗ even with ZDR/HIPAA-BAA** (data leaves your environment; DUAs/IRBs forbid it). On-prem exception → note, not a ⚠.
- `established` (★) only for genuinely mainstream tools, the choice in their lane — keep scarce (~10–15 total).
- `sources` (vendor URL backing the policy), `verified` (today), `confidence`.

## 4. Write entries
- Edit `tools.json` only (dedupe by normalized name). Build `links`/`sources` from verified URLs only; ASCII-normalize strings. No "NEW" tags. Keep the public page clean.

## 5. Rebuild, validate, publish
```bash
python3 build_html.py tools.json docs/index.html
```
- Validate JSON parses; required fields present; sanity-check per-type and per-`suitability` counts; confirm special-category ✓/⚠ are all infrastructure-you-control.
- Commit & push once the repo/Pages exist (mirror the sibling wikis: GitHub Pages from `main:/docs`). Poll the live URL until it serves the new content.

## 6. Keep it alive
- **Re-verify on a cadence** — privacy & pricing drift weekly; this wiki rots faster than the sibling wikis. Each sweep: re-check all existing + discover new + drop discontinued.
- Keep the "curated, not exhaustive" footer; keep the omission policy.

## Full re-sweep = multi-agent Workflow
Use the **Workflow tool**: (a) segment discovery agents to surface current/missing tools, then (b) **one web-research agent per tool (existing + new)** that reads the vendor's own current docs/privacy pages and returns a corrected record + `sources` + `verified`. This is the pattern that built the wiki. Token-heavy but thorough; default conservative on every privacy call.

## Guardrails
Only real, **currently-available**, in-scope tools, **verified against the vendor's own current pages**. Data-policy claims are safety-critical — conservative when unsure, always cite `sources`, always date. Curated not exhaustive. `tools.json` is the only file you hand-edit; everything else is generated.
