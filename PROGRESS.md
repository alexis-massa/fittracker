# FitTracker – progress

Handoff between work sessions: read it first, update it last. The whole rewrite is tracked in pi-infra's
PROGRESS.md (phase 2 = this app).

## State (2026-11-15)
- **Live on the new stack** (v0.5.0, pi-kit v0.3.1) at https://fitracker.duckdns.org (note: one `t`), behind Caddy
  basic auth. Cut over 2026-11-15 08:48 UTC; the Python version is the tag `python-final`.
- Cutover: backup (restore-checked) → image shipped while the old app ran → old app stopped → `baseline` →
  `deploy`. 76 s from stop to healthy (about 40 s of it a needless rebuild: next time `just ship`, stop, then
  `./deploy.sh fittracker v0.5.0`).
- Data unchanged: 2 users, 53 exercises, 1 session; migrations `1` (baseline, recorded not run) and `2`.
- [PARITY.md](PARITY.md): all 32 items done (the phone lock-screen and basic-auth items were checked by the
  owner on the preview).
- Idle: RSS 3.4 MB (Python 95 MB), image 5.8 MB (467 MB).
- Everyone logs in again once (sessions are new); old scrypt hashes are upgraded to argon2id at each user's
  next login.

## Kept for rollback (delete only with the owner's OK, pi-infra phase 5)
- Image `fittracker-app:latest` (the Python app, 467 MB), volumes `fittracker_nicegui-storage` and
  `fittracker_mongodata`, and `~/fittracker/docker-compose*.yml` on the Pi.
- Pre-cutover dump: `~/backups/fittracker/fittracker-20261115-084731.dump` (path also in `~/fittracker/.pre-cutover-dump`).

## Rollback
- To the previous new-stack image: `just rollback` (tested on the hello app).
- To the Python app (**not tested end to end**): `cd ~/fittracker && docker compose -p fittracker -f compose.yml down`,
  then `docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d app` (recreates the container).
  The schema only gained the `auth_sessions` table, which Python ignores. Users who logged in since the cutover
  have argon2id hashes that the Python version cannot read: restore the dump above
  (`~/pi-infra/restore.sh fittracker DUMP`, loses changes since) or set their passwords again.

## Session log
| Date | Done | Next |
| --- | --- | --- |
| 2026-11-15 | Cutover to v0.5.0; preview removed; docs updated | Owner: log in once and check; later pi-infra phase 5 decides when the old image and volumes go |
| 2026-11-14 | Rewrite: backend, frontend, tests, docs; pi-kit v0.2.0–v0.3.1; preview on a copy of the data | Owner test, then cutover |
