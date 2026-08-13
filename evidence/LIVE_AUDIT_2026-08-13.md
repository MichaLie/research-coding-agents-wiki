# Coding and Data Agents live audit — 2026-08-13

## Scope and method

- Baseline: 43 catalog records at source commit `d9b68b9b84e8b91ae827232007446254427f8c14` (v2.0.1 line).
- Review date: 2026-08-13.
- Re-verification: six delegated review slices covered all 43 retained records against current first-party vendor/project documentation for product status, model/deployment boundary, pricing, privacy/data use, retention, contractual tier, and controlled-infrastructure availability. Each slice ran under an anti-fabrication contract: every claimed change carries a fetched source URL and quote, and anything not re-found on a fetched page is marked unverified rather than silently retained.
- Discovery: five lanes (IDE/editor, terminal/CLI, cloud/autonomous, local/self-hosted, data/notebook) surfaced candidates; every surviving candidate then went through per-candidate first-party verification before acceptance.
- Constraint note (honest limitation): the session's shared web-search quota was exhausted mid-sweep, so later stages ran on direct first-party fetches rather than search. Coverage of brand-new startup launches may therefore be thinner than the lane design intended; the next sweep should re-open discovery with full search capacity.
- Safety rule: cloud processing is never classified as suitable for special-category health/genetic/clinical data. A `cfg` result in that column requires a real local, self-hosted, on-premises, or air-gapped path on infrastructure the researcher controls.
- Meaning of `verified`: the cited first-party pages were appraised on the review date. It is not a legal approval, certification guarantee, or promise that a vendor will not change its terms.
- Detailed per-claim evidence (verdicts, changed fields, fetched URLs, and quotes) is machine-readable in `evidence/reverify-2026-08-13/rca_reverify_{1..6}.json` and `evidence/additions-2026-08-13/rca_result_{1..5}.json`.

## Re-verification results

| Verdict | Records |
|---|---|
| changed (materially updated) | 28 |
| unchanged (verified refresh only) | 15 |
| discontinued | 0 |
| could_not_verify | 0 |

All 43 retained records now carry `verified: 2026-08-13`; the 28 materially updated records also carry `date_modified: 2026-08-13`.

## Additions and rejections

17 records added after first-party verification: Grok Build, Muse Code, Ante, Nanocoder, Qwen Code, Factory (Droids), Roomote, GitLab Duo Agent Platform, Clusy, DataFoundry, Nobie, Ada (Automated Data Analyst), Microsoft 365 Copilot Analyst, Zerve, LM Studio Bionic, Juggler, and OpenSquilla. Result: 60 curated records.

| Candidate | Decision | Reason |
|---|---|---|
| shai (OVH) | Reject | Fails the open-source maintenance-health gate: no commits or releases in 2026 (~8 months dormant); the anonymous/EU-sovereignty selling point was also only partially reconcilable with the AI Endpoints product page. Re-evaluate if activity resumes. |
| Rowboat | Reject | Out of scope: a general-purpose desktop assistant whose code mode delegates to external coding agents already catalogued; no discoverable privacy policy. |
| Zencoder | Reject (discovery stage) | No in-window event to justify (re-)evaluation this cycle. |
| we-love-jupyter-notebook | Reject (discovery stage) | Too thin to meet the curated-inclusion bar. |

## Ecosystem notes

- Continue's sunset is confirmed by its own repository README; the record was already removed in v2.0.0 under the maintenance-health rule. The rumored Cursor involvement found no first-party evidence on Cursor's blog and was not acted on.
- Gemini CLI's consumer retirement completed: the CLI and Code Assist IDE extensions stopped serving consumer free-tier and Google AI Pro/Ultra requests on 2026-06-18; the Apache-2.0 project itself remains active for paid API/Vertex/enterprise routes, so the record is retained with the consumer route removed. The project's github.io docs still describe the retired free tier; the dated first-party blog is treated as authoritative.
- Windsurf -> Devin Desktop is now first-party confirmed (windsurf.com 308-redirects to devin.ai/desktop, whose FAQ states the rename); the record's name was updated with "Windsurf" kept as an alias on the stable ID. The Windsurf name survives only for the JetBrains plugin.
- Vendor-identity drift observed at Amp: the terms name Amp Frontier Corporation while the privacy policy still names Sourcegraph, Inc. as data controller; recorded in the record notes.

## Material safety corrections

- Reframed Amp's enterprise offering from ZDR to "Minimal Data Retention" with 30-day provider safety retention, per its current security page.
- Tightened Mistral Vibe: cloud ZDR is discretionary, pay-as-you-go API-only, and never covers Vibe Work/Chat.
- Downgraded Augment Code's deployment claims: VPC/single-tenant/on-prem statements were not found on current public pages and are treated as unverified enterprise-contract options.
- Marked stale or dead first-party artifacts: Julius's public DPA URL (404, DPA still offered via the privacy policy), Zed's security page (404, SOC 2 status unverified), Kiro's moved privacy/compliance docs, marimo's privacy URL now redirecting to CoreWeave's policy, and Hex's retired "Magic" branding (record renamed to Hex with the former name aliased).
- Removed no-longer-supported claims conservatively: Cursor and Windsurf student offers, Kiro CLI's FedRAMP-in-progress line, Kilo's signup credit, Amp's $5 minimum and $10/day free-credit figures, and Tabnine's trial claim; Tabnine's private/self-hosted deployment is now advertised on both self-service tiers and the gate text was widened accordingly.

## Coordinator adjudications

- Nobie and Clusy were accepted despite thin governance documentation, because each uniquely fills a researcher need surfaced by the data lane. Both are classified sharply conservatively (Clusy: `trains`/no/no with no compliance claims; Nobie: local-only route with telemetry caveats) and carry `confidence: low`. These two records are explicitly flagged for owner review.
- Where a drafted field could not be verified (e.g. Grok Build's retention default, Muse Code's retention posture, Qwen Code's telemetry default, Zerve's in-boundary inference), the conservative classification was kept and the gap is stated in the record text rather than smoothed over.

## Verification results

- `python3 scripts/apply_2026_08_13_refresh.py`: idempotent (second run produced a byte-identical tools.json).
- `python3 build.py`: deterministic generation passed for all 7 generated artifacts.
- `python3 validate_catalog.py`: PASS with 0 errors and 1 warning (the intentionally null `release_ref`, resolved only during the human-authorized packaging step).
- Post-edit link audit (`scripts/audit_links.py`, now with per-host politeness limits): 352 unique URLs across 489 occurrences.
  - Reachable: 339.
  - Access-restricted: 13.
  - Missing: 0.
  - Network error: 0.
- Machine-readable result: `evidence/link_audit.tsv`.

## Remaining boundaries

- Product terms can change faster than the catalog release cycle. The next maintenance run must re-open current vendor pages rather than inherit this audit's conclusions mechanically.
- A public DPA, BAA, trust-page badge, or ZDR statement is not enough to approve a research workflow. Researchers must still apply their institution's DPO/IRB/DUA requirements and validate the exact plan, region, model provider, integrations, and retention settings.
- Several vendors' trust centers render only client-side and could not be appraised (Julius, Hex, Replit, Augment, Factory); certification claims from those vendors are recorded with their observed evidence level, not upgraded.
