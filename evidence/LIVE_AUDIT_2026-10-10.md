# Live audit — October 10, 2026

This is a local 2.3.0 candidate on branch `agent/v2.3.0-2026-10-refresh`, not a published release. Baseline: commit `5d7e7b8` (full SHA in [`reverify-2026-10-10/decisions.json`](reverify-2026-10-10/decisions.json)). No push, tag, release, merge or deployment was performed. `release_ref` remains null.

## Result

- Baseline: 61 tools. Final: **71 tools**.
- All 61 retained tools were re-verified against current first-party sources. 59 remain displayed. DataFoundry moves to an evidence hold, and Nobie stays held.
- 11 additions: Poolside Agent CLI, Snowflake Cortex Code (CoCo), Notebook Intelligence, MLJAR Studio, JASP, IBM Bob, Coder Agents, Kimi Code CLI, Deep Agents Code, Oh My Pi and DeepSeek Harness.
- Special-category routes: **47 configuration-required** on customer-controlled infrastructure, **24 not appropriate**, none ready without configuration.
- 70 of 71 public records carry `verified: 2026-10-10`. Tabnine keeps its September date: its pricing page returned errors after the Tricentis acquisition, and its DPA and provider retention terms are not public, so not every claim could be re-checked.

## Method

1. **Re-verification.** One agent per retained tool re-checked every field against current first-party product, documentation, pricing, privacy, DPA, trust, deployment and licence pages, and recorded short excerpts with locators. No tool was installed or run.
2. **Adversarial review.** A separate agent tried to refute every safety-relevant change: training default, retention, deployment boundary, suitability, special-category route, openness, licence and status. Seven tools without a flagged safety change were also reviewed. Each of the 61 verdicts confirmed the proposal with corrections, and every refuted element was dropped. The refuted elements include three attempts to loosen the personal-data route to consumer or individual plans (Claude Code, Grok Build, Devin Desktop), and GitLab Dedicated for Government offered as a special-category deployment.
3. **Discovery.** Five lanes (IDE/editor, terminal/CLI, cloud/autonomous, local/self-hosted, data/notebook) and a re-check of the September holds. Every proposed addition went to its own refuting agent.
4. **Integration pass.** One agent compared privacy judgments across all tools. It found 23 issues, from vendor-hosted tiers treated as customer-controlled to missing default-egress controls and inconsistent labels.
5. **Merge.** One agent per tool produced the final record from the proposal, the verdict and the integration resolutions. Refuted or unverifiable changes revert to the baseline value. Every final record passes the schema and the catalog's cross-field rules.

Machine-readable decisions, verdicts, merge logs, excerpts and source access records are in [`reverify-2026-10-10/decisions.json`](reverify-2026-10-10/decisions.json).

## Material judgments

- **Six tools gain a documented special-category route** (`no` → `cfg`): GitHub Copilot (only the Copilot CLI offline mode with a local BYOK model), OpenAI Codex (only the Apache-2.0 CLI with `--oss` or a local provider), Google Antigravity (only the SDK with an on-device or localhost model), Posit Assistant (only with Ollama or LM Studio and cloud providers disabled), Roomote (only self-hosted with an institution-run model endpoint) and Zerve (only Enterprise Self-Managed with an institution-operated gateway). Each route lists its required controls. The rest of each product stays `no` for special-category data, and confidence is lowered to medium where the route rests on documentation of a closed runtime.
- **Vendor-hosted tiers removed from qualifying routes:** Factory Private (in-boundary inference not documented) and GitLab Dedicated for Government (Agent Platform unavailable there; GitLab-hosted single tenancy).
- **Localhost is not proof of local inference.** A signed-in Ollama server can serve `:cloud` models through the same localhost endpoint. Every configuration-required route that names Ollama now requires Ollama's local-only mode. Routes that accept an institutional endpoint must also confirm that the endpoint does not forward requests to external providers.
- **Default egress.** Several local tools turn on web search, web fetch, update checks or remote telemetry by default. Their routes now require disabling or centrally governing them.
- **Data-handling labels made consistent.** Where individual or self-serve tiers train by default and the record's gate is the organisational tier, the label now follows one rule: it is the training default of the least-protective plan the gate admits for personal data, before any opt-out. Windsurf, Devin, Hex and Jules move from `no-train` to `opt-out`; Antigravity moves from `opt-out` to `no-train`. This convention is proposed to the owner for confirmation and is not yet written into MAINTENANCE.md.
- **Openness:** Cline and Kilo Code are `open-core` (open-source clients, proprietary hosted services). Codex is `open-core` with a confirmed licence for its CLI.
- **Ownership changes recorded from first-party sources:** Cursor (Anysphere, acquired by SpaceX), Tabnine (acquired by Tricentis), Kilo Code (acquired by Anaconda), marimo (part of CoreWeave), Augment Code (Cosmos, Auggie CLI and Context Engine assets acquired by Harness), and xAI's Grok Build (now under SpaceXAI).
- **Muse Code:** personal-data suitability `no` → `cfg`, as a gated organisational route under the Meta processor terms and organisation ZDR, with written confirmation of coverage required.
- **DataFoundry:** moved to an evidence hold. Its install branch has had no commits since 2026-08-17, it has no releases, issues are disabled, and upstream was renamed DataAgent. Prior row and reconsideration condition are preserved.
- **twinny:** proposed as an addition and confirmed by its reviewer, but held by the curator. Its refuter found a 13-month idle period that ended only five weeks before this review. MAINTENANCE.md requires maintenance health for open-source inclusion.
- **Orion** is dropped: Orion Cloud sign-in is a required onboarding step. **Nobie** stays held (one of three conditions met).

## Presentation fix

The Free/academic filter counted any non-empty academic text as an offer, including "No academic or student program found". In the baseline, 30 of 61 tools appeared under that filter wrongly. Negative statements no longer count.

## Coverage limits

Verification means the dated public evidence was checked. It does not certify a customer's contract, institutional approval, runtime behaviour or every model and integration. JavaScript-heavy pages sometimes returned only navigation; agents then read official Markdown or raw documentation sources, and recorded the access limits. Web search was rationed across agents, and Hacker News and GitHub search served as lead channels for discovery. Wayback snapshots were rate-limited, so some September-to-October text differences rest on dated changelogs instead.

## Local checks

- The dated migration (`scripts/apply_2026_10_10_refresh.py`) is idempotent: a second run left every canonical JSON file byte-identical.
- `build.py`: 7 generated artifacts byte-stable. `validate_catalog.py`: pass, including the cross-field rules (special route agrees with suitability, customer-controlled boundary for every configuration-required route, open-source only with a confirmed licence); one expected warning for the null release reference. `git diff --check`: clean.
- Full URL audit: 1,282 unique URLs across 1,490 occurrences. 1,434 occurrences reachable and 56 restricted (bot blocks, not verification); none missing.
- `validate_catalog.py --release` is expected to fail only on the null release reference.

Publication remains a separate step that needs the owner's explicit approval.
