# Coding and Data Agents live audit — 2026-07-13

## Scope and method

- Baseline: 46 catalog records at source commit `f18471ac45ee8bec5cdb0bb63c32a6cfe8d5722f`.
- Review date: 2026-07-13.
- Method: every baseline record was reviewed against current first-party vendor/project documentation for product status, model/deployment boundary, pricing, privacy/data use, retention, contractual tier, and controlled-infrastructure availability.
- Safety rule: cloud processing is never classified as suitable for special-category health/genetic/clinical data. A `cfg` result in that column requires a real local, self-hosted, on-premises, or air-gapped model path on infrastructure the researcher controls.
- Source rule: evidentiary `sources` now use vendor/project-owned pages and official project repositories. Third-party reviews were removed.
- Meaning of `verified`: the cited first-party pages were appraised on the review date. It is not a legal approval, certification guarantee, or promise that a vendor will not change its terms.

## Curation decisions

| Baseline record | Decision | Reason |
|---|---|---|
| Continue.dev | Remove | Final v2.0.0 is archived/read-only and the service/vendor support path is no longer active; fails the maintenance-health gate. |
| Plandex | Remove | Official cloud wound down and the repository has been stale since 2025-10-03; self-hosting alone also did not guarantee local inference. |
| Qodo | Remove | Current product is code review/governance and code generation was deprecated; code-review/PR bots are explicitly out of scope. |
| SWE-agent | Replace | Original project is maintenance-only and officially superseded for most uses. |
| mini-SWE-agent | Add | Active MIT-licensed successor with current releases, local-model support, and local/Docker/Singularity/Apptainer execution options. |
| Gemini CLI | Retain as active open source | The Apache-2.0 CLI remains available for paid API/Vertex/enterprise use. Consumer migration to Antigravity CLI does not make the two products one record. |
| Google Antigravity | Retain separately | Proprietary consumer/enterprise agentic development product with its own terms and access model. |

Result: 43 curated records.

## Material safety corrections

- Corrected training defaults and contractual gates for Claude Code, Cursor, GitHub Copilot, Devin/Devin Desktop, Kiro IDE/CLI, Mistral Vibe, Google products, and Replit.
- Removed unsupported implications that customer-dedicated or VPC deployments are necessarily customer-controlled on-premises deployments.
- Separated model-provider ZDR from the product operator's own chat/thread/notebook retention for Amp, Hex, Databricks Genie Code, and ChatGPT Data Analysis.
- Added or restored controlled-infrastructure `cfg` paths for Aider, JetBrains Junie, Zed, Deepnote Enterprise, JetBrains Datalore On-Premises, and other genuinely local/self-hosted tools.
- Downgraded personal-data use where no current public DPA or institutional processor terms were verified, including Jules and Runcell.
- Removed unsupported product-level compliance inheritance from generic cloud-provider certifications.
- Renamed ChatGPT Advanced Data Analysis to its current product name, ChatGPT Data Analysis, while preserving the former name as an alias.
- Reframed Ollama as local model infrastructure for coding agents rather than a standalone coding agent.

## Verification results

- `python3 build.py`: deterministic generation passed for all 7 generated artifacts.
- `python3 validate_catalog.py`: 0 errors; resource-level licence and publisher warnings remained at this live-audit checkpoint and were resolved during later v2.0.0 release preparation.
- Post-edit link audit: 257 unique URLs across 345 occurrences.
  - Reachable: 244.
  - Access-restricted: 13.
  - Missing: 0.
  - Network error: 0.
- Machine-readable result: `evidence/link_audit.tsv`.

## Remaining boundaries

- Product terms can change faster than the catalog release cycle. The next maintenance run must re-open current vendor pages rather than inherit this audit's conclusions mechanically.
- A public DPA, BAA, trust-page badge, or ZDR statement is not enough to approve a research workflow. Researchers must still apply their institution's DPO/IRB/DUA requirements and validate the exact plan, region, model provider, integrations, and retention settings.
- At this live-audit checkpoint, catalog-level reuse licensing, formal publisher identity, and persistent identifiers were unresolved governance decisions. The v2.0.0 release metadata later records their resolution; the current canonical metadata is authoritative.
