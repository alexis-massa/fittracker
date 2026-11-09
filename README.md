# FitTracker

A personal workout tracker. Log sessions made of warmup, workout, and
stretch exercises — each with sets, reps or duration, and rest timing — and
build up a small exercise library (with variants, e.g. "Pushup" → "Wide
grip") as you go, including creating new exercises on the go while logging
a session.

A personal hobby project, built largely as an experiment in
pair-programming with Claude.

## Training method

The set/rep/rest model is built around Olivier Lafay's *Méthode de
musculation* (bodyweight-only circuits of timed series, with strict,
prescribed rest between each series and between exercises — progression
comes from adding reps at a fixed rest time, never from cutting rest
short). That's why every exercise entry in a session tracks `rest_before`
(the transition rest before starting it) and `rest_seconds` (rest between
series) as first-class fields alongside sets/reps — the method itself is
built around exact timing, which is also why a guided, timer-driven
"run session" mode (rather than just logging after the fact) is the
natural direction for this app.

## Stack

[NiceGUI](https://nicegui.io) (renders a Vue/Quasar UI from pure Python —
no separate frontend or build step), PostgreSQL (JSONB documents, no ORM)
for storage, `uv` for dependency management. In production this shares a
Postgres instance with a sibling project rather than running its own.

## Local development

```bash
./setup.sh
```

Writes `.env` and installs dependencies and git hooks. Refuses to run if
`.env` already exists, so it's safe to leave lying around — remove `.env`
first if you want to regenerate it.

Then start the local Postgres:

```bash
docker compose up -d db
```

Create your login (there is no signup page - see [Users and access](#users-and-access)):

```bash
uv run python scripts/manage_users.py create YOURNAME
```

And run the app:

```bash
uv run main.py
```

## Running a workout

"Start" on a session opens a guided timer. The clock runs in your browser
rather than on the server, so it keeps going when the screen locks, and it
plays a beep at every step. Tapping **Start workout** keeps the screen on and
puts controls on your lock screen / notification shade (Media Session API):

| Control | Does |
| --- | --- |
| play / pause | pause or resume the timer |
| next | skip to the next step |
| previous | restart this step; twice in a row goes back one step |
| stop | leave the workout (nothing is saved) |

**Reset workout** (start over) is in the app only, to avoid a stray tap on the
lock screen wiping your progress. The lock-screen controls rely on a silent
audio loop (browsers only show them for audio, and keep the page alive for it),
so which buttons appear depends on your phone and browser. If the page is
killed in the background the workout restarts from the beginning.

JS timer tests run with `node --test tests/js/*.test.js` (no dependencies).

## Users and access

The app is private: every page requires a login, and each user has their own
sessions, exercise library and preferences — nobody can see or touch another
user's data. Accounts can only be created by whoever runs the admin script, so
you hand out access yourself:

```bash
uv run python scripts/manage_users.py create alice     # prompts for a password
uv run python scripts/manage_users.py passwd alice     # reset a password
uv run python scripts/manage_users.py list             # who exists, and how much data
uv run python scripts/manage_users.py delete alice     # removes them and ALL their data
uv run python scripts/seed_exercises.py alice          # give them the Lafay exercise library
```

In production, run them inside the container, e.g.
`docker compose exec app .venv/bin/python scripts/manage_users.py create alice`.

Users can change their own password from the account menu in the header.

**Upgrading from the single-user version:** the first start adds an owner
column to your existing tables, so take a backup first
(`pg_dump "$DATABASE_URL" > fittracker-backup.sql`). Existing sessions and
exercises have no owner, so they stay hidden from everyone until you assign
them to your account, once, after creating it:

```bash
uv run python scripts/manage_users.py claim-legacy YOURNAME
```

Production needs `STORAGE_SECRET` set (a long random string that signs the
login cookies; the app refuses to start without it — see `.env.example`).
Logins are kept in a Docker volume (`nicegui-storage`), so redeploys don't
sign anyone out. The login form is throttled (5 failed attempts per
username, then a 5-minute lock), and you can drop the Caddy `basic_auth` labels
in `docker-compose.prod.yml` if you'd rather not have a second login in front.

## Code quality

`ruff` (lint + format) and `mypy` (strict) run on every commit via
[lefthook](https://github.com/evilmartians/lefthook) — installed
automatically by `setup.sh`.

## Changelog

[CHANGELOG.md](CHANGELOG.md) follows [Keep a Changelog](https://keepachangelog.com/).
A commit hook (`scripts/append-changelog.sh`) automatically appends every
commit's subject line to the `[Unreleased]` section — versions are cut and
tagged on `main` by hand.

## License

[MIT](LICENSE)
