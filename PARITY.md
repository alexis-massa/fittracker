# Feature parity with the Python version

Checklist for the rewrite (pi-infra phase 2): every behaviour of `python-final` (v0.4.0, NiceGUI), and what
proves the new version has it. `[x]` = done and covered by the test named; `(manual)` = checked by hand in
the browser, listed in PROGRESS.md.

## Accounts and access
- [x] Every page and API needs a login, except the login page, the PWA files and the health check — `tests/api.rs::anonymous_requests_are_refused`
- [x] Login with user name (any case) and password; wrong password and unknown user fail the same way — `tests/api.rs::login_logout_and_password_change`
- [x] 5 failed logins per user name in 5 minutes lock that name, even with the right password — `tests/api.rs::login_is_throttled`
- [x] Existing scrypt password hashes keep working and are upgraded to argon2id on login — `tests/api.rs::legacy_scrypt_hash_logs_in_and_is_upgraded`
- [x] After login, back to the page first requested (local paths only) — `web/src/lib/router.test.ts`
- [x] Change password (current password checked, throttled, 8+ characters, repeated) — `tests/api.rs::login_logout_and_password_change`
- [x] Sign out — `tests/api.rs::login_logout_and_password_change`
- [x] A deleted user is logged out on the next request — `tests/api.rs::deleted_user_is_logged_out`
- [x] Dark mode is a per-user preference, toggled from the header — `tests/api.rs::preferences_are_per_user`, (manual)
- [ ] Caddy basic auth in front of the whole site (labels from `.env`) — `compose.yml`, (manual: owner's test on the preview)

## Data isolation
- [x] A user only lists, opens, changes and deletes their own sessions and exercises — `tests/api.rs::users_cannot_touch_each_others_data`
- [x] "Last used" values never come from another user's sessions — `tests/api.rs::last_used_effort`

## Exercise library
- [x] List sorted by name, with variants; count shown — `tests/api.rs::exercise_crud`, (manual)
- [x] Create inline (name required, label, variants; empty-named variants dropped) — `tests/api.rs::exercise_crud`
- [x] Edit name, label and variants (add, rename, remove) — `tests/api.rs::exercise_crud`
- [x] Delete with confirmation — `tests/api.rs::exercise_crud`, (manual)
- [x] Pictogram per exercise letter (fallback figure), enlarged on click — `web/src/lib/phases.test.ts` (pictograms)

## Sessions
- [x] List newest first (date, exercise/warmup/stretch counts, energy and progress or "Not completed yet"), with Start, Duplicate, View — `tests/api.rs::session_crud`, (manual)
- [x] Detail: energy, progress, weight, notes when completed; warmup, workout, stretches; Start, Edit, Duplicate, Delete (confirmed) — (manual)
- [x] New and duplicate: three groups, add/edit/remove/reorder exercises — `tests/api.rs::session_crud`, (manual)
- [x] Edit an existing session also edits its info (date required, weight, energy, progress, notes) and marks it completed — `tests/api.rs::session_crud`
- [x] Exercise picker: exercise and variant from the library, or create a new exercise inline — (manual)
- [x] Sets 1–100, rest before 0–3600 s, rest between sets 0–3600 s, reps 0–200, duration 0–999 s; reps or duration, not both — `tests/api.rs::session_validation`
- [x] A fresh row is pre-filled from the last use of that exercise, preferring the same variant — `tests/api.rs::last_used_effort`
- [x] Stored documents keep the Python field names and defaults, so old and new rows read the same — `src/model.rs` tests

## Guided run
- [x] Phases: rest before (if > 0), then per set work (timed or reps), rest between sets — `web/src/lib/phases.test.ts`
- [x] Timer in the browser: start, pause/resume, skip, restart phase, previous (double press), reset workout, stop; catches up after a frozen tab — `web/src/lib/runner.test.ts` (port of `runner.test.js`)
- [ ] Screen kept on, lock-screen controls (Media Session), beep on each phase change, silent audio to stay alive — (manual, phone: owner's test on the preview)
- [x] Reflection at the end (date, weight pre-filled from the last completed session, energy, progress, notes), Save or Skip — `tests/api.rs::last_weight`, (manual)

## Install and tooling
- [x] Installable PWA (manifest with credentials, icons, service worker) — (manual: headless Chromium, PROGRESS.md)
- [x] CLI: `create-user`, `set-password`, `list-users` (with counts and unowned rows), `delete-user` (typed confirmation), `claim-legacy`, `seed-exercises` (Lafay library, skips existing names) — `tests/cli.rs`
- [x] Runs on the existing database unchanged (baseline migration equals the live schema) — `just schema-check`

## No longer applicable
- The Python test that inline `<script>` JSON could not break out of its tag: there is no inline script any more, and Svelte escapes all text.
- The NiceGUI websocket reconnect timeout for a locked phone: the run page no longer needs a server connection while running.
