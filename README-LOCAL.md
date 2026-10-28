# Bubbablox local website

## Open it in Opera GX

1. Double-click **Start Website.cmd** in this folder.
2. Wait for the message **Ready: open http://127.0.0.1:5080/local in Opera GX**.
3. Open Opera GX, press **Ctrl+L**, paste **http://127.0.0.1:5080/local**, and press Enter. Use HTTP, not HTTPS.
4. Create an account with a new username and a password of at least eight characters.
5. Click **Add 10,000 test robux**, then buy a catalog item or choose **View resellers** for a limited.
6. Click **Open original website** to use the original Bubbablox frontend. The local dashboard and original website share the same login and database.

The first startup or first visit to a frontend page can take a few minutes. Keep the project folder in its current location; the local configuration contains absolute storage paths.

## What you can test

- Account creation, sign-in, and sign-out.
- Persistent test-robux balances and a fixed 10,000-credit grant, capped at 1,000,000.
- Catalog purchases, inventory, and transaction records.
- A limited-unique crown with three copies and assigned serial numbers. One copy was used by the verification account, leaving two initial-sale copies.
- Limited resale. Once an item is off sale, set a resale price in your inventory. Zero removes the listing. Sign in as another account to buy it.
- Original home and catalog pages through the same backend.

Test credits are local database values. Sample items are economy fixtures, not implemented wearable 3D assets. Avatar rendering, clients, and multiplayer are not running yet.

The database includes a reserved **Roblox** account (ID 1) and two generated verification accounts. Create your own account from the dashboard. Those verification accounts are not needed for normal use. The grant log is separate from original purchase transactions, so local credit grants do not masquerade as item sales.

## Stop and restart

Double-click **Stop Website.cmd**. It asks the supervisor to stop the web services and save/shut down PostgreSQL. Wait for the stopped message before shutting down Windows. Restart with **Start Website.cmd**. Accounts, balances, inventory, and the signing key remain on disk. The cache is temporary and recreated on startup.

## Files and troubleshooting

- Local database: **.local/pgdata-ready**. Do not delete it; it contains your accounts and economy.
- Storage and encryption keys: **.local/storage**.
- Configuration: **Roblox/Roblox.Website/appsettings.json**. Keep this private; it contains local database and signing secrets.
- Startup status: **.local/status.json**.
- Logs: **.local/website.log**, **frontend.log**, **postgres.log**, **cache.log**, and **supervisor.log**.
- Source changes and launch code: **local/** and the original source folders.

If Opera GX cannot connect, run the start script and wait for Ready. Check the status file if it reports an error. A message that a port is in use means another process already occupies one of the configured ports; do not run multiple copies. The four listeners are 5080 (website), 3000 (frontend), 15432 (PostgreSQL), and 16379 (Garnet cache), all bound to 127.0.0.1.

Do not use the upstream **runall.bat**; it contains unrelated game-service commands and paths from the original developer's machine.

## Verification

See **TEST-REPORT.md** for completed checks and limitations. This local setup is based on the archived upstream repository and is not a deployment-ready public server.

## Admin and next steps

See START-HERE.md for the new Set Website Owner.cmd launcher and admin URL. The exact user-1 biography is stored in docs/roblox-profile.json. See docs/BUILD-PLAN-2017.md and docs/HOSTING.md for the phased 2017 revival and public-hosting plan.
