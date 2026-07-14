# Maintenance protocol

This is the canonical, agent-neutral operating guide for the AI Coding and Data Agents for Researchers index. `CLAUDE.md`, `AGENTS.md`, and `.claude/skills/` are adapters to this file; if they disagree, this file wins.

## Purpose and safety boundary

This is a curated, privacy-first decision aid for off-the-shelf coding and data-analysis tools used in research. It is not a general product directory. Exclude code-review bots, app builders, autonomous science agents, knowledge/literature tools, abandoned projects, thin forks, and low-relevance niche products unless one uniquely fills a researcher privacy need.

Data-policy claims are safety-critical. The catalog is not DPO, IRB, legal, procurement, security, or clinical approval. Always point researchers to their institutional review and current vendor terms.

## Non-negotiable classification rules

- Re-verify every retained tool during a full sweep; do not only discover additions.
- Use current first-party product, documentation, pricing, privacy, DPA, trust, deployment, and release sources. Third-party round-ups are not evidence.
- Capture the exact plan/tier, model provider, product retention, training default, opt-out, and deployment boundary. Model-provider ZDR does not erase product-level retention.
- For special-category health/genetic/clinical data, `ok` or `cfg` is allowed only when the workflow runs on infrastructure the researcher/institution controls (local, self-hosted, on-premises, or air-gapped as actually documented). Pure cloud remains `no`, even with ZDR or a BAA.
- A vendor-dedicated cloud/VPC is not customer-controlled on-premises unless the first-party source explicitly establishes that boundary.
- Default to the conservative classification when evidence is incomplete.
- Open-source inclusion requires maintenance health and researcher relevance, not stars.

## Sources of truth

- `tools.json`: canonical records; the only catalog data edited by hand or a reviewed migration.
- `schema.json`: JSON Schema 2020-12 contract.
- `resource_metadata.json`: resource identity, dates, version, provenance, creator/publisher/licence decisions.
- `build.py`: deterministic build and synchronization entry point.
- `validate_catalog.py`: preview/release validation.
- `evidence/`: dated live-review and URL evidence.
- `docs/` HTML/JSON/schema/JSON-LD: generated distributions; never hand-edit.

Counts are derived from `tools.json`; never hard-code them in agent instructions.

## Record identity and dates

- Preserve stable `rca-*` IDs through renames and mergers; keep former names in `aliases`.
- New records receive `date_added`; materially changed records receive `date_modified`.
- `verified` is the date the exact claims and sources were checked. Rebuilding does not refresh it.
- Keep first-party `sources` and `links` sufficient to support data handling, plan gating, deployment, pricing, and availability claims.

## Update workflow

1. Read this file, `schema.json`, the latest live-audit note, and the deliberate omission policy above.
2. Normalize current names/aliases and identify every record requiring re-verification.
3. Run independent lanes for IDE/editor, terminal/CLI, cloud/autonomous, local/self-hosted, and data/notebook tools; use a separate integration pass for consistent privacy judgments.
4. Verify every retained row against current first-party sources. Remove discontinued, stale, out-of-scope, or misleading products.
5. Apply a large review through a dated idempotent migration and document removals, replacements, uncertainty, and tier-specific caveats in `evidence/`.
6. Build, validate, audit links, and inspect every table/filter/data-sensitivity state in the browser.

## Local verification

```bash
python3 build.py
python3 validate_catalog.py
python3 scripts/audit_links.py --workers 24 --timeout 20
git diff --check
```

The public, agent-neutral harness in [`maintenance/`](maintenance/README.md) runs these gates, full JSON Schema 2020-12 format validation, normalized identity/date checks, report generation, and isolated synthetic fault injection. The checked-in GitHub workflow runs quality gates on changes and a live-link audit on a schedule; it has read-only repository permissions and contains no deployment job.

The public design is generated from `build_html.py`. Source Sans 3 is self-hosted in `assets/fonts/` under the SIL Open Font License and copied into `docs/assets/fonts/` by `build.py`; do not add a runtime font service or edit generated HTML. Preserve the shared crisp layout and this index's blue identity accent while keeping privacy/status colors, data-class controls, focus states, horizontal table scrolling, and mobile geometry accessible. After visual changes, test a wide desktop, 1024 px, 900 px, and 390 px viewport and exercise search, reset, data-class selection, filters, and row expansion.

Before release:

```bash
python3 validate_catalog.py --release
```

Do not weaken the release gate to hide missing record evidence, catalogue licence, formal publisher identity, versioning, or synchronization defects.

## FAIR and fork checklist

Forkers must replace the landing page/repository, real creator and publisher, catalogue licence, version, and provenance in `resource_metadata.json`; rebuild synchronized JSON/schema/JSON-LD/HTML distributions; and validate them. Do not copy Michaela/ELIXIR identity or imply institutional endorsement without authority.

FAIR metadata makes the catalog discoverable and reusable only when rights, versioning, provenance, identifiers, and distributions are honest. It does not make the underlying commercial tools FAIR, safe, or approved.

For this release line, catalog data/metadata/original documentation are CC BY 4.0 and maintenance/build code is MIT. External resources, logos, and trademarks retain their own terms. Michaela Liegertová is the individual publisher; IMG CAS is affiliation only, and ELIXIR-CZ is dedication/community context only.

Provenance separates `baseline_commit`/`baseline_commit_url` (the revision from which the refresh was derived) from `release_ref` (the immutable release URL). Keep `release_ref: null` during ordinary preview work. During an explicitly authorized final packaging step, set it to the planned release URL matching `repository/releases/tag/v<resource_version>`; after publication and before announcement, verify that the exact URL resolves. Do not try to embed the hash of the commit that contains itself.

## Publication boundary

Local editing, testing, and commits are preparation. Push, merge, Pages deployment, DOI minting, release creation, and public FAIR badges require explicit human approval after release validation and preview review. No agent adapter or skill authorizes publication by itself.
