# Changelog

All notable public changes to this resource are documented here.

## 2.3.0 — 2026-10-10

- Re-verified all 61 retained tools against current first-party sources. A separate agent tried to refute every safety-relevant change, and a cross-tool pass made privacy judgments consistent. 70 of 71 records carry the new verification date.
- Added 11 tools: Poolside Agent CLI, Snowflake Cortex Code, Notebook Intelligence, MLJAR Studio, JASP, IBM Bob, Coder Agents, Kimi Code CLI, Deep Agents Code, Oh My Pi and DeepSeek Harness. Moved DataFoundry to an evidence hold; Nobie stays held.
- Documented special-category routes for six tools, each restricted to a fully local or institution-controlled configuration with explicit controls: Copilot CLI offline mode, Codex CLI with local models, the Antigravity SDK, Posit Assistant with local models, self-hosted Roomote and Zerve Self-Managed.
- Removed vendor-hosted tiers from qualifying routes (Factory Private, GitLab Dedicated for Government). Required Ollama's local-only mode wherever a route names Ollama, and required disabling default web, update and telemetry egress.
- Applied one data-handling rule to tiered products: Windsurf, Devin, Hex and Jules now read opt-out; Antigravity reads no-train.
- Fixed the Free/academic filter, which listed tools whose academic note said no programme existed.
- Recorded method, verdicts and limits in `evidence/LIVE_AUDIT_2026-10-10.md` and `evidence/reverify-2026-10-10/`.

## 2.2.0 — 2026-09-11

- Reviewed all 60 baseline entries against current first-party evidence. Updated
  59 retained public summaries and added Pi and Zencoder, producing 61 displayed
  tools. Nobie is held outside the catalog with its prior record and reconsideration
  conditions preserved; this does not mark the company or product discontinued.
- Corrected Kiro operational storage, Replit Enterprise-only agreement scope,
  Amp retention terminology, Ante binary licensing and exported log contents,
  and multiple plan, pricing and model-route changes. DataFoundry remains one
  product after checking its parent/distribution relationship.
- Added an explicit `unknown` data-handling value for unresolved training/retention
  evidence. Zerve uses this value; Clusy's own-service no-training statement is
  distinguished from non-uniform provider controls. Suitability policy is unchanged.
- Clarified configuration-dependent Local/ZDR/No-train legends. Preserved stable
  identifiers, recorded source access and dated decisions, and set the immutable
  release reference after owner review and publication authorization.

## 2.1.1 — 2026-08-14

- Added a visible version-and-date badge to the index header, generated from
  `resource_metadata.json`, so the most recent published update is legible at
  a glance and refreshes automatically with every release.
- No tool records, suitability classifications, or data distributions changed.

## 2.1.0 — 2026-08-13

- Re-verified all 43 retained records against current first-party vendor/project sources through six delegated review slices; 28 records were materially updated (pricing, model backends, data-handling terms, contractual gates, moved or dead vendor URLs) and every record carries a 2026-08-13 evidence-check date.
- Added 17 records from five discovery lanes after per-candidate first-party verification, including Grok Build, Muse Code, Qwen Code, Factory (Droids), GitLab Duo Agent Platform, Roomote, Microsoft 365 Copilot Analyst, LM Studio Bionic, and local/self-hosted data tools; two candidates were rejected (shai: maintenance health; Rowboat: out of scope).
- Completed the first-party-confirmed Windsurf to Devin Desktop rename and retired Hex's discontinued "Magic" branding, keeping former names as aliases on stable IDs.
- Tightened conservative classifications where vendor evidence weakened or vanished, including Amp's retention reframing, Mistral's discretionary API-only ZDR, Augment's undocumented on-prem claims, and unverified student discounts.
- Hardened the link auditor with per-host politeness limits and fixed CI artifact uploads of hidden maintenance outputs.

No DOI is assigned to this release.

## 2.0.1 — 2026-07-14

- Increased the index's main reading text, explanatory details, and column headings for more comfortable use while preserving the compact research-table layout.
- Kept badges, filters, metadata, catalog records, and evidence classifications unchanged.

## 2.0.0 — 2026-07-14

- Refreshed coding and data-agent records against current first-party evidence through separate delegated review lanes with adversarial coordinator cross-checking.
- Clarified data-sensitivity classes, deployment dependencies, and the catalog's conservative suitability policy.
- Added schema-validated JSON, JSON-LD metadata, provenance, evidence dates, content and code licences, and release-level metadata.
- Added a reproducible agent-neutral maintenance protocol, deterministic builds, strict release validation, link auditing, and continuous quality checks.
- Redesigned the interactive index for clearer filtering, responsive use, and accessibility.

No DOI is assigned to this release.
