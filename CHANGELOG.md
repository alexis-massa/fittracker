# Changelog

All notable changes to this project are documented here. Format loosely
follows [Keep a Changelog](https://keepachangelog.com/). New entries are
appended automatically to `[Unreleased]` by a commit hook (see
[README.md](README.md)); versions are cut and tagged on `main` by hand.

## [Unreleased]
- feat: add Skip option to the post-run reflection screen
- feat: add Start button to sessions list
- feat: reflect on a session after running it, not before
- feat: reflect on a session after running it, not before
- chore: exclude dev dependencies from the production image
- feat: migrate storage from MongoDB to shared Postgres
- chore: config for a common caddy docker

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
