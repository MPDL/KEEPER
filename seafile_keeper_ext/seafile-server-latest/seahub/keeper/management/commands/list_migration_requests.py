"""
Django management command: python manage.py list_migration_requests

Lists waiting/in-progress self-service data moves.
Useful for admins to monitor without going through the full admin UI.

Run from the seahub context (with KEEPER settings).
"""

from django.core.management.base import BaseCommand
from keeper.migration.models import EmailMigrationRequest


class Command(BaseCommand):
    help = "List self-service KEEPER data moves (waiting, in progress, etc.)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--status",
            default="pending,in_progress",
            help="Comma-separated statuses to filter (default: pending,in_progress)",
        )

    def handle(self, *args, **options):
        statuses = [s.strip() for s in options["status"].split(",")]
        qs = EmailMigrationRequest.objects.filter(status__in=statuses).order_by("-requested_at")

        if not qs:
            self.stdout.write("No matching data moves.")
            return

        self.stdout.write(f"Found {qs.count()} move(s):\n")
        for req in qs:
            self.stdout.write(
                f"  #{req.id} | {req.source_email} → {req.target_email} | "
                f"{req.status} | started {req.requested_at:%Y-%m-%d %H:%M}"
            )
            if req.token_expires_at:
                self.stdout.write(f"    Code expires: {req.token_expires_at:%Y-%m-%d %H:%M}")
            if req.error_message:
                self.stdout.write(f"    Error: {req.error_message[:100]}...")
            if options.get('verbosity', 1) > 1:
                self.stdout.write(f"    Confirmed: {req.confirmed_at or 'N/A'}")