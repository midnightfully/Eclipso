# Eclipso status

Updated 2026-10-28 by Claude. Keep this short; details live in FEATURE-MATRIX.md and TEST-REPORT.md.

## Current phase
**Phase 1 — website** (then single-player client → Studio → multiplayer, in that order).

## Where things run
| Environment | URL | What it is |
|---|---|---|
| Public | https://eclipso.lol, https://staging.eclipso.lol | **Static "Coming soon" page only** (Caddy on the Hostinger VPS). No accounts, backend or database online. |
| Local (kindmops's PC) | http://127.0.0.1:5080 | The real website: .NET 10 backend :5080, Next.js production build :3000 (`next start`), PostgreSQL 16 :15432, Garnet cache :16379. Start/stop with the root .cmd launchers. |

Repository: github.com/midnightfully/Eclipso. `main` = upstream bubbablox-v2 history. Work branches:
`claude/recover-startup` (startup, routing, CSP, landing, VPS) → `claude/admin-milestone` (admin, publishing, economy) → `claude/website-completion` (launcher, production frontend, sessions, branding). None merged yet.

Data: local DB `.local/pgdata-ready`; uploaded assets `.local/storage/asset`; thumbnails and group icons
`api/public/images/{thumbnails,groups}` (git-ignored). Backups: `.local/backups/` (pg_dump before every migration).
Schema changes: `api/sql/migrations/` via `python local/migrate.py`.

## Verified (with evidence)
- Local startup/stop/restart; backend build 0 errors.
- Accounts API: `local/test-signup-2017.py` 10/10.
- Admin authorization + audit trail: `local/test-admin.py` 7/7.
- Publishing (Image type) + economy incl. limited-unique concurrency and resale: `local/test-economy-pipeline.py` 10/10.
- Purchases, serials and resale history survive a full stack restart.
- Owner = Midnight (#36), confirmed by kindmops; recorded in admin_audit_log.
- Sessions persist in PostgreSQL (30-day expiry, revocation): `local/test-sessions.py` 4/4.
- Browser: staff opened admin dashboard, published an Image item through the form; buyer bought it through the item page (DB verified).
- Frontend now served from a production build (`local/build-frontend.cmd`, then restart).

## Active work
Security pass (upstream RCE report, CSRF bypass prefixes, admin copy/upload routes, local-only endpoints), then
the game renderer (needed for wearable items and avatars).

## Known failures / gaps
- Wearable items (hats, gear, clothing, faces, packages) need the RCC-based game renderer for thumbnails and
  avatar renders; it is not set up. Model uploads also need the separate AssetValidationService (not present).
- Limited/resale browser walkthrough not yet done by Claude (API-verified; kindmops Guide C/D).
- Mobile/narrow layout: the 2017 login card overflows off-screen below ~850px width.
- Upstream RCE report not yet located; dependency advisories (e.g. ImageSharp 2.1.3) not yet upgraded.
- Several URL "bypass" prefixes (e.g. `/users/`, `/asset`) are exempt from CSRF checks.
- Local-only endpoints (`/local/*`) are gated by LocalDevelopment + loopback; behind a reverse proxy every
  request is loopback, so production must use a separate flag before deployment.

## External blockers (need kindmops)
None right now. Renderer/validation binaries may be needed later (see FEATURE-MATRIX "Blocked").

## Exact next step
1. kindmops runs docs/TESTING-GUIDE.md sections A–D in Opera GX and reports results.
2. Claude: set up the local renderer (upstream `renderer/` + RCCService) so one wearable type completes the pipeline.
