# Changes — 2026-10-27

- Backed up the database, renamed account 1 from LocalCatalog to Roblox, and set the exact supplied biography. Verified the public profile after restart.
- Updated local fixture seeding to require and reuse Roblox user 1; it no longer creates a new LocalCatalog account after the rename.
- Removed user 1 from the configured site-owner role. Added Set Website Owner.cmd and a local account-selection helper for choosing an existing personal account.
- Added direct home, system-profile, catalog, group and admin links to the local dashboard.
- Tested friendship transitions, group creation/public joining, persisted group ownership, admin HTML/bundle access, PNG publishing, real purchase/inventory, limited/off-sale product settings, and non-staff rejection.
- Retained initial failed test evidence and documented the successful follow-up checks. Removed temporary staff grants after testing.
- Added START-HERE.md, the 2017 build plan, hosting steps, download inventory and expanded feature test report.
- Archived thirteen historical setup/debug/test scripts. Replaced a fixed-balance persistence helper with capture/verify semantics.
- Removed pre-existing merge conflict markers from .gitignore and ignored generated Python caches and uploaded public media.

The 2017 visual overhaul, complete browser coverage, vulnerability remediation, real 3D asset pipeline, public deployment and game clients remain separate unfinished milestones in the build plan.
