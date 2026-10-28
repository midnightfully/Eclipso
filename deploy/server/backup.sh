#!/usr/bin/env bash
# Nightly backup: database dump + uploaded assets/thumbnails/keys. Keeps 14 days. Run as root.
set -euo pipefail
ts=$(date +%Y%m%d-%H%M%S)
dir=/var/backups/eclipso
install -d -m 700 -o postgres -g postgres "$dir"
sudo -u postgres pg_dump -Fc -f "$dir/db-$ts.dump" eclipso
tar -czf "$dir/files-$ts.tgz" -C /var/lib/eclipso storage thumbnails groups
chmod 600 "$dir/files-$ts.tgz"
find "$dir" -name 'db-*.dump' -mtime +14 -delete
find "$dir" -name 'files-*.tgz' -mtime +14 -delete
echo "backup ok: $dir/db-$ts.dump"
