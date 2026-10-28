#!/usr/bin/env bash
# Activate an uploaded release (run as root):  activate-release.sh /opt/eclipso/releases/<rev> https://staging.eclipso.lol
# Backs up the database, applies pending migrations, switches /opt/eclipso/current, restarts, health-checks, and
# rolls back to the previous release automatically if the new one does not come up.
set -euo pipefail
REL=$1; SITE=$2
[ -d "$REL/website" ] || { echo "no release at $REL"; exit 1; }
PREV=""; [ -L /opt/eclipso/current ] && PREV=$(readlink -f /opt/eclipso/current)
psqlq() { sudo -u postgres psql -d eclipso -v ON_ERROR_STOP=1 -qAt "$@"; }

# 1. Database: backup, base schema on first deploy, then numbered migrations (each in one transaction).
/usr/local/sbin/eclipso-backup >/dev/null
if [ "$(psqlq -c "SELECT to_regclass('public.\"user\"') IS NOT NULL")" != "t" ]; then
  echo "empty database: loading base schema"
  # PostgreSQL 16 does not know transaction_timeout (a PG17 setting in the upstream dump).
  grep -v '^SET transaction_timeout' "$REL/sql/schema.sql" | sudo -u postgres psql -d eclipso -v ON_ERROR_STOP=1 -q >/dev/null
fi
psqlq -c "CREATE TABLE IF NOT EXISTS schema_migrations (version text PRIMARY KEY, applied_at timestamptz NOT NULL DEFAULT now())"
for f in "$REL"/sql/migrations/[0-9][0-9][0-9][0-9]_*.sql; do
  v=$(basename "$f" .sql)
  if [ -z "$(psqlq -c "SELECT 1 FROM schema_migrations WHERE version='$v'")" ]; then
    echo "applying migration $v"
    sudo -u postgres psql -d eclipso -v ON_ERROR_STOP=1 -q -1 -f "$f" -c "INSERT INTO schema_migrations(version) VALUES ('$v')" >/dev/null
  fi
done
# The application role owns and can use everything in the schema.
psqlq -c "GRANT ALL ON ALL TABLES IN SCHEMA public TO eclipso; GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO eclipso; ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO eclipso; ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO eclipso;"

# 2. Frontend runtime dependencies (exact versions from the lockfile) and config.
(cd "$REL/frontend" && npm ci --omit=dev --no-audit --no-fund --loglevel=error >/dev/null)
python3 "$REL/deploy/make-config.py" --release "$REL" --site "$SITE"
chown -R root:root "$REL"; chmod -R a+rX "$REL"

# 3. Switch and restart.
ln -sfn "$REL" /opt/eclipso/current.new && mv -T /opt/eclipso/current.new /opt/eclipso/current
systemctl restart eclipso-frontend eclipso-website

# 4. Health check; roll back on failure.
ok=0
for i in $(seq 1 90); do
  if curl -fsS -o /dev/null -A "EclipsoHealthCheck/1.0" -H "Host: ${SITE#*://}" http://127.0.0.1:5080/login && curl -fsS -o /dev/null http://127.0.0.1:3000/login; then ok=1; break; fi
  sleep 2
done
if [ $ok -ne 1 ]; then
  echo "HEALTH CHECK FAILED"; journalctl -u eclipso-website -n 30 --no-pager | tail -30
  if [ -n "$PREV" ] && [ -d "$PREV" ]; then
    ln -sfn "$PREV" /opt/eclipso/current.new && mv -T /opt/eclipso/current.new /opt/eclipso/current
    systemctl restart eclipso-frontend eclipso-website; echo "rolled back to $PREV"
  fi
  exit 1
fi
basename "$REL" > /opt/eclipso/DEPLOYED
echo "activated $(basename "$REL")"
