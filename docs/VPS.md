# Eclipso VPS (Hostinger KVM 2)

Recorded 2026-10-28. Ubuntu 24.04.5 LTS, 2 vCPU, 7.8 GB RAM, 96 GB disk, France.

| Item | Value |
|---|---|
| IPv4 | 2.24.48.245 |
| SSH host key (ED25519) | `SHA256:HsiwLz0keNop8a5EXgBWrDr6h4A0m2PyecoQKrgSZ+I` (if SSH ever warns this changed, stop and investigate) |
| Admin login | `ssh kindmops@2.24.48.245` with key `%USERPROFILE%\.ssh\eclipso_vps` (passphrase-protected; unlock with `ssh-add`) |
| Emergency access | Hostinger dashboard → VPS → browser terminal |
| Service account | `eclipso` (system user, no shell, home `/srv/eclipso`, mode 750) for the future website |

## Hardening applied

- SSH: keys only (`/etc/ssh/sshd_config.d/00-eclipso-hardening.conf`): no passwords, root by key only, MaxAuthTries 4. Verified: password login refused, key login works.
- `kindmops` admin user, passwordless sudo (the account has no password; access is by key only).
- UFW firewall: deny incoming except 22, 80, 443.
- All packages upgraded; `unattended-upgrades` enabled for automatic security updates.
- fail2ban: 1-hour ban after 5 failed SSH logins.
- Hostinger's `monarx-agent` malware scanner was pre-installed and left running.

## Placeholder landing page

- Source: `deploy/landing/` (static HTML, no forms or backend). Served from `/var/www/eclipso-landing` by Caddy 2.11.7 (`deploy/caddy/Caddyfile.landing` = live `/etc/caddy/Caddyfile`).
- Update it (from the project folder, Git Bash):
  `tar -cf - -C deploy/landing . | ssh kindmops@2.24.48.245 'sudo tar -xf - -C /var/www/eclipso-landing --no-same-owner && sudo chmod -R a+rX /var/www/eclipso-landing'`
- Roll back: check out the previous commit of `deploy/landing` and run the same command.
- Live since 2026-10-28: https://eclipso.lol (canonical), https://staging.eclipso.lol (noindex), www and http redirect to https://eclipso.lol. Let's Encrypt certificates, renewed automatically by Caddy.
- Previous IP-only config kept on the server as `/etc/caddy/Caddyfile.bak-ip-only`.
- Change the Caddy config: edit `deploy/caddy/Caddyfile.landing`, then
  `ssh kindmops@2.24.48.245 'sudo cp /etc/caddy/Caddyfile /etc/caddy/Caddyfile.bak && sudo tee /etc/caddy/Caddyfile >/dev/null && sudo caddy validate --config /etc/caddy/Caddyfile && sudo systemctl reload caddy' < deploy/caddy/Caddyfile.landing`

## DNS (Spaceship, authoritative: launch1/launch2.spaceship.net)

A records `@`, `www`, `staging` → 2.24.48.245. The previous parking A records (34.216.117.25, 54.149.79.189) were removed. No MX/TXT records existed.

The full website (backend, database) is NOT deployed. See docs/BUILD-PLAN-2017.md for the security gates.
