# Roblox 2017 revival — start here

Project folder: C:\Users\gauth\Documents\Codex\2026-10-27\you-are-toker-you-re-toker\outputs\bubbablox-local

1. Double-click **Start Website.cmd** and wait for Ready.
2. In Opera GX press **Ctrl+L**, enter **http://127.0.0.1:5080/local**, then Enter. Do not include trailing asterisks.
3. Create your personal account. Use the local dashboard to test credits and purchases.
4. To administer the site, leave it running, double-click **Set Website Owner.cmd**, and enter that exact existing username. The launcher applies the setting and restarts the website. Sign in again, then open **http://127.0.0.1:5080/admin/**. This replaces the configured owner; it does not create an account or change its password.
5. User 1 is the automated **Roblox** profile with the supplied biography. Open **http://127.0.0.1:5080/users/1/profile**. Do not use the automated account as your personal admin login.
6. Double-click **Stop Website.cmd** before shutting down Windows. Use **Open Project Folder.cmd** to find the source in Explorer.

## Useful pages

- Local account/economy dashboard: http://127.0.0.1:5080/local
- Original home: http://127.0.0.1:5080/home
- Catalog: http://127.0.0.1:5080/catalog
- Create a group: http://127.0.0.1:5080/My/CreateGroup.aspx
- Your groups: http://127.0.0.1:5080/My/Groups.aspx
- Admin panel: http://127.0.0.1:5080/admin/

The source routes exist; HTTP/API verification and browser click verification are recorded separately in TEST-REPORT.md. The original frontend is still being converted to the 2017 baseline.

## Project documents

- docs/BUILD-PLAN-2017.md — feature gates, 2017 appearance, public release and later multiplayer.
- docs/HOSTING.md — domain, VPS, GitHub, DNS, HTTPS and backups.
- docs/DOWNLOADS-AND-LAYOUT.md — what was downloaded and where it lives.
- TEST-REPORT.md — confirmed results and remaining gaps.
- README-LOCAL.md — local startup and troubleshooting.

The current website is a local development environment. The hosting document lists the specific work remaining before public deployment.
