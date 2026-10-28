-- Database-level guarantees for the economy, independent of the cache (Garnet/Redis) purchase locks.
-- If a lock expires or the cache restarts mid-purchase, the losing transaction fails here and rolls back
-- (no charge, no item) instead of producing a duplicate serial or a negative balance.
-- Verified before applying: 0 duplicate serials, 0 negative balances.
CREATE UNIQUE INDEX IF NOT EXISTS user_asset_asset_serial_unique
    ON user_asset (asset_id, serial) WHERE serial IS NOT NULL;
CREATE INDEX IF NOT EXISTS user_asset_user_asset_idx ON user_asset (user_id, asset_id);
CREATE INDEX IF NOT EXISTS user_asset_asset_idx ON user_asset (asset_id);
ALTER TABLE user_economy  DROP CONSTRAINT IF EXISTS user_economy_balances_non_negative;
ALTER TABLE user_economy  ADD  CONSTRAINT user_economy_balances_non_negative  CHECK (balance_robux >= 0 AND balance_tickets >= 0);
ALTER TABLE group_economy DROP CONSTRAINT IF EXISTS group_economy_balances_non_negative;
ALTER TABLE group_economy ADD  CONSTRAINT group_economy_balances_non_negative CHECK (balance_robux >= 0 AND balance_tickets >= 0);
