"""
Django admin for EmailMigrationRequest.

This allows operators to monitor, search, and manually intervene
on self-service data moves from the KEEPER admin interface.
"""

from django.contrib import admin
from .models import EmailMigrationRequest


@admin.register(EmailMigrationRequest)
class EmailMigrationRequestAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "source_email",
        "target_email",
        "status",
        "requested_at",
        "confirmed_at",
        "completed_at",
    )
    list_filter = ("status", "requested_at")
    search_fields = ("source_email", "target_email", "migration_token")
    readonly_fields = (
        "requested_at",
        "confirmed_at",
        "completed_at",
        "migration_token",
        "token_expires_at",
    )
    ordering = ("-requested_at",)

    actions = ["mark_as_failed"]

    def mark_as_failed(self, request, queryset):
        marked = 0
        for obj in queryset.filter(status__in=["pending", "in_progress"]):
            obj.mark_failed("Manually marked failed by admin")
            marked += 1
        self.message_user(request, f"Marked {marked} move(s) as failed.")
    mark_as_failed.short_description = "Mark selected moves as failed"