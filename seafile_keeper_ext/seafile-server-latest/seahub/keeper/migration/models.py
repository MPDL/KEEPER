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
        db_table = 'keeper_email_migration'
        # Prevent duplicate active requests for the same pair
        constraints = [
            models.UniqueConstraint(
                fields=['source_email', 'target_email', 'status'],
                name='uniq_active_migration_pair',
                condition=models.Q(status__in=[ 'pending', 'in_progress' ]),
            )
        ]
        indexes = [
            models.Index(fields=['source_email', 'status']),
            models.Index(fields=['target_email', 'status']),
            models.Index(fields=['migration_token']),
        ]

    def __str__(self):
        return f"{self.source_email} → {self.target_email} ({self.status})"

    @property
    def is_active(self):
        return self.status in (self.STATUS_PENDING, self.STATUS_IN_PROGRESS)

    @property
    def is_expired(self):
        return timezone.now() > self.token_expires_at and self.status == self.STATUS_PENDING

    def mark_in_progress(self):
        self.status = self.STATUS_IN_PROGRESS
        self.save(update_fields=['status'])

    def mark_completed(self):
        self.status = self.STATUS_COMPLETED
        self.completed_at = timezone.now()
        self.save(update_fields=['status', 'completed_at'])

    def mark_failed(self, error: str):
        self.status = self.STATUS_FAILED
        self.error_message = error[:2000]
        self.completed_at = timezone.now()
        self.save(update_fields=['status', 'error_message', 'completed_at'])

    @classmethod
    def get_active_for_user(cls, email):
        """Return active (pending or in_progress) move where user is source or target."""
        email = email.lower()
        return cls.objects.filter(
            models.Q(source_email=email) | models.Q(target_email=email),
            status__in=[cls.STATUS_PENDING, cls.STATUS_IN_PROGRESS]
        ).first()

    @classmethod
    def create_request(cls, source_email, target_email, token, expires_at):
        """Convenience creator (not currently used by views, which do direct create)."""
        return cls.objects.create(
            source_email=source_email.lower(),
            target_email=target_email.lower(),
            migration_token=token,
            token_expires_at=expires_at,
        )