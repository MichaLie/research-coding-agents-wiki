# Reproducible maintenance harness

This directory turns the policy in [`MAINTENANCE.md`](../MAINTENANCE.md) into executable, agent-neutral gates. It is safe for a public fork: it does not publish, push, open issues, spend money, or upload catalogue content.

## Commands

```bash
python3 -m pip install -r requirements-maintenance.txt
python3 maintenance/run_maintenance.py --mode quick
python3 maintenance/run_maintenance.py --mode full
python3 maintenance/run_maintenance.py --mode release
python3 maintenance/simulate_maintenance.py
```

- `quick` rebuilds twice, runs the preview validator, validates the full JSON Schema with format checking, checks stable IDs/names/aliases/dates, checks canonical-data immutability, and runs `git diff --check`.
- `full` adds a live audit of every catalogue URL. HTTP 404/410 is a hard failure; unresolved network/server errors produce `review_required`; authentication, bot protection, and rate limits are recorded as `restricted`, not falsely called broken.
- `release` invokes the strict governance gate as well. It must remain red while publisher, catalogue licence, release version, evidence, or distributions are unresolved.
- `simulate_maintenance.py` copies the repository into isolated temporary directories and proves that a valid synthetic addition passes while invalid vocabulary, alias collisions, impossible dates, stale public distributions, and unresolved release governance are caught. It never adds the synthetic record to the real catalogue.

Reports are written to `.maintenance-output/` and are ignored by Git. CI uploads them as workflow artifacts. A passing automated report is necessary but not sufficient for publication: primary-source appraisal, rendered review, and explicit human approval remain mandatory.
