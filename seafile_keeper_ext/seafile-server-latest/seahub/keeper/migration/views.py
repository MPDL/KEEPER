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
from django.db import IntegrityError
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
    # How long a COMPLETED transfer keeps showing its "completed" message on the
    # landing page. After this, the page returns to the "start a new transfer"
    # state so a new migration can be initiated on either account.
    COMPLETED_DISPLAY_HOURS = getattr(django_settings, 'KEEPER_MIGRATION_COMPLETED_DISPLAY_HOURS', 48)
except Exception:
    DEFAULT_FROM_EMAIL = 'keeper@mpdl.mpg.de'
    SUPPORT_EMAIL = 'keeper@mpdl.mpg.de'
    MIGRATION_PAGE_URL = 'https://keeper.mpdl.mpg.de/account/migrate/'
    TOKEN_LIFETIME_DAYS = 7
    COMPLETED_DISPLAY_HOURS = 48

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


def _authoritative_email(username):
    """The account's DB-authoritative email, or None — NEVER a user-edited value.

    - Old / local accounts: the username IS the unique, system-assigned login email
      (not user-editable), so it is authoritative.
    - SSO accounts (uuid@auth.local): trust profile.contact_email ONLY when it was set
      by the system/IdP (is_manually_set_contact_email == 0). A user-edited contact
      email (flag 1) is never trusted.

    Note: social_auth_usersocialauth stores only the numeric NameID (no email), so the
    IdP-provided address is the system-set contact_email distinguished by that flag.
    """
    username = (username or '').strip().lower()
    if not username:
        return None
    if '@' in username and not username.endswith('@auth.local'):
        return username
    try:
        from seahub.profile.models import Profile
        p = Profile.objects.filter(user__iexact=username).first()
        if p and p.contact_email and not getattr(p, 'is_manually_set_contact_email', True):
            return p.contact_email.strip().lower()
    except Exception:
        pass
    return None


def _accounts_sharing_email(email, exclude_username):
    """Account ids that AUTHORITATIVELY share this email: the account whose username
    IS the email (unique login id), plus SSO accounts whose contact_email was set by
    the system/IdP (is_manually_set_contact_email == 0). User-edited contact emails are
    ignored, so a user cannot point at someone else's account by editing their own
    contact email."""
    email = (email or '').strip().lower()
    exclude = (exclude_username or '').strip().lower()
    if not email:
        return []
    found = []
    # The account whose username IS this email (unique + authoritative).
    if email != exclude:
        try:
            from seahub.base.accounts import User
            User.objects.get(email)
            found.append(email)
        except Exception:
            pass
    # SSO accounts whose SYSTEM-set (IdP) contact_email matches.
    try:
        from seahub.profile.models import Profile
        for p in Profile.objects.filter(contact_email__iexact=email):
            u = (p.user or '').strip()
            if (u and u.lower() != exclude and u not in found
                    and not getattr(p, 'is_manually_set_contact_email', True)):
                found.append(u)
    except Exception:
        pass
    return found


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
    current_email = _get_current_user_email(request).lower()  # display only
    current_username = (request.user.username or '').strip().lower()
    # Authoritative identity for matching rows — the login id and the system-verified
    # email only (never a user-edited contact email), so a user can only see/act on
    # migrations that are genuinely theirs.
    identities = [i for i in {current_username, _authoritative_email(current_username)} if i]

    # Check if this user is involved in any active migration
    as_source = EmailMigrationRequest.objects.filter(
        source_email__in=identities,
        status__in=[EmailMigrationRequest.STATUS_PENDING, EmailMigrationRequest.STATUS_IN_PROGRESS]
    ).first()

    as_target = EmailMigrationRequest.objects.filter(
        target_email__in=identities,
        status__in=[EmailMigrationRequest.STATUS_PENDING, EmailMigrationRequest.STATUS_IN_PROGRESS]
    ).first()

    # If there is no active (pending/in_progress) migration, fall back to the most
    # recent finished one (completed/failed) so its status is shown here on the
    # landing page. The status is merged into /account/migrate/ (no separate page).
    #
    # A COMPLETED transfer is only shown for COMPLETED_DISPLAY_HOURS (default 48h)
    # after it finished; once that window passes the page returns to the "start a
    # new transfer" state so a new migration can be initiated on either account
    # (e.g. if the deactivated source account is later reactivated). FAILED transfers
    # keep showing so the error / support message stays visible until resolved.
    if not as_source and not as_target:
        recent_source = EmailMigrationRequest.objects.filter(
            source_email__in=identities).order_by('-requested_at').first()
        recent_target = EmailMigrationRequest.objects.filter(
            target_email__in=identities).order_by('-requested_at').first()

        candidate, candidate_is_source = None, False
        if recent_source and recent_target:
            if recent_source.requested_at >= recent_target.requested_at:
                candidate, candidate_is_source = recent_source, True
            else:
                candidate, candidate_is_source = recent_target, False
        elif recent_source:
            candidate, candidate_is_source = recent_source, True
        elif recent_target:
            candidate, candidate_is_source = recent_target, False

        # Hide a completed transfer once its display window has elapsed.
        if (candidate
                and candidate.status == EmailMigrationRequest.STATUS_COMPLETED
                and candidate.completed_at
                and timezone.now() - candidate.completed_at > timedelta(hours=COMPLETED_DISPLAY_HOURS)):
            candidate = None

        if candidate and candidate_is_source:
            as_source = candidate
        elif candidate:
            as_target = candidate

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

        # Handle cancel for source (only allowed while still pending, i.e. before the worker starts it)
        if 'cancel_token' in request.POST and as_source:
            return _handle_cancel(request, as_source, current_email)

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
            'error': 'Please wait a minute before requesting another data transfer code.',
            'current_email': source_email,
        })
    request.session[session_key] = timezone.now().isoformat()

    # Record the source by its DB-authoritative id (login id / system-set email), so the
    # owner always matches their own request and no one else can act on it.
    source_account = (_authoritative_email((request.user.username or '').strip().lower())
                      or (request.user.username or '').strip().lower()
                      or source_email)

    target_email = request.POST.get('target_email', '').strip().lower()
    if not target_email:
        # In real implementation we would show a form asking for the target email first
        # For now, error back to landing
        return render(request, 'keeper/migration/landing.html', {
            'error': 'Please enter the email address of your new account.',
            'current_email': source_email,
        })

    # Prevent self-migration
    if target_email in (source_email, source_account):
        return render(request, 'keeper/migration/landing.html', {
            'error': 'The source and target email addresses cannot be the same.',
            'current_email': source_email,
        })

    # The target email must belong to a real, AUTHORITATIVE Keeper account — one whose
    # login id is this email, or an SSO account whose system-set (IdP) email is this
    # address. A user-edited contact email is never accepted as a target identity, and
    # the same authoritative rule is used at claim/confirm so the target can complete it.
    if not _accounts_sharing_email(target_email, source_account):
        return render(request, 'keeper/migration/landing.html', {
            'error': 'No Keeper account uses that email address as its verified login or SSO email. '
                     'Please check the address and make sure that account can already sign in to Keeper.',
            'current_email': source_email,
        })

    # Check for existing active move as source
    if EmailMigrationRequest.objects.filter(
        source_email=source_account,
        status__in=[EmailMigrationRequest.STATUS_PENDING, EmailMigrationRequest.STATUS_IN_PROGRESS]
    ).exists():
        return redirect('keeper_migration_landing')

    token = secrets.token_urlsafe(48)
    expires = timezone.now() + timedelta(days=TOKEN_LIFETIME_DAYS)

    try:
        migration = EmailMigrationRequest.objects.create(
            source_email=source_account,
            target_email=target_email,
            migration_token=token,
            token_expires_at=expires,
        )
    except IntegrityError:
        # Lost a race / duplicate — just return to the landing page.
        return redirect('keeper_migration_landing')

    # Send notification to source with the code
    token_msg = f"""You can transfer ownership of your Keeper data (libraries, shares, and groups) to your new account using the following data transfer code:

From: {source_email}
To: {target_email}

Data transfer code: {token}

This code will expire on {expires.strftime('%Y-%m-%d %H:%M')}.

To complete the transfer:

- Log in to Keeper using the new account (the target account).
- Go to the account data transfer page:
{MIGRATION_PAGE_URL}

- Verify on the identity banner at the top that you are authenticated as the TARGET account for this transfer. If the banner shows the SOURCE account, log out and log in again with the target account before proceeding.

- Enter the data transfer code on the page and complete the required confirmation steps.

Once the transfer has completed successfully, the source account will be deactivated and will no longer provide access to Keeper. All access must use the new account thereafter.
"""
    send_migration_email(
        subject="Keeper Account Data Transfer - Data Transfer Code",
        message=token_msg,
        recipient_list=[source_email]
    )

    # Back to the landing page so the source immediately sees the code (with a copy button).
    return redirect('keeper_migration_landing')


def _handle_regenerate(request, existing_migration, source_email):
    """Regenerate a fresh code for an existing pending move (7-day window)."""
    if existing_migration.status != EmailMigrationRequest.STATUS_PENDING:
        return redirect('keeper_migration_landing')

    token = secrets.token_urlsafe(48)
    expires = timezone.now() + timedelta(days=TOKEN_LIFETIME_DAYS)

    existing_migration.migration_token = token
    existing_migration.token_expires_at = expires
    existing_migration.save(update_fields=['migration_token', 'token_expires_at'])

    # Notify source of new code
    token_msg = f"""A new data transfer code has been issued for the transfer to your new account.

From: {source_email}
To: {existing_migration.target_email}

Data transfer code: {token}

This code will expire on {expires.strftime('%Y-%m-%d %H:%M')}.

To complete the transfer:

- Log in to Keeper using the new account (the target account).
- Go to the account data transfer page:
{MIGRATION_PAGE_URL}

- Verify on the identity banner at the top that you are authenticated as the TARGET account for this transfer. If the banner shows the SOURCE account, log out and log in again with the target account before proceeding.

- Enter the data transfer code on the page and complete the required confirmation steps.

Once the transfer has completed successfully, the source account will be deactivated and will no longer provide access to Keeper.
"""
    send_migration_email(
        subject="Keeper Account Data Transfer - New Data Transfer Code",
        message=token_msg,
        recipient_list=[source_email]
    )

    # Back to the landing page so the source immediately sees the new code (with a copy button).
    return redirect('keeper_migration_landing')


def _handle_cancel(request, existing_migration, source_email):
    """Cancel a pending move entirely.

    Only allowed while the request is still 'pending' (before the background
    worker has started it). Once the migration is in_progress/completed/failed
    it can no longer be cancelled. Cancelling fully removes the request so the
    user is free to start a new one, and invalidates the issued data transfer code.
    """
    target_email = existing_migration.target_email

    # Atomic guard against the race where the worker flips the row to
    # 'in_progress' between page load and this click: only delete if still pending.
    deleted, _ = EmailMigrationRequest.objects.filter(
        pk=existing_migration.pk,
        status=EmailMigrationRequest.STATUS_PENDING,
    ).delete()

    if not deleted:
        # Worker already picked it up; cancellation is no longer possible.
        return render(request, 'keeper/migration/landing.html', {
            'error': 'This data transfer has already started and can no longer be cancelled.',
            'current_email': source_email,
            'as_source': existing_migration,
            'is_source': True,
        })

    # Notify both parties that the queued transfer was cancelled.
    cancel_msg = f"""The pending Keeper data transfer has been cancelled.

From: {source_email}
To: {target_email}

No data has been moved, and both accounts remain unchanged. The previously issued data transfer code is no longer valid.

If you wish to transfer your data later, you can start a new request at any time:
{MIGRATION_PAGE_URL}
"""
    send_migration_email(
        subject="Keeper Account Data Transfer - Cancelled",
        message=cancel_msg,
        recipient_list=[source_email, target_email],
    )

    # Re-render the landing page in its fresh "start a new transfer" state with a confirmation.
    return render(request, 'keeper/migration/landing.html', {
        'current_email': source_email,
        'notice': 'The data transfer has been cancelled. The data transfer code is no longer valid. No data was moved. You can start a new transfer whenever you are ready.',
    })


def _handle_claim_token(request, target_email):
    # Basic rate limiting for claims too
    session_key = f'migration_claim_last_{target_email}'
    last = request.session.get(session_key)
    if last and (timezone.now() - timezone.datetime.fromisoformat(last)).total_seconds() < 60:
        return render(request, 'keeper/migration/landing.html', {
            'error': 'Please wait a minute before attempting to use another data transfer code.',
            'current_email': target_email,
        })
    request.session[session_key] = timezone.now().isoformat()

    token = request.POST.get('token', '').strip()
    if not token:
        return redirect('keeper_migration_landing')

    # The code is the secret; additionally require that the row's target matches the
    # claimer's AUTHORITATIVE identity (login id / system-set email), never a contact email.
    current_username = (request.user.username or '').strip().lower()
    identities = [i for i in {current_username, _authoritative_email(current_username)} if i]

    try:
        migration = EmailMigrationRequest.objects.get(
            migration_token=token,
            target_email__in=identities,
            status=EmailMigrationRequest.STATUS_PENDING,
        )
    except EmailMigrationRequest.DoesNotExist:
        # Invalid / expired / wrong target
        return render(request, 'keeper/migration/landing.html', {
            'error': 'That code is not valid, has expired, or does not match the account you are logged in with now.',
            'current_email': target_email,
        })

    if migration.token_expires_at < timezone.now():
        return render(request, 'keeper/migration/landing.html', {
            'error': 'This code has expired. Please ask the source account holder to request a new one.',
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
    current_username = (request.user.username or '').strip().lower()

    migration = EmailMigrationRequest.objects.filter(
        pk=pk,
        status=EmailMigrationRequest.STATUS_PENDING,
    ).first()

    if not migration:
        return redirect('keeper_migration_landing')

    # Only the TARGET may confirm, matched by authoritative identity (login id +
    # system-verified email) — never the user-editable contact email.
    identities = {i for i in (current_username, _authoritative_email(current_username)) if i}
    if migration.target_email.lower() not in identities:
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

    # Send confirmation to both
    queued_msg = f"""The data transfer from the source account to the target account has been queued.

From: {migration.source_email}
To: {migration.target_email}

The transfer will begin shortly.

You can monitor progress on the account data transfer page:
{MIGRATION_PAGE_URL}

Verify on the identity banner at the top that you are using the correct account (SOURCE or TARGET). If the banner shows the incorrect account, log out and log in with the appropriate account, then return to the page.

After the transfer completes, log in using the target account to access your files and folders. The source account will be deactivated for Keeper access.
"""
    # Don't send to internal virtual ids (uuid@auth.local); use real addresses only.
    recipients = [r for r in (migration.source_email, migration.target_email)
                  if r and '@' in r and not r.lower().endswith('@auth.local')]
    if not recipients:
        recipients = [current_email]
    send_migration_email(
        subject="Keeper Account Data Transfer - Scheduled",
        message=queued_msg,
        recipient_list=recipients
    )

    # Status is shown on the landing page itself; go back there after confirming.
    return redirect('keeper_migration_landing')


@login_required
def migration_status(request, pk):
    # The status is now merged into the landing page (/account/migrate/).
    # This route is kept only so older links (e.g. in already-sent emails)
    # still work; it simply redirects to the landing page.
    return redirect('keeper_migration_landing')