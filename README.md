# FitTracker

A personal workout tracker built around the Lafay method's timed set/rest circuits: an exercise library
with variants and pictograms, session plans (warmup, workout, stretches), a guided run with a timer that
keeps going with the screen locked, and a short reflection after each session. Multi-user, installable as
a phone app (PWA), behind Caddy basic auth on the Raspberry Pi.

Built from the [pi-kit](https://github.com/alexis-massa/pi-kit) template (Rust: axum, sqlx; Svelte 5 PWA
embedded in the binary); the shared code is pinned by tag in `Cargo.toml` and `web/package.json`. The
Python/NiceGUI version is the git tag `python-final`; [PARITY.md](PARITY.md) lists every feature it had and
what proves the rewrite keeps it.

## Commands

| Command | Does |
| --- | --- |
| `just setup` | once after cloning: tools (mise), dependencies, git hooks |
| `just dev` | API + Vite with hot reload on http://localhost:5173 (starts the local Postgres) |
| `just fmt` / `just lint` | format / check everything (the pre-commit hook runs the checks) |
| `just test` | Rust tests against a fresh local database, then the web tests |
| `just prepare` | refresh `.sqlx/` after changing a query or a migration (commit it) |
| `just build` / `just image` | arm64 binary in `dist/app` / container image |
| `just deploy` / `just rollback` | ship the current commit to the Pi / go back to the previous image |
| `just logs` / `just status` | the app on the Pi |
| `just create-user NAME`, `just seed-exercises NAME` | on the Pi |
| `just schema-check FILE` | prove migration 1 equals a live schema dump |
| `just baseline`, `just ship` | cutover steps (PROGRESS.md) |

`INSTANCE=fittracker-preview just …` targets the preview instance instead of the live one.

CI (GitHub Actions, `.github/workflows/ci.yml`) runs `just lint`, `just test` and the builds on every push to
`main` and every pull request; it reads pi-kit with the repository secret `PI_KIT_DEPLOY_KEY` (pi-kit README,
"CI in an app"). Nothing is deployed from CI.

The binary: `fittracker serve | migrate | healthcheck | baseline | create-user NAME | set-password NAME |
list-users | delete-user NAME | claim-legacy NAME | seed-exercises NAME` (replacing the Python
`scripts/manage_users.py` and `scripts/seed_exercises.py`).

## Layout

- `src/` the server: `model.rs` (the stored JSON documents, with the Python field names and defaults),
  `docs.rs` (their storage, per user), `users.rs`, `routes.rs` (HTTP API), `commands.rs` (CLI).
- `migrations/` 0001 is the Python version's schema, unchanged; later ones are additive.
- `web/` the Svelte app: `src/pages/` one per URL (the same URLs as before), `src/lib/runner.ts` the
  timer core, `src/lib/workout.ts` its browser side (sound, wake lock, lock-screen controls).
- `data/lafay_exercises.json` the library `seed-exercises` adds, embedded in the binary.
- Files with a `# pi-kit vX.Y.Z` header are copied from pi-kit; upgrade them with pi-kit's UPGRADING.md.
  App-specific parts: the basic-auth labels in `compose.yml`, the recipes after the marker in `justfile`.

## Configuration

Environment only (`.env`, never committed; see `.env.example` and pi-infra's `APP_CONTRACT.md`):
`DATABASE_URL`, `APP_DOMAIN`, `BIND_ADDR`, `COOKIE_SECURE`, `SESSION_DAYS`, `RUST_LOG`, and on the Pi
`FITTRACKER_BASIC_AUTH_USER` / `FITTRACKER_BASIC_AUTH_HASH` (bcrypt, each `$` written `$$`).
