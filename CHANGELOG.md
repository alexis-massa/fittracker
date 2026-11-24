# Changelog

All notable changes. Versions are git tags (`vX.Y.Z`); `just deploy` deploys the checked-out commit and
names the image after `git describe`.

## Unreleased
- chore: upgrade to pi-kit v0.4.4 (no behaviour change)
- Login throttle: 5 failures per 15 min (was 5 min), pi-kit's default
- refactor: the workout type is `Workout`, so `Session` only means a login session (no behaviour change)
- chore: CI (GitHub Actions: lint, tests, builds) and Dependabot for the actions, from pi-kit v0.4.2

## [0.5.1] - 2026-11-15
- chore: upgrade to pi-kit v0.4.1, the same version as the other apps (no behaviour change)

## [0.5.0] - 2026-11-15
- Rewrite on the pi-kit stack (Rust + Svelte 5), same features and data (see PARITY.md); the Python
  version is the tag `python-final`.
- Login sessions are stored in the database: everyone logs in once more after the update.
- Old scrypt passwords keep working and are upgraded to argon2id at the next login.
- The installed app's shell opens without network.
- User admin is the binary's subcommands (`create-user`, `set-password`, `list-users`, `delete-user`,
  `claim-legacy`, `seed-exercises`).

## [0.4.0] - 2026-11-10
- feat: run the workout timer in the browser with lock-screen controls
- chore: trim the Docker image and keep logins across redeploys
- feat: add private multi-user accounts with per-user data, login and password change
- fix: send credentials when fetching the PWA manifest
- chore: remove release commit's self-referential changelog entry

## [0.3.0] - 2026-10-28
- feat: make FitTracker installable as a mobile home-screen app

## [0.2.1] - 2026-10-12
- fix: stop showing the exercise variant number twice in session views
- fix: drop app's depends_on db, which broke compose validation without the dev profile
- chore: remove release commit's self-referential changelog entry

## [0.2.0] - 2026-09-11
- feat: add exercise pictograms and clean up variant list display
- feat: add Lafay exercise dataset and seeding script
- feat: carry over sets/reps/rest from an exercise's last use
- feat: show live exercise counts in session-form group headers
- feat: carry over last logged weight into a fresh reflection
- feat: add Skip option to the post-run reflection screen
- feat: add Start button to sessions list
- feat: reflect on a session after running it, not before
- chore: exclude dev dependencies from the production image
- feat: migrate storage from MongoDB to shared Postgres
- chore: config for a common caddy docker
- feat: add guided session runner with rest/work timers
- fix: use NiceGUI's validation API instead of raw error props
- fix: preserve explicit zero for reps/duration/rest fields on save
- fix: add missing /sessions/{id}/duplicate route
- docs: credit the Lafay method as the training model

## [0.1.0] - 2026-09-09
- ci: add GitHub Actions workflow for lint, type check, and tests
- test: add pytest suite for models and utils layer
- feat: mark invalid fields inline instead of only toasting
- refactor: clarify rest-before vs rest-between-sets fields
- feat: make exercise picker searchable
- feat: confirm before deleting sessions and exercises
- feat: add duplicate/repeat session action
- feat: convert pages to real url routes, drop in-memory router
- refactor: extract header building into _render_header helper
- fix: prevent header overflow on mobile viewports
- fix: correct grey-7 typo and outline input fields for consistency
- fix: replace dead spacer/heading classes with Quasar utilities
- fix: unify exercise-effort form styling and stack fields on mobile
- fix: restore card containers and text hierarchy on list rows
- fix: small bug fixes (rest_before/duration, dead code, port config)
- chore: ignore .claude/worktrees/ (Claude Code agent scratch worktrees)
- chore: add MIT license, changelog tooling, setup script, and rewrite README
