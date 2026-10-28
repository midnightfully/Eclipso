# Database migrations

`api/sql/schema.sql` is the upstream base schema. Every change after it is a numbered file here
(`NNNN_description.sql`), applied once, in order, and recorded in the `schema_migrations` table.

Rules:
- Never edit a migration that has been applied anywhere; add a new one.
- Migrations must preserve existing accounts, balances, inventories and published content
  (additive changes; backfill in the same file when needed).
- Take a backup first. Locally: `python local/migrate.py` backs up automatically, then applies pending files.
- Rollback: application rollback does not undo a migration. Additive migrations (new tables/columns)
  are compatible with the previous application version. A destructive migration must ship with a
  written restore plan and is restored from the pre-migration backup.
