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
