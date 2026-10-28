# Running the revival online

A domain is the address visitors type. Hosting is the server that runs your application while your PC is switched off. GitHub stores source and can automate deployment; it does not replace the .NET server, Node frontend, database, cache and persistent uploads.

## Steps in order

1. Finish the website and public-release gates in BUILD-PLAN-2017.md. Keep the current environment local while those gates are open.
2. Choose a revival name and optionally register its domain now. A domain alone does not start the website. Check first-year price, renewal price and account recovery/2FA at the registrar. No domain or hosting was purchased in this task.
3. Create your own GitHub repository or fork for source history and backup. Connecting GitHub is not needed to run locally. Authentication is needed if you want Codex to create/push a repository under your account. No fork or push has been made. Public upstream forks are public: [GitHub fork visibility](https://docs.github.com/en/pull-requests/reference/forks).
4. Choose a VPS after an OS compatibility test and a small load test. For planning only, test a web-only staging candidate around 2 vCPU/4 GB RAM, then size from measurements. That is not a promised capacity. Compare server, disk, backup, traffic and any Windows license costs. [Hetzner Cloud](https://www.hetzner.com/cloud/) is one Linux-hosting candidate; the current Windows build must be ported and tested before using it.
5. Deploy a clean production build plus production configuration. Run PostgreSQL, the chosen compatible cache, backend, frontend and proxy as services that start after a reboot. Copy a consistent database backup and asset files. Do not copy the whole local dependency/debug folder to a public web root.
6. Point the domain's A record to the server IPv4 address. Add an AAAA record only if IPv6 is configured and tested. Point www to the canonical host. The hosting provider supplies the IP; the registrar/DNS provider hosts these records. [DNS record instructions](https://developers.cloudflare.com/dns/manage-dns-records/how-to/create-dns-records/).
7. Enable HTTPS through the reverse proxy, redirect HTTP to HTTPS, and configure canonical website/API/asset URLs. [Caddy](https://caddyserver.com/docs/automatic-https) can provision and renew certificates after the DNS and required ports are configured. Expose web ports only; do not expose the local development, database or cache ports.
8. Set up external uptime monitoring, service restart policies, log rotation and off-server backups. Verify a restore and a reboot. Test from another network and in Opera GX while your development PC is off.
9. Start an invited website beta, fix the recorded issues, then open signups. Clients and multiplayer come afterward on separate workers.

## Architecture

Browser -> HTTPS reverse proxy -> .NET website/API -> PostgreSQL + cache + asset storage
                                      |
                                      +-> production Node frontend

Later: authenticated job/launch interfaces -> isolated render and game workers.

## Current launch blockers

- Upstream's explicit RCE warning has not been resolved here.
- Vulnerable dependencies remain in the build.
- Frontend currently runs next dev; browser flows and 2017 appearance are not fully verified.
- Local-only bypasses, grants and fixture routes must be excluded from production.
- Asset validation/rendering and account recovery need completion.
- Reproducible fresh deployment, load testing, monitoring and off-server restore remain to implement.

This document is a deployment plan, not a claim that a public server has already been provisioned.
