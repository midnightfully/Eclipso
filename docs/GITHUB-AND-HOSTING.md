# Eclipso: GitHub and public hosting

Updated 27 October 2026. Domain: **eclipso.lol**, purchased by kindmops at Spaceship. No hosting purchase, GitHub push or public deployment has been performed from this session.

## What to buy next

The remaining infrastructure purchase is a VPS, a computer hosted in a datacenter that stays on while your PC is off. The domain is the address; GitHub holds source code; the VPS runs the website, database and background services.

Candidate plans from [OVHcloud France](https://www.ovhcloud.com/fr/vps/), checked 27 October 2026:

| Plan | Resources | Advertised starting monthly price |
|---|---|---|
| VPS-1 | 2 vCores, 4 GB RAM, 40 GB NVMe | €3.81 excluding VAT / €4.57 including French VAT |
| VPS-2 | 4 vCores, 8 GB RAM, 75 GB NVMe | €7.21 excluding VAT / €8.65 including French VAT |

VPS-2 is the proposed website staging target for additional memory headroom; it is not a measured concurrent-user capacity guarantee. These are starting offers; select country, location and billing term in checkout and read the total and renewal terms. No game-worker budget is included.

**Wait to order the VPS until the deployment compatibility gate is passed.** The current working installation is Windows-based. The source still has Windows image-processing and path dependencies, and Linux deployment has not passed a clean-machine test. A Linux Ubuntu x86-64 VPS is the cost target, not an already verified deployment platform. Windows VPS licensing has different pricing.

No additional domain, site builder, shared PHP hosting or paid TLS certificate is needed. TLS can be provided by [Caddy automatic HTTPS](https://caddyserver.com/docs/automatic-https). Off-server backup storage and recovery email delivery must be budgeted when the deployment design is finalized.

## What kindmops can do now

1. Keep eclipso.lol in Spaceship. Confirm the registration email, enable account two-factor authentication, and check its renewal date and price. Do not change DNS to 127.0.0.1.
2. Create or sign into your GitHub account and enable two-factor authentication.
3. Open [the upstream repository](https://github.com/harryzawg/bubbablox-v2), click **Fork**, choose your account and a repository name such as **eclipso**. Our current base is branch **2021**; include that branch rather than assuming the default branch is the same. GitHub's [fork instructions](https://docs.github.com/en/pull-requests/how-tos/work-with-forks/fork-a-repo) explain the branch option. This creates the upstream copy; the modified local project still needs a reviewed commit and push.
4. Install/connect the GitHub integration offered in Codex and authorize **only the Eclipso repository**. If using Codex cloud tasks, also select the repository in its cloud environment setup. A GitHub connector being connected does not by itself prove local Git push authentication is configured. Use browser-based GitHub authentication when prompted; do not paste passwords or tokens into chat.
5. Supply the resulting repository URL in this chat. That identifies the push destination. We will preserve the existing upstream remote, add your fork and push the reviewed project changes. Keep database files, runtime secrets, account credentials and signing keys out of commits. The current checkout is sparse and contains upstream binaries/history, so do not drag the entire working folder into GitHub's upload box.
6. Configure Claude Code against the same repository and choose Opus 5.5 in Claude. For repository automation, run **/install-github-app** from Claude Code and review its workflow pull request. The [official setup guide](https://code.claude.com/docs/en/github-actions) describes installing its GitHub App and storing authentication as a GitHub secret. Restrict the app to Eclipso. Any API usage is billed separately from hosting.
7. Keep yourself as owner and add no other human collaborators. Use **codex/** and **claude/** branches, pull requests and passing checks. One developer implements, the other reviews; you retain release control. Public source does not give visitors write access. Only authorized owner/member requests should trigger privileged AI jobs.

The upstream root LICENSE is AGPL-3.0. Preserve its license and notices and plan to provide the corresponding modified source to network users. Publicly visible source and having only two authorized developers are compatible. The local LICENSE is the exact license text for this checkout.

## Files prepared for the two developers

- AGENTS.md: shared architecture, historical baseline, test and release rules.
- CLAUDE.md: Claude's entry point to those shared rules.
- .github/workflows/website-build.yml: read-only CI permissions, backend and frontend build jobs on pushes/PRs. No deployment credentials or automatic release.
- scripts/prepare-ci.cjs: creates temporary frontend build configuration on a clean checkout, refusing to overwrite existing configuration.
- docs/BUILD-PLAN-2017.md: feature completion gates and current production blockers.
- TEST-REPORT.md: verified behavior and missing tests.

The GitHub workflow has not run on GitHub yet. Build-only checks do not establish that accounts, purchases, limiteds or permission boundaries work. Integration tests must be added to an isolated CI database after the clean-machine bootstrap is reproducible.

## Hosting order after compatibility is confirmed

1. Create/sign into an OVHcloud account and choose VPS-2 from the France price page if that offer fits the final requirements.
2. Select an EU region, x86-64 Linux and the Ubuntu LTS release used by our tested deployment. Avoid a long commitment until staging is proven.
3. Add the SSH public key prepared for your administrator account. Review recurring total, tax and any options before you pay.
4. Record the public IPv4 address from the VPS dashboard. Keep root credentials and private keys out of the repository and chat.
5. Deploy a production-built backend/frontend with private PostgreSQL and cache, a reverse proxy, HTTPS, restart policies and off-server backups. The local next-dev launcher is not the deployment system.
6. Start on staging.eclipso.lol, complete external tests and a backup restore, then switch the public domain to the tested release.

## Spaceship DNS, once the server is ready

In Spaceship's Launchpad open **Advanced DNS**, select **eclipso.lol**, and use these records if Spaceship remains the authoritative DNS provider:

| Type | Host | Value |
|---|---|---|
| A | @ | VPS public IPv4 from its dashboard |
| CNAME | www | eclipso.lol |
| A | staging | VPS public IPv4, or a separate staging server's IP |

Remove conflicting parking records for those same hosts after reading the existing DNS entries. Preserve unrelated mail and verification records. Do not add an AAAA record until IPv6 has been configured and tested. If nameservers point elsewhere, edit DNS with that authoritative provider instead. [Spaceship DNS tools](https://www.spaceship.com/domain-management/) and [DNS record reference](https://www.spaceship.com/knowledgebase/dns-records-types/) describe the controls.

Configure the reverse proxy for eclipso.lol and www.eclipso.lol, choose one canonical hostname, and request certificates after DNS resolves. The browser connects over HTTPS; PostgreSQL/cache stay private. No home router port forwarding is needed.

## Why public launch is still blocked

The upstream README explicitly reports a known remote-code-execution problem. That specific report has not been located and fixed yet. The local backend build also emits known dependency vulnerability warnings. The current LocalDevelopment flag bundles development grants, external registration checks and game/render service startup, so simply setting it to false is not a production configuration.

Remaining release requirements include dependency and endpoint repairs, Linux compatibility, reproducible deployment/migrations, HTTPS sessions, account recovery, upload isolation, concurrent economy tests, backup restore, and page-by-page browser acceptance. The 2017 visual conversion currently starts with signup/login; the entire original website has not been converted.

## Later: clients and multiplayer

Keep client source and release manifests in GitHub. Build versioned release artifacts, verify their integrity, test updates on staging, and publish releases. The website host stores accounts and issues launch tickets; separate isolated game workers run sessions. This stage starts after the website acceptance gate. No runnable multiplayer deployment is presently installed.
