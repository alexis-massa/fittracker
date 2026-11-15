# FitTracker – progress

Handoff between work sessions: read it first, update it last. The whole rewrite is tracked in pi-infra's
PROGRESS.md (phase 2 = this app).

## State (2026-11-14)
- Rewrite on branch `rust-rewrite` (pi-kit v0.3.1), PR open, **not merged: waiting for the owner's test**.
- Python version: tag `python-final` (= v0.4.0), still the live app (`~/fittracker` on the Pi, compose project
  `fittracker`, image `fittracker-app`).
- [PARITY.md](PARITY.md): 30 of 32 items done with tests; open: lock-screen controls on a phone, basic auth
  (both for the owner's test on the preview).
- Checks: `just lint`, `just test` (7 unit, 12 API and 2 CLI tests against Postgres, 32 web tests),
  `just schema-check ~/pi-baseline/schemas/fittracker.schema.sql` (migration 1 = live schema).
- Checked by hand: every page in the browser pane (login redirect, library, new session with picker and the
  reps/duration rule, detail, run with countdown, skip, reflection, theme toggle, 375 px wide with no
  horizontal scroll); PWA in headless Chromium (service worker active, manifest with credentials, 3 icons).
  The in-app browser pane cannot register service workers, so that check needs a real Chromium.

## Preview (for the owner's test)
- https://fittracker-preview.dermaquiz.duckdns.org — same basic auth as the live app, then the usual login.
  Everyone logs in again (sessions are new); passwords are the live ones (the data is a copy).
- Pi: `~/fittracker-preview/` (compose project `fittracker-preview`), database and role `fittracker_preview`, a
  restored copy of `fittracker` taken 2026-11-14 19:27 UTC (`~/backups/fittracker/fittracker-20261114-192707.dump`).
  Changes made on the preview never reach the live data.
- Measured on the Pi (idle, after a deploy): RSS 3.5 MB (Python: 95 MB), image 5.8 MB (Python: 467 MB), deploy
  64 s from a clean build (12 s from start to healthy).
- To try on a phone: install it from the browser menu, start a session's run, lock the screen; pause/skip
  should be on the lock screen and the timer should keep going.

## Cutover (after the owner's OK)
Downtime is about a minute. Each command is run as written; nothing here touches other apps.
1. Merge the PR (rebase), tag `v0.5.0` on `main`, `git switch main && git pull`.
2. On the Pi: `~/pi-infra/backup.sh fittracker` and `~/pi-infra/restore.sh fittracker DUMP --check`.
3. `just ship` (image + `compose.yml` into `~/fittracker`; the old app keeps running from `docker-compose.yml`).
4. Stop the old app: `cd ~/fittracker && docker compose -f docker-compose.yml -f docker-compose.prod.yml stop app`
   (stopped, not removed: its image `fittracker-app` stays for rollback).
5. `just baseline` (records migration 1 on the live database), then `just deploy` (migration 2 at start).
6. `.env` on the Pi: add `APP_DOMAIN` (the live host) if missing; the basic-auth lines are already there.
7. Remove the preview: `INSTANCE=fittracker-preview` … `docker compose -p fittracker-preview -f compose.yml down`,
   then `~/pi-infra/remove-app.sh fittracker-preview` and `rm -r ~/fittracker-preview`.
8. Measure (RSS, image, deploy time) and record them in pi-infra's PROGRESS.md.

## Rollback
- To the previous new-stack image: `just rollback`.
- To the Python app: `cd ~/fittracker && docker compose -p fittracker -f compose.yml down`, then
  `docker compose -f docker-compose.yml -f docker-compose.prod.yml start app`. The schema is unchanged except
  the extra `auth_sessions` table, which Python ignores. **But** users who logged in on the new app have
  argon2id hashes that the Python version cannot read: either restore the dump from step 2
  (`restore.sh fittracker DUMP`, loses changes made since), or set their passwords again with the Python CLI.

## Session log
| Date | Done | Next |
| --- | --- | --- |
| 2026-11-14 | Rewrite: backend, frontend, tests, docs; pi-kit v0.2.0–v0.3.1 for what it needed; preview deployed on a copy of the data | (human) owner tests the preview; then the cutover above |
