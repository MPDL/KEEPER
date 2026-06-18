-- Table for self-service KEEPER email account moves.
-- This table lives in the `keeper-db` database (not seahub-db).
-- Run this on the keeper database (usually via the automation host or DB admin).
-- Emails and screens guide users to check the top identity banner for the correct SOURCE or TARGET account.
--
-- Idempotent: safe to run repeatedly (CREATE TABLE IF NOT EXISTS + harmless COMMENT ALTER).

CREATE TABLE IF NOT EXISTS keeper_email_migration (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    source_email VARCHAR(255) NOT NULL,
    target_email VARCHAR(255) NOT NULL,
    migration_token CHAR(64) NOT NULL,
    token_expires_at DATETIME NOT NULL,
    status ENUM('pending', 'in_progress', 'completed', 'failed') NOT NULL DEFAULT 'pending',
    requested_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    confirmed_at DATETIME NULL,
    completed_at DATETIME NULL,
    error_message TEXT NULL,
    metadata JSON NULL,

    UNIQUE KEY uniq_token (migration_token),
    KEY idx_source_status (source_email, status),
    KEY idx_target_status (target_email, status),
    KEY idx_status_requested (status, requested_at)
    -- NOTE: intentionally NO full UNIQUE(source_email,target_email,status). It would
    -- over-constrain terminal states (blocking re-migrating a pair, or a second
    -- completed/failed row), and MySQL/MariaDB cannot express the intended "one ACTIVE
    -- move per pair" partial unique. Active-duplicate prevention is done in the app.
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Drop the legacy full unique on (source,target,status) if a previous deploy created it
-- (idempotent; safe when absent). It over-constrained terminal states.
ALTER TABLE keeper_email_migration DROP INDEX IF EXISTS uniq_active_pair;

-- Set/refresh comment (idempotent operation; safe on re-runs)
ALTER TABLE keeper_email_migration COMMENT = 'Self-service email migration moves (source -> target). Processed by process_keeper_email_migrations.py. Users guided to verify SOURCE vs TARGET banner.';