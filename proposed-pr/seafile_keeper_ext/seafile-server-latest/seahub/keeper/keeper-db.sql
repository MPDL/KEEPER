-- keeper-db.sql
--
-- Custom tables for the 'keeper' database used by the KEEPER extension.
-- This database is separate from the main seahub-db and is accessed via
-- the DbRouter defined in keeper/dbrouter.py.
--
-- This file is part of the KEEPER application deployment.
-- When contributing schema changes, add the CREATE TABLE statements here.

-- Existing tables would be above this line in the full file.
-- The section below was added for the self-service email migration feature.

-- Self-service email migration table.
-- Used by the move screen (/account/migrate/) and the
-- worker process_keeper_email_migrations.py (deployed to /opt/seafile/scripts/migration/).
-- Users are guided in emails and on screen to always check the identity banner for SOURCE vs TARGET.

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

    -- Prevent multiple active requests for the same (source, target) pair
    UNIQUE KEY uniq_active_pair (source_email, target_email, status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
  COMMENT='Self-service email migration requests (user-triggered source->target). Processed by the worker in /opt/seafile/scripts/migration/';

-- End of email migration schema addition.