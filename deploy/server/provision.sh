#!/usr/bin/env bash
# One-time (re-runnable) server setup for Eclipso on Ubuntu 24.04. Run as root:  sudo bash provision.sh
# Installs only Ubuntu archive packages; PostgreSQL and Redis listen on localhost only.
set -euo pipefail
export DEBIAN_FRONTEND=noninteractive

apt-get update -q
apt-get install -y -q aspnetcore-runtime-10.0 nodejs npm postgresql-16 redis-server python3 >/dev/null

# Service account (created earlier by hand; ensure it exists). No shell, no login.
id eclipso >/dev/null 2>&1 || adduser --system --group --home /srv/eclipso --shell /usr/sbin/nologin eclipso

install -d -m 755 -o root -g root /opt/eclipso /opt/eclipso/releases
install -d -m 750 -o root -g eclipso /etc/eclipso
install -d -m 750 -o eclipso -g eclipso /var/lib/eclipso /var/lib/eclipso/storage /var/lib/eclipso/storage/asset \
    /var/lib/eclipso/thumbnails /var/lib/eclipso/groups /var/lib/eclipso/chat
install -d -m 700 -o postgres -g postgres /var/backups/eclipso

# Redis: localhost only, no persistence needed for sessions (PostgreSQL is authoritative), but keep defaults.
sed -i 's/^#\?\s*bind .*/bind 127.0.0.1 -::1/' /etc/redis/redis.conf
sed -i 's/^#\?\s*protected-mode .*/protected-mode yes/' /etc/redis/redis.conf
systemctl enable --now redis-server >/dev/null
systemctl restart redis-server

# PostgreSQL: localhost only (Ubuntu default). Application role + database; password generated here, never leaves.
if [ ! -f /etc/eclipso/db-password ]; then
  umask 077; head -c 32 /dev/urandom | base64 | tr -d '/+=' | head -c 40 > /etc/eclipso/db-password
  chown root:eclipso /etc/eclipso/db-password; chmod 640 /etc/eclipso/db-password
fi
DBPW=$(cat /etc/eclipso/db-password)
sudo -u postgres psql -q -v ON_ERROR_STOP=1 <<SQL
DO \$\$ BEGIN
  IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'eclipso') THEN
    CREATE ROLE eclipso LOGIN PASSWORD '${DBPW}';
  ELSE
    ALTER ROLE eclipso PASSWORD '${DBPW}';
  END IF;
END \$\$;
SQL
sudo -u postgres psql -tAc "SELECT 1 FROM pg_database WHERE datname='eclipso'" | grep -q 1 || sudo -u postgres createdb -O eclipso eclipso

install -m 644 "$(dirname "$0")/eclipso-website.service" /etc/systemd/system/eclipso-website.service
install -m 644 "$(dirname "$0")/eclipso-frontend.service" /etc/systemd/system/eclipso-frontend.service
install -m 644 "$(dirname "$0")/eclipso-backup.service" /etc/systemd/system/eclipso-backup.service
install -m 644 "$(dirname "$0")/eclipso-backup.timer" /etc/systemd/system/eclipso-backup.timer
install -m 755 "$(dirname "$0")/backup.sh" /usr/local/sbin/eclipso-backup
systemctl daemon-reload
systemctl enable eclipso-website eclipso-frontend eclipso-backup.timer >/dev/null
systemctl start eclipso-backup.timer
echo "provision: OK"
