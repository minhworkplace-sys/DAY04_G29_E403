# Deliverables Checklist

Use this as the team execution checklist for the Day 04 lab.

## Must complete

- [ ] Keep working inside `starter_v0/`.
- [ ] Make sure virtual environment is active before running anything.
- [ ] Fill `starter_v0/.env` with real keys, but never commit it.
- [ ] Keep at least 5 declared tools in `artifacts/tools.yaml`.
- [ ] Keep at least 1 team-written new tool.
- [ ] Run and save base eval as `v0`.
- [ ] Produce three real improvement runs: `v1`, `v2`, `v3`.
- [ ] Write exactly 10 team eval cases in `data/eval_group.json`.
- [ ] Save run JSON files under `runs/`.
- [ ] Save transcript JSON files under `transcripts/`.
- [ ] Fill `artifacts/version_log.csv` with the v0-v3 evidence.
- [ ] Fill `artifacts/REPORT.md` with real screenshots/log references or file links.
- [ ] Keep UI runnable and show tool trace plus artifact version.

## What should be done by the group, not guessed

- [ ] Team member names.
- [ ] Provider/model actually used for the final demo.
- [ ] Final metric values from real runs.
- [ ] Final failure analysis from actual errors.
- [ ] The 10 custom eval cases that match your team focus.

## Recommended ownership split

- [ ] Tech lead: `system_prompt.md`, `tools.yaml`, version alignment.
- [ ] Provider owner: `.env`, provider preflight, Gemini runtime.
- [ ] Tool owner: tool implementation and `TOOL.md` files.
- [ ] Eval owner: `eval_base.json` review, `eval_group.json`, run analysis.
- [ ] UI owner: `app.py`, transcript display, demo flow.
- [ ] Report owner: `REPORT.md`, version log, final submission sanity check.

## Quick sanity checks

- [ ] `python -m compileall starter_v0`
- [ ] `python -m pytest -q` if tests are installed
- [ ] `streamlit run app.py`
- [ ] `python starter_v0/scripts/preflight_provider.py --provider gemini`

