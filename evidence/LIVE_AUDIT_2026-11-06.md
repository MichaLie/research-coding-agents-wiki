# Live audit — November 6, 2026

This is a local 2.4.0 candidate on branch `agent/v2.4.0-2026-11-refresh`, not a published release. Baseline: commit `d21b4eb` (the published 2.3.0 release; full SHA in [`reverify-2026-11-06/decisions.json`](reverify-2026-11-06/decisions.json)). No push, tag, release, merge or deployment was performed. `release_ref` remains null.

## Result

- Baseline: 71 tools. Final: **78 tools**.
- All 71 tools were re-verified against current first-party sources. 70 remain displayed. **Jules is removed**: Google announced on 29 October 2026 that Jules winds down (sessions can be finished until 11 November, read-only afterwards, shutdown on 31 December) and points users to Google Antigravity. MAINTENANCE.md requires discontinued products to be removed; the prior record and the shutdown evidence are kept in `decisions.json` (`removed_records`).
- 8 additions: Open WebUI (with Open Terminal), Data Formulator, Amazon SageMaker Data Agent, Codewhale (formerly DeepSeek TUI; not affiliated with DeepSeek), MATLAB Copilot, KNIME K-AI, Claude for Excel and Freebuff (formerly Codebuff; ad-funded, prompts are used for ad profiling, rated accordingly). The last four were October holds whose conditions are now met.
- Special-category routes: **50 configuration-required** on customer-controlled infrastructure, **28 not appropriate**, none ready without configuration. New routes come from three additions (Open WebUI, Data Formulator and Codewhale, each self-hosted with local or institution-run inference); no retained tool changed its special-category rating.
- All 78 public records carry `verified: 2026-11-06`, including Tabnine, whose pricing and terms could be re-checked this time.

## Method

1. **Re-verification.** One agent per tool re-checked every field against current first-party product, documentation, pricing, privacy, DPA, trust, deployment and licence pages, and recorded short excerpts with locators. No tool was installed or run.
2. **Adversarial review.** A separate agent tried to refute every safety-relevant change (training default, retention, deployment boundary, suitability, special-category route, openness, licence, status). 39 re-verifications were reviewed this way, including Jules; all confirmed the proposal, 37 with corrections, and every refuted element was dropped. The other 32 tools had no safety-relevant change and are recorded as proposer-verified.
3. **Discovery.** Five lanes (IDE/editor, terminal/CLI, cloud/autonomous, local/self-hosted, data/notebook) screened 72 candidates: 4 additions, 10 holds, 58 not added. A separate re-check of the 30 October holds produced 4 additions, 18 continued holds and 8 drops (including Nobie, held for the third time with nothing changed). Every proposed addition went to its own refuting agent, which confirmed all eight with corrections.
4. **Integration pass.** One agent compared privacy judgments across all tools and raised 36 issues.
5. **Merge.** One agent per tool produced the final record from the proposal, the verdict and the integration decisions below. Refuted or unverifiable changes revert to the baseline value. Every final record passes the schema and the catalog's cross-field rules. One merge output was overwritten by an unrelated record during the run; it was detected by an ID check and re-run.

The refuters were tested with three planted known-bad proposals taken from October's not-added list (an end-of-life product presented with a customer-controlled route, a sunset open-source tool, and an archived CLI that duplicates a catalogued tool). All three were rejected. They are not in any payload.

Machine-readable decisions, verdicts, merge logs, excerpts and source access records are in [`reverify-2026-11-06/decisions.json`](reverify-2026-11-06/decisions.json).

## Material judgments

- **Classification changes (3):** Julius AI `no-train` → `opt-out` and Kimi Code CLI `opt-out` → `trains`, both confirmed by their refuters. Claude Code `zdr` → `no-train`: zero data retention needs Anthropic's approval per organisation, so it is not the commercial default; the ZDR scope stays in the record's tier gate.
- **Refuted changes, reverted or reworded:** Zerve's proposed `no-train` rested on one marketing sentence and stays `unknown`; an OpenCode wording change that softened default-enabled hosted free models was reverted; a generalisation of GitHub Copilot's memory default was narrowed to the plans it applies to; an unsupported claim that Roomote Cloud is closed to new users and a claimed Windsurf admin feature were dropped. Over-promising wording was corrected for JetBrains Datalore (only JDBC-driver preloading is documented for air-gapped use), Amp (self-hosted orbs do not keep file contents in the customer's network), Devin EU (US transfers disclosed), Posit Assistant (only the local-model option qualifies for special-category data), OpenAI Codex, Ante and Juggler.
- **Labelling conventions left unchanged.** The integration pass found that data-handling scope, "local-only" versus institution-endpoint inference, and open-core versus open-source are applied by more than one convention. Writing one rule is the owner's decision, pending since October, so labels were changed only where evidence showed them to be wrong.
- **Consistency fixes applied:** a one-line tier gate for six bring-your-own-model tools that lacked one (Aider, Cline, Goose, Jupyter AI, marimo, Ollama); SPDX-style licence identifiers; Kiro scoped to IDE/Web with the CLI in `rca-kiro-cli`; Windsurf and Devin describe the air-gapped build and Devin EU consistently.
- **Product changes recorded from first-party sources** include OpenCode discontinuing session sharing and folding OpenCode Zen into its Console, Posit Assistant becoming generally available in Workbench 2026.10.0, and Poolside's hosted availability changing while its local and air-gapped routes stay documented.
- **DataFoundry** stays on evidence hold: the distributed workbench still shows no maintenance of its own.

## Coverage limits

Verification means the dated public evidence was checked. It does not certify a customer's contract, institutional approval, runtime behaviour or every model and integration. JavaScript-heavy pages sometimes returned only navigation; agents then read official Markdown or raw documentation sources and recorded the access limits. GitHub search and the shared GitHub API quota were rate-limited during discovery, so open-source health checks were limited for some candidates; Hacker News and GitHub served as lead channels and favour developer-facing launches.

## Local checks

- The dated migration (`scripts/apply_2026_11_06_refresh.py`) is idempotent: a second run left every canonical JSON file byte-identical.
- `build.py`: generated artifacts byte-stable. `validate_catalog.py`: pass, including the cross-field rules; one expected warning for the null release reference. `git diff --check`: clean.
- Full URL audit: 1,683 unique URLs across 1,932 occurrences. 1,851 occurrences reachable and 74 restricted (bot blocks, not verification); none missing. The 7 network errors are all jasp-stats.org pages, which the audit client could not reach; three of them, re-fetched with curl the same day, returned HTTP 200 or 301, so the host is reachable ([`reverify-2026-11-06/link_recheck.json`](reverify-2026-11-06/link_recheck.json)).
- `validate_catalog.py --release` is expected to fail only on the null release reference.

Publication remains a separate step that needs the owner's explicit approval.
