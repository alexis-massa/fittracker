# Decisions

Choices this app made where pi-kit or the brief left a detail open. Newest first. Stack-wide choices are
in pi-kit's DECISIONS.md.

| Date | Decision | Why |
| --- | --- | --- |
| 2026-11-14 | The PWA icons stay in git (`web/public/icons`), as in the Python version | They are source assets of the app, not container or content images |
| 2026-11-14 | Version 0.5.0 for the rewrite | Same features and data, so not a 1.0 break; the Python version is `python-final` (v0.4.0) |
| 2026-11-14 | Exercises and sessions share one generic storage module (`docs.rs`) with runtime-checked SQL; everything else uses compile-time checked `query!` | The two tables have the same shape; `query!` needs literal SQL per table, which would duplicate every query. The integration tests cover these queries |
| 2026-11-14 | Stored JSON keeps the Python field names, defaults and `null`s; ids in the API are numbers | Rows stay readable by either version (rollback to `python-final` keeps working) |
| 2026-11-14 | The API validates what the Python forms validated (ranges, reps or duration, date) | The forms are now client-side; the server must not trust them |
| 2026-11-14 | Login throttle keeps the Python limits: 5 failures per user name in 5 minutes | Parity |
| 2026-11-14 | Changing one's password keeps the current session; `set-password` (CLI) ends all of them | Parity with the Python account menu; the admin command is the "lock everyone out" tool |
| 2026-11-14 | Users log in once more after the cutover | NiceGUI kept sessions in its file storage; passwords (scrypt) are kept and upgraded to argon2id at login |
| 2026-11-14 | Deletes ask with the browser's `confirm()` | Same behaviour as the Python dialog, no extra component |
| 2026-11-14 | The service worker precaches the app shell (pi-ui preset) | The Python one only made the app installable; the shell now opens without network, data still needs it |
| 2026-11-14 | Pictograms are generated from the Python source into `web/src/lib/pictograms.ts` | One mechanical copy instead of re-typing 26 SVGs |
| 2026-11-14 | No GitHub Actions; `just lint` / `just test` and the pre-commit hook | Fresh-clone builds need the private pi-kit; local checks are enough for one maintainer |
| 2026-11-14 | Preview instance `fittracker-preview` on `fittracker-preview.dermaquiz.duckdns.org`, on a copy of the database (removed at the cutover) | DuckDNS resolves sub-names of a working domain, so no new DNS record; the copy kept the live data safe |
