"""
Views for the self-service KEEPER email migration flow.

All pages must make it extremely obvious which account the user
is currently authenticated as (Source vs Target).
"""

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.core.mail import send_mail
from datetime import timedelta
import secrets

from .models import EmailMigrationRequest

# Defaults are built-in below (no changes needed in seahub_settings.py for basic use).
# We may expose these for configuration in seahub_settings.py later:
#   KEEPER_MIGRATION_CODE_LIFETIME_DAYS = 7
#   KEEPER_MIGRATION_PAGE_URL = 'https://keeper.mpdl.mpg.de/account/migrate/'
#   KEEPER_MIGRATION_SUPPORT_EMAIL = 'keeper@mpdl.mpg.de'
# (DEFAULT_FROM_EMAIL is the standard Django/KEEPER setting.)
try:
    from django.conf import settings as django_settings
    DEFAULT_FROM_EMAIL = getattr(django_settings, 'DEFAULT_FROM_EMAIL', 'keeper@mpdl.mpg.de')
    SUPPORT_EMAIL = getattr(django_settings, 'KEEPER_MIGRATION_SUPPORT_EMAIL',
                             getattr(django_settings, 'SUPPORT_EMAIL', 'keeper@mpdl.mpg.de'))
    MIGRATION_PAGE_URL = getattr(django_settings, 'KEEPER_MIGRATION_PAGE_URL',
                                 'https://keeper.mpdl.mpg.de/account/migrate/')
    TOKEN_LIFETIME_DAYS = getattr(django_settings, 'KEEPER_MIGRATION_CODE_LIFETIME_DAYS', 7)
except Exception:
    DEFAULT_FROM_EMAIL = 'keeper@mpdl.mpg.de'
    SUPPORT_EMAIL = 'keeper@mpdl.mpg.de'
    MIGRATION_PAGE_URL = 'https://keeper.mpdl.mpg.de/account/migrate/'
    TOKEN_LIFETIME_DAYS = 7

def send_migration_email(subject, message, recipient_list):
    """Send email using Django's mail system. Defaults are built in (see module-level settings block).
    We might expose KEEPER_MIGRATION_* keys in seahub_settings.py for configuration later (see integration notes)."""
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=DEFAULT_FROM_EMAIL,
            recipient_list=recipient_list,
            fail_silently=False,
        )
        return True
    except Exception as e:
        # Log error in production
        print(f"Email send failed: {e}")
        return False


def _get_current_user_email(request):
    """Return the best available email for the logged-in user.

    Prefers contact_email for SSO users, falls back to username/email.
    This mirrors logic used in the existing migration scripts.
    """
    user = request.user
    # Common patterns in Seafile/KEEPER
    contact_email = getattr(user, 'contact_email', None) or getattr(user, 'profile', None)
    if hasattr(contact_email, 'contact_email'):
        contact_email = contact_email.contact_email
    return contact_email or user.username or user.email


@login_required
@require_http_methods(["GET", "POST"])
def migration_landing(request):
    """
    Main entry point: /account/migrate/

    Context-aware:
    - If the current user looks like a SOURCE for an existing move → show generate or status
    - If they are a TARGET → show claim form
    - Otherwise show the primary "start move" guidance
    """
    current_email = _get_current_user_email(request).lower()

    # Check if this user is involved in any active migration
    as_source = EmailMigrationRequest.objects.filter(
        source_email=current_email,
        status__in=[EmailMigrationRequest.STATUS_PENDING, EmailMigrationRequest.STATUS_IN_PROGRESS]
    ).first()

    as_target = EmailMigrationRequest.objects.filter(
        target_email=current_email,
        status__in=[EmailMigrationRequest.STATUS_PENDING, EmailMigrationRequest.STATUS_IN_PROGRESS]
    ).first()

    context = {
        'current_email': current_email,
        'as_source': as_source,
        'as_target': as_target,
        'is_source': bool(as_source),
        'is_target': bool(as_target),
    }

    if request.method == 'POST':
        # Handle regenerate for source
        if 'regenerate_token' in request.POST and as_source:
            return _handle_regenerate(request, as_source, current_email)

        # Handle "Get code" action when acting as source
        if 'generate_token' in request.POST and not as_source:
            return _handle_generate_token(request, current_email)

        # Handle code claim when acting as target
        if 'claim_token' in request.POST:
            return _handle_claim_token(request, current_email)

    return render(request, 'keeper/migration/landing.html', context)


def _handle_generate_token(request, source_email):
    # Basic rate limiting per user (can be improved with Django cache or rate-limit lib)
    # For production, consider django-ratelimit or similar.
    session_key = f'migration_generate_last_{source_email}'
    last = request.session.get(session_key)
    if last and (timezone.now() - timezone.datetime.fromisoformat(last)).total_seconds() < 60:
        return render(request, 'keeper/migration/landing.html', {
            'error': 'Please wait a minute before requesting another migration code.',
            'current_email': source_email,
        })
    request.session[session_key] = timezone.now().isoformat()

    target_email = request.POST.get('target_email', '').strip().lower()
    if not target_email:
        # In real implementation we would show a form asking for the target email first
        # For now, error back to landing
        return render(request, 'keeper/migration/landing.html', {
            'error': 'Please enter the new email address.',
            'current_email': source_email,
        })

    # Prevent self-migration
    if target_email == source_email:
        return render(request, 'keeper/migration/landing.html', {
            'error': 'The old and new email cannot be the same.',
            'current_email': source_email,
        })

    # Check for existing active move as source
    if EmailMigrationRequest.objects.filter(
        source_email=source_email,
        status__in=[EmailMigrationRequest.STATUS_PENDING, EmailMigrationRequest.STATUS_IN_PROGRESS]
    ).exists():
        return redirect('keeper_migration_landing')

    token = secrets.token_urlsafe(48)
    expires = timezone.now() + timedelta(days=TOKEN_LIFETIME_DAYS)

    migration = EmailMigrationRequest.objects.create(
        source_email=source_email,
        target_email=target_email,
        migration_token=token,
        token_expires_at=expires,
    )

    # Full specific link to this move's screen (for emails)
    status_url = f"{MIGRATION_PAGE_URL}status/{migration.pk}/"

    # Send notification to source with the code
    token_msg = f"""You can transfer ownership of your Keeper data (libraries, shares, and groups) to your new email address using the following migration code:

Old email: {source_email}
New email: {target_email}

Migration code: {token}

This code will expire on {expires.strftime('%Y-%m-%d %H:%M')}.

To complete the transfer:

- Log in to Keeper using the new email address.
- Go to the account migration page:
{MIGRATION_PAGE_URL}

- Verify on the identity banner at the top that you are authenticated as the TARGET account for this transfer. If the banner shows the SOURCE account (old email), log out and log in again with the new email before proceeding.

Direct status link for this transfer: {status_url}

Enter the migration code on the page and complete the required confirmation steps.

Once the transfer has completed successfully, your old email address will be deactivated and will no longer provide access to Keeper. All access must use the new email address thereafter.
"""
    send_migration_email(
        subject="Keeper Account Data Transfer - Migration Code",
        message=token_msg,
        recipient_list=[source_email]
    )

    return redirect('keeper_migration_status', pk=migration.pk)


def _handle_regenerate(request, existing_migration, source_email):
    """Regenerate a fresh code for an existing pending move (7-day window)."""
    if existing_migration.status != EmailMigrationRequest.STATUS_PENDING:
        return redirect('keeper_migration_landing')

    token = secrets.token_urlsafe(48)
    expires = timezone.now() + timedelta(days=TOKEN_LIFETIME_DAYS)

    existing_migration.migration_token = token
    existing_migration.token_expires_at = expires
    existing_migration.save(update_fields=['migration_token', 'token_expires_at'])

    # Full specific link to this move's screen (for emails)
    status_url = f"{MIGRATION_PAGE_URL}status/{existing_migration.pk}/"

    # Notify source of new code
    token_msg = f"""A new migration code has been issued for the data transfer to your new email address.

Old email: {source_email}
New email: {existing_migration.target_email}

Migration code: {token}

This code will expire on {expires.strftime('%Y-%m-%d %H:%M')}.

To complete the transfer:

- Log in to Keeper using the new email address.
- Go to the account migration page:
{MIGRATION_PAGE_URL}

- Verify on the identity banner at the top that you are authenticated as the TARGET account for this transfer. If the banner shows the SOURCE account (old email), log out and log in again with the new email before proceeding.

Direct status link for this transfer: {status_url}

Enter the migration code on the page and complete the required confirmation steps.

Once the transfer has completed successfully, your old email address will be deactivated and will no longer provide access to Keeper.
"""
    send_migration_email(
        subject="Keeper Account Data Transfer - New Migration Code",
        message=token_msg,
        recipient_list=[source_email]
    )

    return redirect('keeper_migration_status', pk=existing_migration.pk)


def _handle_claim_token(request, target_email):
    # Basic rate limiting for claims too
    session_key = f'migration_claim_last_{target_email}'
    last = request.session.get(session_key)
    if last and (timezone.now() - timezone.datetime.fromisoformat(last)).total_seconds() < 60:
        return render(request, 'keeper/migration/landing.html', {
            'error': 'Please wait a minute before attempting to use another migration code.',
            'current_email': target_email,
        })
    request.session[session_key] = timezone.now().isoformat()

    token = request.POST.get('token', '').strip()
    if not token:
        return redirect('keeper_migration_landing')

    try:
        migration = EmailMigrationRequest.objects.get(
            migration_token=token,
            target_email=target_email,
            status=EmailMigrationRequest.STATUS_PENDING,
        )
    except EmailMigrationRequest.DoesNotExist:
        # Invalid / expired / wrong target
        return render(request, 'keeper/migration/landing.html', {
            'error': 'That code is not valid, has expired, or does not match the email you are logged in with now.',
            'current_email': target_email,
        })

    if migration.token_expires_at < timezone.now():
        return render(request, 'keeper/migration/landing.html', {
            'error': 'This code has expired. Please ask the person with the old email to get a new one.',
            'current_email': target_email,
        })

    # Show strong confirmation screen
    return render(request, 'keeper/migration/confirm.html', {
        'migration': migration,
        'current_email': target_email,
    })


@login_required
@require_http_methods(["POST"])
def confirm_migration(request, pk):
    """Final confirmation step from the target account."""
    current_email = _get_current_user_email(request).lower()

    migration = EmailMigrationRequest.objects.filter(
        pk=pk,
        target_email=current_email,
        status=EmailMigrationRequest.STATUS_PENDING,
    ).first()

    if not migration:
        return redirect('keeper_migration_landing')

    # Require all critical acknowledgments (strong confirmation as per design)
    if not (request.POST.get('understand_deactivation') == 'on'
            and request.POST.get('understand_clients') == 'on'
            and request.POST.get('have_encrypted_passwords') == 'on'):
        return render(request, 'keeper/migration/confirm.html', {
            'migration': migration,
            'error': 'You must check all three boxes to proceed with the data transfer.',
            'current_email': current_email,
        })

    migration.confirmed_at = timezone.now()
    migration.save(update_fields=['confirmed_at'])

    # Full specific link to this move's screen (for emails)
    status_url = f"{MIGRATION_PAGE_URL}status/{migration.pk}/"

    # Send confirmation to both
    queued_msg = f"""The data transfer from your old account to the new account has been queued.

From: {migration.source_email}
To: {migration.target_email}

The transfer will begin shortly.

You can monitor progress on the account migration page:
{MIGRATION_PAGE_URL}

Verify on the identity banner at the top that you are using the correct account (SOURCE or TARGET). If the banner shows the incorrect account, log out and log in with the appropriate email address (old or new), then return to the page.

Direct status link for this transfer: {status_url}

After the transfer completes, log in using the new email address to access your files and folders. The old email address will be deactivated for Keeper access.
"""
    send_migration_email(
        subject="Keeper Account Data Transfer - Scheduled",
        message=queued_msg,
        recipient_list=[migration.source_email, migration.target_email]
    )

    return render(request, 'keeper/migration/status.html', {
        'migration': migration,
        'just_confirmed': True,
        'current_email': current_email,
    })


@login_required
def migration_status(request, pk):
    current_email = _get_current_user_email(request).lower()
    migration = EmailMigrationRequest.objects.filter(pk=pk).first()

    if not migration or current_email not in (migration.source_email.lower(), migration.target_email.lower()):
        return redirect('keeper_migration_landing')

    return render(request, 'keeper/migration/status.html', {
        'migration': migration,
        'current_email': current_email,
    })