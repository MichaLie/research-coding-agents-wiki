# AI Coding & Data Agents for Researchers

A **privacy-first** guide to AI coding and data-analysis tools for scientific work. Start from **your data**, see which tools are appropriate, and what each costs in capability.

**▶ Live site:** https://michalie.github.io/research-coding-agents-wiki/

> *As open as possible, as closed as necessary.* — guiding principle (ELIXIR)

## Why this exists
General "best AI coding tool" round-ups ignore the question that actually gates adoption in research: **where does my data go, and can I trust this tool with unpublished, personal, or special-category data?** This wiki puts that question first.

## How to read it
1. **Pick your data class** — non-sensitive · personal (pseudonymised, GDPR) · special-category (health / genetic / clinical, GDPR Art. 9). The table then shows a suitability verdict per class: ✓ suitable · ⚠ only with a specific tier/config · ✗ not appropriate.
2. **Check the data-handling pill** — the best privacy option a tool offers (Local · Zero-retention · No-train · Opt-out · Trains by default). The small **▸ line beneath** is the plan/tier or setting required to get it — the default or free plan is usually less private.
3. **Weigh capability** — frontier / strong / capable / basic. **↔ model** means capability depends on the LLM you connect (bring-your-own-model tools).
4. **★ established** marks the widely-adopted choice within each lane.

## Principles
- **Special-category data → infrastructure you control only.** Local / self-host / on-prem are ✓/⚠; cloud services — *even with zero data retention or a HIPAA BAA* — are ✗, because the data still leaves your environment and most data-use agreements and ethics boards forbid it.
- **Curated, not exhaustive.** A useful shortlist, not a complete catalogue; niche, enterprise-only, and single-purpose tools are intentionally omitted for clarity.
- **Decision-support, not legal advice.** Classify your data with the [ELIXIR RDMkit](https://rdmkit.elixir-europe.org/data_sensitivity), and **confirm with your DPO / data steward and each vendor's own terms** before using sensitive or regulated data. Privacy and pricing change quickly — each row shows when it was last verified.

## Repository
| File | Purpose |
|------|---------|
| `tools.json` | Source of truth — **the only file edited by hand** |
| `build_html.py` | Generates the self-contained site (`python3 build_html.py tools.json docs/index.html`; Python 3, no dependencies) |
| `docs/index.html` | The published page (GitHub Pages, served from `main:/docs`) |
| `CLAUDE.md` / `AGENTS.md` | Operating guide for AI agents maintaining the wiki |
| `.claude/skills/update-coding-agents-wiki/` | Invocable skill for the discover + re-verify maintenance loop |

Never hand-edit the generated HTML — edit `tools.json` and rebuild.

## Dedicated to ELIXIR-CZ
This resource is dedicated to **[ELIXIR-CZ](https://www.elixir-czech.cz/)**, the Czech national node of **[ELIXIR](https://elixir-europe.org/)**, the European research infrastructure for life-science data.
