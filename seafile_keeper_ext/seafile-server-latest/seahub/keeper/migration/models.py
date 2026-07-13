"""
Django models for self-service email account migration in KEEPER.

Table lives in the 'keeper' database (via the existing DbRouter).
"""

from django.db import models
from django.utils import timezone


class EmailMigrationRequest(models.Model):
    """
    Represents a user-initiated move of all KEEPER data
    (libraries, shares, groups, etc.) from source_email to target_email.
    """

    STATUS_PENDING = 'pending'
    STATUS_IN_PROGRESS = 'in_progress'
    STATUS_COMPLETED = 'completed'
    STATUS_FAILED = 'failed'

    STATUS_CHOICES = [
        (STATUS_PENDING, 'Waiting to start'),
        (STATUS_IN_PROGRESS, 'Moving your files now'),
        (STATUS_COMPLETED, 'Done'),
        (STATUS_FAILED, 'Had a problem'),
    ]

    source_email = models.EmailField(db_index=True)
    target_email = models.EmailField(db_index=True)

    # Secure random token (store the raw value; shown to user only once).
    # 64 chars is sufficient for urlsafe token.
    migration_token = models.CharField(max_length=64, unique=True, db_index=True)

    token_expires_at = models.DateTimeField()

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
        db_index=True,
    )

    requested_at = models.DateTimeField(default=timezone.now)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    error_message = models.TextField(blank=True, null=True)

    # Flexible storage for captured shares, logs, timing info, etc.
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        # Explicit app_label: the DbRouter routes on app_label == 'keeper' to the
        # keeper-db. Without this, the label is only inherited implicitly from the
        # parent 'keeper' app (keeper.migration is not in INSTALLED_APPS) — and
        # registering 'keeper.migration' as its own app would silently flip the
        # label to 'migration' and break the DB routing. Pin it.
        app_label = 'keeper'
        db_table = 'keeper_email_migration'
        # NOTE: this table is created from raw SQL (keeper-db.sql /
        # create_keeper_email_migration_table.sql), not from a Django migration, so
        # the SQL DDL is authoritative for the actual schema. The indexes below are
        # documentation of the query patterns; the real indexes/keys are defined in
        # that DDL. There is intentionally NO unique constraint on
        # (source_email, target_email, status): MySQL/MariaDB cannot express the
        # desired "one ACTIVE move per pair" partial unique, and a full unique would
        # over-constrain terminal states. Active-duplicate prevention is done in the
        # app (see views._handle_generate_token).
        indexes = [
            models.Index(fields=['source_email', 'status']),
            models.Index(fields=['target_email', 'status']),
            models.Index(fields=['migration_token']),
        ]

    def __str__(self):
        return f"{self.source_email} → {self.target_email} ({self.status})"

    def mark_failed(self, error: str):
        """Used by the Django admin 'mark as failed' action."""
        self.status = self.STATUS_FAILED
        self.error_message = error[:2000]
        self.completed_at = timezone.now()
        self.save(update_fields=['status', 'error_message', 'completed_at'])