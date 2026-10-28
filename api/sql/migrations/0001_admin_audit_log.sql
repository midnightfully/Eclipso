-- Central audit trail for every administrative change attempt (and denied admin requests).
-- Written by Roblox.Website/Filters/AdminAuditFilter.cs; read via /admin-api/api/logs?logType=audit.
CREATE TABLE IF NOT EXISTS admin_audit_log (
    id            bigserial PRIMARY KEY,
    created_at    timestamptz NOT NULL DEFAULT now(),
    actor_user_id bigint NULL REFERENCES "user"(id),
    method        text NOT NULL,
    path          text NOT NULL,
    action        text NOT NULL,
    parameters    jsonb NULL,
    status_code   integer NOT NULL,
    outcome       text NOT NULL
);
CREATE INDEX IF NOT EXISTS admin_audit_log_created_at_idx ON admin_audit_log (created_at DESC);
CREATE INDEX IF NOT EXISTS admin_audit_log_actor_idx ON admin_audit_log (actor_user_id, created_at DESC);
