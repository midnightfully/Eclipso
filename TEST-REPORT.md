# Local website verification — 2026-10-27

| Check | Result | Evidence |
|---|---|---|
| .NET backend compilation | PASS | 0 errors; upstream warnings remain in .local/backend-build.log |
| PostgreSQL schema import | PASS | Atomic import; 98 public tables, including the local grant log |
| Local fixture seeding | PASS | Catalog records created through /local/seed |
| Account creation | PASS | Two accounts created and authenticated |
| Test-robux grant | PASS | Database balance increased by 10,000 |
| Ordinary purchase | PASS | Balance decreased by 25; item added to inventory |
| Duplicate purchase | PASS | Request rejected; balance and inventory unchanged |
| Limited resale | PASS | Existing user-asset copy transferred to another account; buyer debited and seller credited |
| Logout/login persistence | PASS | Same balance and inventory after authentication cycle |
| Backend and full-service restart persistence | PASS | Saved account restored with 9,475 test robux and three owned items after clean stop/start |
| Limited-unique purchase | PASS | Serial 1 assigned; balance decreased by 100 |
| Local dashboard HTTP response | PASS | /local returned HTTP 200 |
| Original home page HTTP response | PASS | /home returned HTTP 200 |
| Original catalog HTTP response | PASS | /catalog returned HTTP 200 |
| Browser rendering and clicks | UNVERIFIED | Built-in browser timed out; isolated Opera launch was blocked by the execution environment |
| Full supervisor start/stop cycle | PASS | Supervisor reached Ready; stop request shut down all services and PostgreSQL cleanly |
| Game clients and multiplayer | NOT IMPLEMENTED | Deferred to the next phase |

The verification accounts and their purchases remain in the local database. Source test scripts in local/ record the initial fresh-database checks; they are not a database-reset mechanism.

## Implementation notes

The local dashboard uses the original signup service, session cookies, economy purchase endpoint, resale endpoint, and database tables. It adds local-only account entry points, explicit credit grants, and sample catalog fixtures. Purchases are not browser-only simulations.

The .NET projects target the installed .NET 10 SDK. Repairs include an ambiguous JSON overload, invalid prose in an upstream C# file, empty game-server configuration binding, database startup connection disposal, and local encryption-key storage. Renderer startup and game-server cleanup are skipped in local mode. Daily automatic stipends and external IP lookups are disabled during local testing so balance checks remain deterministic.

Microsoft Garnet 2.2.4 provides the Redis protocol cache with Lua enabled; the downloaded native Redis ports could not run in this execution environment. PostgreSQL 16.15 is portable and stored in the project. Frontend runtime versions are pinned in package.json/package-lock.json; the original development dependency manifest is saved in local/frontend-package.original.json.

## Website expansion verification — 2026-10-27

| Feature | Implemented | Tested | Result | Remaining limit |
|---|---|---|---|---|
| Roblox user 1 and exact biography | Yes | DB and public API, including restart | PASS | Browser layout unverified |
| Seed fixture remains owned by user 1 | Yes | Repeat seed, compare account count | PASS | Local-only fixture endpoint |
| Friends request/accept/remove | Upstream implementation | Two real test accounts | PASS | Decline/cancel, counts, races and browser controls not yet covered |
| Create group and public join | Upstream implementation | API with PNG icon, 100-robux debit, second-account membership | PASS | Wall, roles, funds and failure rollback not yet covered |
| Group creator ownership | Upstream implementation | Read after full service restart | PASS | Group permissions need broader testing |
| Admin panel HTML and script bundle | Upstream implementation | Authenticated HTTP requests | PASS | Interactive admin browser controls unverified |
| Staff asset publishing | Upstream implementation | Upload PNG, buy through original economy API, inspect inventory and debit | PASS for PNG | RBXM hats, clothing, validation service and 3D render pipeline unverified |
| Admin limited/off-sale settings | Upstream implementation | Update published item and read product back | PASS | Concurrent stock enforcement and all limited variants need tests |
| Non-staff admin API access | Upstream guard | Request as ordinary account | PASS: HTTP 403 | Broader authorization audit remains |
| Personal owner selector | New local helper | Existing-user validation, system-account rejection, no mutation in check-only mode | PASS for validation | Interactive launcher/restart sequence not separately exercised |
| Temporary test staff permissions | Test harness | Database check after tests | PASS: none retained | Personal owner remains unassigned until user selects their account |
| Local dashboard page navigation | Added links | HTTP response content | PASS | Browser clicks unverified |
| Backend rebuild | Yes | .NET build | PASS: 0 errors | 393 warnings, including vulnerable upstream dependencies |
| 2017 visual conversion | Planned | No | NOT COMPLETE | Dated references and page-by-page implementation required |
| Whole original website browser journey | Partial | No | UNVERIFIED | Full Opera GX click-through required |
| Public 24/7 deployment | Planned | No | NOT DEPLOYED | See docs/HOSTING.md and security gates |

### Evidence and failures resolved

- local/social-test-results.json records friend/group passes and the initial profile API failure. The API still held the previous cached profile immediately after the database update. The service restart cleared that cache; local/publishing-test-results.json and local/update-verification.json record the exact profile passing afterward.
- The first publishing test attempt stopped in the Python helper because struct was not imported. The helper was corrected; the subsequent actual PNG upload, purchase and product update all passed.
- local/verify-group-owner.py verified group ownership after restart.
- local/test-publishing.py adds only the required permissions to a generated test account and removes them in finally. A separate check confirmed zero retained user_permission rows.
- The test group and uploaded PNG fixture remain in the local database. The later group and item purchases changed the verification buyer balance, so the earlier 9,475 balance is historical evidence, not the current expected balance.
- Two obsolete fixed-balance scripts were archived. local/verify-persisted.py now supports capture then verify against an actual recorded baseline, avoiding hardcoded balances. That new capture/verify workflow has not itself been run through another full restart.

No browser screenshots, complete 2017 appearance, 3D item readiness, public deployment, or multiplayer success are claimed by these API results.
