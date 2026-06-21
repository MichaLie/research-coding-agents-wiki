# CLAUDE.md — AI Coding & Data Agents for Researchers (privacy-first)

Operating guide for any Claude/Codex/other agent working in this repo. **Read this first, in full, before editing anything.** This is an **ELIXIR-CZ** resource: accuracy about data protection is the whole point — a wrong cell here can lead a researcher to mishandle sensitive data. Treat it as safety-critical.

## What this is
A **curated, privacy-first** guide to AI coding and data-analysis tools for scientific work. The reader starts from **their data**, sees which tools are appropriate, and what each costs in capability. Tagline / guiding maxim (ELIXIR): **"as open as possible, as closed as necessary."**

- **Scope:** off-the-shelf AI **coding + data-analysis** tools researchers actually adopt (commercial + open-source). This is the *practitioner-tools* wiki — distinct from the sibling **Autonomous STEM Science Agents** wiki (that catalogs research *systems*; this one catalogs *products you adopt and pay for*).
- **Status (2026-06-21):** 46 tools. **Local draft — NOT yet a git repo, NOT published.** When published it will be `MichaLie/research-coding-agents-wiki` + GitHub Pages from `main:/docs`, same as the two sibling wikis.
- **Owner:** Michaela. Sibling wikis: `~/Desktop/wiki/Foundation_models`, `~/Desktop/wiki/Autonomous_Agents`.

## ⛔ Non-negotiables (the reason this repo exists)

1. **CURRENCY IS MANDATORY. Never trust training memory or stale/cached docs.** This field moves weekly; products rename, get acquired, change data policy, or shut down. **Every fact must be confirmed against the vendor's OWN current pages** (docs, pricing, privacy/trust/DPA) via live web search at edit time. A page from last quarter may already be wrong. Stamp every record with `verified` (today's date) and keep `sources`. *Lesson from the 2026-06 build: training-era assumptions were stale — Roo Code had shut down, Amazon Q Developer was being retired in favour of Kiro. Both were caught only by live web checks. Assume your priors are out of date and verify.*

2. **DATA-POLICY CLAIMS ARE SAFETY-CRITICAL — be extremely cautious.** `data_handling`, `tier_gate`, and `suitability` are the highest-stakes fields. Read the vendor's **own** privacy / trust / DPA pages — not a blog, not a third-party summary, not your memory. Capture the **tier nuance**: what the *default/free* plan does vs. what the safe option requires (Enterprise/API/a toggle). **Default to the more conservative classification when uncertain.** If you cannot confirm a policy, say so / mark it conservatively — never guess optimistically.

3. **MAINTENANCE = DISCOVER **and** RE-CHECK EVERYTHING.** A sweep is not just "add new tools." Every existing tool must be **re-verified** each pass for changes — especially data policy, pricing, renames, acquisitions, and discontinuations. Drop the discontinued, update the changed, downgrade optimistic claims that no longer hold.

4. **CURATED, NOT EXHAUSTIVE — useful beats complete.** Fewer, trustworthy rows > a big stale list. Keep the omission policy below. Do **not** re-add things we deliberately cut.

## What is omitted, and why (do NOT re-add)
This is a deliberate shortlist. Out of scope / intentionally excluded:
- **Code-review / PR bots** (e.g. CodeRabbit, Bito) — not coding/data-analysis agents.
- **App-builders / "vibe-coding"** (e.g. Bolt.new, Bolt.diy, Lovable) — prototyping web apps, not researcher coding/data work.
- **Autonomous *science* agents** (e.g. Sakana AI Scientist) — those belong in the **Autonomous STEM Science Agents** wiki, not here.
- **Knowledge / literature tools** (e.g. NotebookLM) — different category.
- **Abandoned projects** — maintenance-health gate (see below). Popularity does not save a dead repo (e.g. FauxPilot: ~15k stars but no commits in 2+ years → dropped).
- **Thin forks-of-forks with no distinct value**, and **obscure / enterprise-only / niche** tools with low researcher relevance.
- **Exception — keep a niche tool** only if it *uniquely* serves a researcher privacy need (e.g. the only self-hostable option for sensitive data).
A footer disclaimer states the wiki is "curated, not exhaustive." Keep it.

## The model (how to think about every row)
- **Primary axis = data sensitivity** (ELIXIR RDMkit): `non-sensitive` → `personal` (pseudonymised, GDPR) → `special-category` (health/genetic/clinical, GDPR Art. 9). The top box lets the reader pick their class; the table shows a **suitability** verdict per class: `ok` (✓) / `cfg` (⚠ only with a specific tier/config) / `no` (✗).
- **SPECIAL-CATEGORY RULE (strict, non-negotiable):** ✓/⚠ **only** for tools that run on **infrastructure you control** — local/self-host + commercial on-prem/air-gapped. **Pure cloud is ✗ even with ZDR / HIPAA-BAA**, because the data still leaves your environment and most DUAs/IRBs forbid it for identifiable or controlled-access data. The on-prem exception goes in the note, not as a ⚠.
- **Data-handling** (`data_handling`) = the **best available** privacy option, shown as a colour pill. Because the safe option is often tier-gated, every conditional pill carries a **`tier_gate`** sub-label (the plan/toggle that unlocks it) so a reader never assumes the free tier is safe.
- **Capability** tier + **`backend_dependent`** ("↔ model"): for bring-your-own-model tools, capability depends on the LLM you connect (frontier API → frontier; local model → lower but private).
- **`established`** (★): the ~10-15 genuinely mainstream/widely-adopted tools, sorted first per section. Keep scarce or it means nothing.
- Tone: **neutral decision-support, not advocacy and not legal advice.** Strict where the data demands, liberal where it doesn't. Always point to ELIXIR RDMkit + "confirm with your DPO/IRB."

## Data schema (one record in `tools.json`)
```json
{
  "name": "Claude Code", "vendor": "Anthropic",
  "type": "cli",                         // ide | cli | cloud | data  (section)
  "openness": "commercial",              // open-source | open-core | commercial
  "deployment": "cloud",                 // free text: cloud / local-capable / self-hostable / on-prem
  "model_backend": "Claude (own models)",
  "data_handling": "zdr",                // BEST available: local | zdr | no-train | opt-out | trains
  "data_handling_note": "tier nuance — what the default does vs what the safe option needs",
  "tier_gate": "Enterprise / API only",  // short ▸ sub-label; "" for default/local-safe tools
  "capability": "frontier",              // frontier | strong | capable | basic
  "backend_dependent": false,            // true => "↔ model" (capability depends on chosen LLM)
  "suitability": { "nonsensitive": "ok", "personal": "cfg", "special": "no" },  // ok | cfg | no
  "suitability_notes": { "personal": "...", "special": "..." },
  "compliance": ["SOC 2", "GDPR"], "pricing": "...", "academic": "free for students / —",
  "use_cases": ["coding", "data analysis"], "runs_locally": false,
  "established": true,                    // ★ widely-adopted (scarce!)
  "links": { "docs": "...", "pricing": "...", "privacy": "..." },
  "sources": ["vendor privacy/DPA URL backing the data-handling claim"],
  "verified": "2026-06-21",              // ALWAYS today's date when you touch the record
  "status": "active",                    // active | renamed | merged | discontinued
  "current_name": "Claude Code", "confidence": "high", "notes": "one factual line"
}
```
- `data_handling` colour buckets are styled by class `dh-<value>`; keep the controlled values exactly.
- Keep strings ASCII (the JSON is ASCII; normalise `–—→` to `- - ->`).

## Build & deploy
```bash
python3 build_html.py tools.json docs/index.html     # the page
git add -A && git commit -m "update tools" && git push   # once the repo/Pages exist
```
- Python 3, **no dependencies**. `tools.json` is the **only** file you hand-edit; `docs/index.html` is generated — never hand-edit it.
- Rebuild after every data edit. Validate: JSON parses; every record has `name`/`type`/`data_handling`/`suitability`; sanity-check per-type counts.
- Publishing (repo + GitHub Pages from `main:/docs`) is **not yet set up** — mirror the sibling wikis when ready.

## Updating & maintaining
Use the skill **`update-coding-agents-wiki`** (`.claude/skills/update-coding-agents-wiki/SKILL.md`). In short: **discover** genuinely-relevant new tools **AND re-verify every existing tool** against its vendor's current pages → correct data policy / pricing / status → drop discontinued & out-of-scope → rebuild. OSS quality gate = **maintenance health (last-commit recency), not stars.** Full re-sweep = multi-agent Workflow (segment discovery → per-tool web re-verification). The field moves weekly; re-verify on a cadence.
