-- Login sessions were stored only in the in-memory cache (Garnet/Redis) with no expiry: every restart logged
-- everyone out, and a stolen session never expired. PostgreSQL is now the authoritative session store;
-- the cache is a TTL-bounded copy.
CREATE TABLE IF NOT EXISTS user_web_session (
    id          text PRIMARY KEY,
    user_id     bigint NOT NULL REFERENCES "user"(id),
    created_at  timestamptz NOT NULL DEFAULT now(),
    expires_at  timestamptz NOT NULL,
    revoked_at  timestamptz NULL
);
CREATE INDEX IF NOT EXISTS user_web_session_user_idx ON user_web_session (user_id);
CREATE INDEX IF NOT EXISTS user_web_session_expires_idx ON user_web_session (expires_at);
