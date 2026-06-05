-- Table for self-service KEEPER email account moves.
-- This table lives in the `keeper-db` database (not seahub-db).
-- Run this on the keeper database (usually via the automation host or DB admin).
-- Emails and screens guide users to check the top identity banner for the correct SOURCE or TARGET account.

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
    KEY idx_status_requested (status, requested_at),

    -- Prevent multiple active moves for the same (source, target) pair
    UNIQUE KEY uniq_active_pair (source_email, target_email, status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Optional: add a comment
ALTER TABLE keeper_email_migration COMMENT = 'Self-service email migration moves (source -> target). Processed by process_keeper_email_migrations.py. Users guided to verify SOURCE vs TARGET banner.';