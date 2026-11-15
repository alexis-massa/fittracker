# FitTracker – progress

Handoff between work sessions: read it first, update it last. The whole rewrite is tracked in pi-infra's
PROGRESS.md (phase 2 = this app).

## State (2026-11-15)
- **Live on the new stack** (v0.5.1, pi-kit v0.4.1) at https://fitracker.duckdns.org (note: one `t`), behind Caddy
  basic auth. Cut over 2026-11-15 08:48 UTC; the Python version is the tag `python-final`. `main` is ahead of
  the deployed version by CI, docs, pi-kit v0.4.2 (no code change) and patch-level dependency updates; the next
  deploy ships them.
- Cutover: backup (restore-checked) → image shipped while the old app ran → old app stopped → `baseline` →
  `deploy`. 76 s from stop to healthy.
- Data unchanged: 2 users, 53 exercises, 1 session; migrations `1` (baseline, recorded not run) and `2`.
- [PARITY.md](PARITY.md): all 32 items done (the phone lock-screen and basic-auth items were checked by the
  owner on the preview).
- Idle: RSS 3.4 MB (Python 95 MB), image 5.8 MB (467 MB).
- Old scrypt hashes are upgraded to argon2id at each user's next login.
- CI: GitHub Actions runs `just lint`, `just test` and the builds on every push and pull request
  (`.github/workflows/ci.yml`, secret `PI_KIT_DEPLOY_KEY`); Dependabot bumps the actions monthly.
- Nightly backup on the Pi: `backup.sh fittracker` at 03:20 (pi-infra README).
- Nothing technical is open: new work is features.

## Python leftovers
Removed from the Pi in pi-infra phase 5 (2026-11-15, see its REPORT.md): the Python image, the
`fittracker_nicegui-storage` and `fittracker_mongodata` volumes (only MongoDB system data) and the old compose
files. The pre-cutover dump stays: `~/backups/fittracker/fittracker-20261115-084731.dump`.

## Rollback
- To the previous image: `just rollback`.
- To the Python app (**not tested**): rebuild it from the tag `python-final`. The schema only gained the
  `auth_sessions` table, which Python ignores; users who logged in since the cutover have argon2id hashes that
  the Python version cannot read: restore the dump above (`~/pi-infra/restore.sh fittracker DUMP`, loses changes
  since) or set their passwords again.

## Session log
| Date | Done | Next |
| --- | --- | --- |
| 2026-11-15 | Tidy-up: CI and Dependabot (pi-kit v0.4.2), annotated tags and GitHub release v0.5.1, docs | Features only |
| 2026-11-15 | v0.5.1 (pi-kit v0.4.1) deployed; Python leftovers removed from the Pi (pi-infra phase 5) | |
| 2026-11-15 | Cutover to v0.5.0; preview removed; docs updated | Owner: log in once and check; later pi-infra phase 5 decides when the old image and volumes go |
| 2026-11-14 | Rewrite: backend, frontend, tests, docs; pi-kit v0.2.0–v0.3.1; preview on a copy of the data | Owner test, then cutover |
