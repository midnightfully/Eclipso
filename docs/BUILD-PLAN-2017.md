# Roblox 2017 revival — build plan

Planning baseline: mid-2017 desktop website. The existing folder named 2016-roblox-main is a starting implementation, not evidence of 2017 accuracy. This plan separates local API verification, browser verification, and public launch readiness.

## 1. Preserve and organize the working project

Keep this checkout at its current path until absolute configuration paths have been replaced. Use Start Website.cmd, Stop Website.cmd and Set Website Owner.cmd at the root. Source remains in its upstream folders to keep diffs reviewable; documentation is in docs/, operational scripts in local/, historical setup attempts in local/archive/, and private runtime state in .local/.

Back up PostgreSQL using pg_dump plus asset storage and application signing keys. A backup was taken before changing account 1. Do not commit .local/, generated configuration, logs, credentials, database dumps, dependency caches, or live account data. Add a reproducible clean-machine installer and versioned migrations before staging; the current launcher starts the installed local environment, not a portable installer.

Gate: another clean Windows environment can restore the database and storage and start the same tested revision without undocumented manual edits.

## 2. Finish the website workflows

| Area | Required behavior | Acceptance test |
|---|---|---|
| Accounts | Registration, unique usernames, login/logout, account settings and recovery | Duplicate/case-variant names rejected; session expires/revokes; wrong passwords rejected; create and sign in through the actual site in Opera GX |
| System profile | ID 1 is Roblox; exact supplied biography; automated identity separate from human owner | API and browser profile match docs/roblox-profile.json after restart |
| Friends | Request, accept, decline, cancel, remove; correct lists/counts | Two normal accounts complete every transition; self-request and duplicate requests do not create duplicate friendships |
| Groups | Create, icon, join/leave, wall, roles, owner management, funds | Charge exactly once; failure rolls back; non-owner cannot change roles/spend funds; browser flows complete |
| Economy | Balances, prices, inventory, purchase history, limited serials and resale | Concurrent buyers cannot oversell the last serial; stale price and insufficient balance reject without mutation; transfer and fee ledger reconcile |
| Catalog publishing | Staff upload, validate, moderate, preview, set price/stock, publish/off-sale | File survives restart; ordinary user cannot publish first-party limiteds; finite stock and resale agree with inventory |
| Admin | Personal owner setup, scoped staff permissions, moderation and audit logs | Owner can manage intended functions; ordinary users receive 403; no system-account login required |
| Inventory/avatar | Assets, thumbnails, equipped appearance | Real uploaded assets display correctly; renderer failure is visible and cannot block unrelated website requests |

Current API evidence is in TEST-REPORT.md. A successful API call is not a passed browser test. Local test-credit grants are development fixtures; production balance changes require controlled, audited rules. Finish account recovery and reliable image/asset processing before inviting public users.

## 3. Match the 2017 website

Collect dated 2017 references for the logged-out landing page, home, profile, friends, catalog list/detail, groups list/detail/manage, inventory, avatar, develop/create, trade, settings and upgrade pages. Store reference dates and image sources alongside the page checklist. Implement shared navigation, typography, spacing, icons, buttons, pagination, dialogs and empty states before per-page polish.

Use period vocabulary: Games, Catalog, Develop, Builders Club, Turbo Builders Club and Outrageous Builders Club. Exclude Premium branding, later verified checkmarks, modern UGC accessory publishing and 2020 menu options from the 2017 public interface. Ordinary creators can use the period-appropriate creation flows; first-party hats and limiteds belong to staff publishing tools. Keep Tix out of the active economy for this baseline. Verify period membership limits and selling rules instead of copying the upstream modern defaults. The current group service permits up to 100 memberships and does not check Builders Club during creation, so functional groups alone do not establish historical accuracy.

Preserve the exact requested Roblox biography, including its original external links. The revival itself needs its own project identity and support contact; do not redirect real Roblox credentials or payments into this local system.

Gate: a page-by-page reference comparison at desktop sizes, followed by keyboard and Opera GX click-through checks. Nothing is labeled historically complete until the comparison is recorded.

Historical source: Roblox's [September 2019 Premium announcement](https://devforum.roblox.com/t/roblox-premium-is-here/355721) establishes that Premium branding is later than the requested baseline. Remaining detailed visual references must be captured and dated before claiming pixel accuracy.

## 4. Prepare a public release

The [upstream repository](https://github.com/harryzawg/bubbablox-v2) explicitly warns about a known remote-code-execution issue and says it is no longer maintained. Its exact root cause has not been independently established or patched in this pass. The current build also reports vulnerable dependency warnings, including a critical System.Drawing.Common advisory. These are concrete launch blockers.

Work required:

- Identify the reported vulnerability and inspect upload conversion, archive/XML parsing, subprocess invocation, internal service authentication and website-update endpoints; add regression tests for the actual findings.
- Upgrade vulnerable .NET, Next, image-processing and admin dependencies with compatibility tests.
- Create separate local, staging and production configuration. Merely setting LocalDevelopment=false currently re-enables external application checks and game/render startup paths; refactor these into independent explicit settings first.
- Exclude local signup/grant/seed/testing endpoints from public release. Reject any public request to those routes even through a loopback reverse proxy. Never expose this development server using router port forwarding.
- Run production-built frontend and backend services. No next dev or debug error pages. Move secrets into server configuration, rotate development secrets, enable HTTPS-only cookies, and configure forwarded headers only for the trusted proxy.
- Apply rate limits to registration/login, friend requests, group creation, uploads and purchases. Add upload type/size limits and isolated processing. Review authorization and transaction handling.
- Restrict database and cache to the host/private network; separate application database credentials from the PostgreSQL superuser. Require strong owner access and audit sensitive admin mutations.

Gate: no unresolved critical launch findings, passing authentication/authorization and economy concurrency tests, and a reviewed production configuration.

## 5. Put staging online

Use a VPS with persistent storage for the web app, PostgreSQL, cache and uploaded files. Keep game servers separate. The present build has Windows-specific image-processing and path dependencies. Test Linux compatibility before choosing a Linux deployment; Windows hosting is the direct compatibility route, with its own service-management setup. Do not purchase hardware based on an untested capacity claim.

Start with one staging machine. Measure memory, CPU, upload storage and concurrent-user load, then select a production plan. Put a reverse proxy and TLS in front of the backend; the backend already proxies frontend routes. Set canonical domain/base/CDN/asset URLs together. Configure service boot and restart policies, health monitoring and daily backups to another location. Exercise a restore onto a second clean environment and a rollback to the previous build.

Gate: registration, friends, groups, uploads, purchases and admin tests pass over HTTPS from an external browser. Reboot and process-crash tests recover the site. Restore preserves accounts, balances, serial ownership, assets and login keys.

## 6. Release the website beta

Freeze a revision, publish an internal changelog, and use a small invited test population. Complete the acceptance matrix, resolve broken routes/images, and run a soak test before opening broader signups. Agree on backup retention, acceptable data loss and recovery time. One VPS is an always-on deployment target, not guaranteed uninterrupted service; high availability is a later multi-instance/database project.

The public currency is this revival's own database economy. Real-money payments are outside this phase. No client launch button should imply that a game service exists yet.

## 7. Add clients and multiplayer after the website gate

Choose and document one 2017 client/server version; inventory the actual binaries and protocol expectations. Implement launch tickets, asset delivery, authentication and place loading against an isolated game-worker service. Then test single-player join, two-player replication, disconnect/rejoin, server lifecycle, capacity, crash recovery and version compatibility. Keep render workers and game workers isolated from website credentials and the database. The current setup has not downloaded or started a complete playable client/server deployment.

Website completion does not establish client compatibility. Multiplayer is a separate milestone with its own tests and hosting budget.
