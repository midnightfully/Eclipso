# Eclipso website feature matrix

Statuses: **Verified** (tested with evidence), **Implemented** (code present, not fully tested), **Failed**,
**Blocked** (needs a missing component), **Not Started**. "API" = automated HTTP + database checks;
"Browser" = clicked through in a real browser. Updated 2026-10-28; environment: local (127.0.0.1:5080).

| Feature | Frontend | Backend | Persistence | Browser test | Permission / negative test | Result | Blocker | Next action |
|---|---|---|---|---|---|---|---|---|
| Signup / login (API) | Implemented (2017 page) | Verified | Verified | Partial: page renders, form not submitted in browser | Verified: invalid input, duplicate case-insensitive names | Verified (API) | — | Browser submit test |
| Logout ends session | Implemented | Verified | — | Not Started | Verified: admin access ends after logout | Verified (API) | — | Browser test |
| Account recovery | Implemented (upstream Discord flow) | Not tested | — | Not Started | Not Started | Not Started | No recovery delivery configured | Decide recovery method (email provider) |
| Owner / admin selection | — | Verified (config + audit) | Verified (survives restart) | kindmops to test (Guide A) | Verified: user 1 refused | Verified | — | kindmops browser check |
| Admin page access control | Implemented | Verified | — | Not Started | Verified: anon/normal user redirect + API 403 | Verified (API) | — | Browser check |
| Admin API authorization | — | Verified (4 leaks fixed) | — | — | Verified: 6 endpoints incl. formerly unguarded | Verified | — | Full audit of remaining ~150 routes' permission choices |
| Role management | Implemented (Permissions page) | Verified owner-only | Verified | Not Started | Verified: staff cannot self-escalate | Verified (API) | — | Browser check |
| Admin audit trail | Implemented (Logs → All admin actions) | Verified | Verified | Not Started | Verified: denied attempts recorded | Verified (API) | — | Browser check |
| Publish Image item | Implemented (/admin/asset/create) | Verified | Verified | Not Started | Verified: non-image & oversized refused, nothing created | Verified (API) | — | Browser walkthrough (Guide B) |
| Publish wearable (hat, gear, clothing, face, package) | Implemented (upstream forms) | Implemented | — | Not Started | Not Started | **Blocked** | Renderer (RCC) + AssetValidationService not set up | Set up local renderer |
| Item thumbnails | Implemented | Verified for Image type | Verified | Not Started | — | Partial | Renderer for all other types | Renderer |
| Catalog search / item details | Implemented (upstream) | Verified (API) | — | Not Started | — | Verified (API) | — | Browser walkthrough |
| Price / sale / off-sale edit | Implemented (/admin/product/update, fixed) | Verified | Verified | Not Started | Verified: off-sale buy via direct API refused | Verified (API) | — | Browser walkthrough |
| Ordinary purchase | Implemented | Verified | Verified (restart) | Not Started | Verified: double buy, insufficient funds, stale price | Verified (API) | — | Browser walkthrough |
| Limited unique: stock & serials | Implemented | Verified | Verified (restart) | Not Started | Verified: 5 concurrent buyers / 3 copies; DB unique serial constraint | Verified (API) | — | Browser walkthrough (Guide C) |
| Resale listing & purchase | Implemented | Verified | Verified (restart) | Not Started | Verified: non-owner listing, stale price, double sale, old owner relist | Verified (API) | — | Browser walkthrough (Guide D) |
| Price history (RAP / sale log) | Implemented | Verified (from real sales) | Verified | Not Started | — | Verified (API) | — | Check chart in browser |
| Test currency grant | Implemented (/local dashboard, local only) | Verified | Verified | Not Started | Local-only (loopback) | Verified (local) | Must not exist in production | Separate production flag |
| Admin Robux adjustment | Implemented (upstream) | Not tested | — | Not Started | Not Started | Implemented | — | Test + audit check |
| Inventory view | Implemented (upstream) | Partial (DB checked) | Verified | Not Started | — | Implemented | — | Browser |
| Avatar equip / save / render | Implemented (upstream) | Not tested | — | Not Started | Not Started | **Blocked** | Renderer | Renderer |
| Friends | Implemented | Partly verified earlier (request/accept/remove) | Verified earlier | Not Started | Partial | Implemented | — | Decline/cancel/counts + browser |
| Groups | Implemented | Partly verified earlier (create/join) | Verified earlier | Not Started | Partial | Implemented | — | Roles, wall, funds, browser |
| Messages, trades, settings, forum | Implemented (upstream) | Not tested | — | Not Started | Not Started | Not Started | — | Audit + test |
| Public deployment of website | — | — | — | — | — | Not Started | Security gates (RCE, CSRF prefixes, local endpoints) + Linux port | After website gate |

Client-dependent (website preparation only; end-to-end acceptance happens in the client phases): Play button,
game servers, place publishing from Studio, in-game avatar loading.
