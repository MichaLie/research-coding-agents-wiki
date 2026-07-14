---
name: update-coding-agents-wiki
description: Perform a current first-party safety review of the researcher coding/data-agent shortlist, then build and locally validate it under the repository maintenance and FAIR release gates.
---

# Update the AI Coding and Data Agents index

1. Read `MAINTENANCE.md` completely. It is canonical and this skill cannot override it.
2. Read `schema.json`, load `tools.json`, normalize names/aliases, and inspect the latest live-audit evidence.
3. A full refresh must re-verify every retained tool—not only discover additions—using current first-party product, release, pricing, privacy/DPA/trust, deployment, and model-provider pages.
4. Use independent review lanes for IDE/editor, CLI, cloud/autonomous, local/self-hosted, and data/notebook tools, with one conservative integration pass for tier, retention, training, deployment, and suitability.
5. Enforce the strict special-category rule and deliberate omission policy in `MAINTENANCE.md`. Remove discontinued, stale, out-of-scope, or misleading products. Public marketing and generic vendor certifications are not sufficient evidence.
6. Preserve stable IDs and evidence dates. Apply a large review through a dated migration and dated evidence note.
7. Run:

```bash
python3 build.py
python3 validate_catalog.py
python3 scripts/audit_links.py --workers 24 --timeout 20
git diff --check
```

8. Inspect all data-sensitivity/filter states in the local rendered site. `python3 validate_catalog.py --release` is the final eligibility gate.

Never push, deploy Pages, create a release/DOI, or publish a FAIR badge unless the human owner explicitly authorizes it after reviewing the complete preview and a passing release gate.
