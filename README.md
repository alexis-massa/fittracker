# FitTracker

A personal workout tracker. Log sessions made of warmup, workout, and
stretch exercises — each with sets, reps or duration, and rest timing — and
build up a small exercise library (with variants, e.g. "Pushup" → "Wide
grip") as you go, including creating new exercises on the go while logging
a session.

A personal hobby project, built largely as an experiment in
pair-programming with Claude.

## Stack

[NiceGUI](https://nicegui.io) (renders a Vue/Quasar UI from pure Python —
no separate frontend or build step), MongoDB for storage, `uv` for
dependency management.

## Local development

```bash
./setup.sh
```

Prompts for a MongoDB connection string (leave blank to use a local
MongoDB), writes `.env`, and installs dependencies and git hooks. Refuses
to run if `.env` already exists, so it's safe to leave lying around —
remove `.env` first if you want to regenerate it.

Then:

```bash
uv run main.py
```

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
