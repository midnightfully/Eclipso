# Downloads and project layout

The project is at:

C:\Users\gauth\Documents\Codex\2026-10-27\you-are-toker-you-re-toker\outputs\bubbablox-local

Double-click Open Project Folder.cmd here to open that folder in Windows Explorer. Keep the folder at this path for now because several configuration values are absolute paths.

## What was obtained

- Public source from https://github.com/harryzawg/bubbablox-v2, branch 2021, shallow/sparse checkout at commit 6e355d803dd332797ae714b65e72f71c5bd08c2e.
- Checked-out source: Roblox/ (.NET services and API), 2016-roblox-main/ (Next frontend), admin/ (Svelte admin source plus its checked-in bundle), api/sql/ and api/public/. Root upstream files are also present.
- Portable PostgreSQL 16.15 under .local/runtime/postgres/.
- Garnet 2.2.4 under .local/runtime/garnet/, used as the working Redis-compatible cache.
- Two Redis attempts under .local/runtime/redis/ and redis-modern/. Neither is started by the current launcher; they were retained as setup artifacts after compatibility failures.
- npm dependencies in 2016-roblox-main/node_modules/; NuGet packages/build artifacts in .local/nuget/ and Roblox project bin/obj folders.
- Local test scripts, a test dashboard, generated private configuration and database state. Existing installed Python, Node, Git and .NET tools are used by the launchers.

No GitHub account connection was needed for the public clone. No fork, remote push, domain purchase, hosting purchase or public deployment was performed. The checkout is a selected subset, not an assembled full client/RCC/game-server distribution. Nothing from the old MM2 hub was used to implement this website.

## Where things belong

| Path | Purpose |
|---|---|
| Start Website.cmd / Stop Website.cmd | Normal local launch and shutdown |
| Set Website Owner.cmd | Assign an existing personal account as site owner and restart |
| Open Project Folder.cmd | Open this project in Explorer |
| START-HERE.md / README-LOCAL.md | Getting started and troubleshooting |
| docs/ | Build plan, hosting plan, exact Roblox profile fixture and this inventory |
| Roblox/ | Backend source |
| 2016-roblox-main/ | Existing frontend source; folder name does not certify period accuracy |
| admin/ | Admin source and compiled assets |
| local/ | Supervisor, build helpers, API tests and machine-readable test results |
| local/archive/ | Historical setup/debug scripts; not normal launchers |
| .local/pgdata-ready/ | Live database containing accounts and economy |
| .local/storage/ | Assets and signing/encryption keys |
| .local/backups/ | Database backup before the system-profile change; owner-setting history |
| .local/*.log | Service and build logs |
| .git/ | Local source history and upstream metadata |

Thirteen historical setup/debug/test files were moved into local/archive/ during this pass. No account, asset, live database, runtime executable or source directory was deleted or relocated.

## GitHub workflow

Keep testing locally now. When you want remote source history, connect GitHub or authenticate Git on this PC and choose your destination repository. A fork retains the upstream relationship and will be public when forked from this public repository. A separate repository is another organizational option. Review the upstream license and source before selecting the distribution arrangement; a clone is not a license grant beyond the supplied terms.

Before the first push, review the staged file list and exclude all generated configuration, .local/, user data, passwords, keys and logs. Preserve the existing local changes when changing remotes. The build plan calls for clean installation and migration scripts so a future server can reproduce this environment without uploading private runtime state.
