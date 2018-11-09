# Copyright (c) 2012-2016 Seafile Ltd.
from django.contrib import messages
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404, render

from django.utils.translation import ugettext as _

from seahub.auth import login as auth_login
from seahub.auth import get_backends
from seahub.base.accounts import User
from seahub.constants import DEFAULT_USER
from seahub.invitations.models import Invitation
from seahub.invitations.signals import accept_guest_invitation_successful
from seahub.settings import SITE_ROOT, NOTIFY_ADMIN_AFTER_REGISTRATION
from registration.models import notify_admins_on_register_complete

# KEEPER
# from registration.models import RegistrationProfile
# from django.contrib.sites.shortcuts import get_current_site
from keeper.utils import account_can_be_auto_activated


def token_view(request, token):
    """Show form to let user set password.
    """
    i = get_object_or_404(Invitation, token=token)
    if i.is_expired():
        raise Http404

    if request.method == 'POST':
        passwd = request.POST.get('password', '')
        if not passwd:
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        try:
            User.objects.get(email=i.accepter)
            messages.error(request, _('A user with this email already exists.'))
        except User.DoesNotExist:

            # Create user, set that user as guest, and log user in.
            # u = User.objects.create_user(email=i.accepter, password=passwd,
                                         # is_active=True)
            # User.objects.update_role(u.username, GUEST_USER)
            #i.accept()          # Update invitaion accept time.

            # for backend in get_backends():
                # u.backend = "%s.%s" % (backend.__module__, backend.__class__.__name__)
            # auth_login(request, u)

            # send signal to notify inviter
            #accept_guest_invitation_successful.send(
            #    sender=None, invitation_obj=i)

            # send email to notify admin
            #if NOTIFY_ADMIN_AFTER_REGISTRATION:
            #    notify_admins_on_register_complete(u.email)

            #return HttpResponseRedirect(SITE_ROOT)


            # KEEPER
            # Create user, set that user as default, send, login if mpg user


            is_mpg_user = bool(account_can_be_auto_activated(i.accepter))

            u = User.objects.create_user(email=i.accepter, password=passwd,
                                         is_active=is_mpg_user)

            User.objects.update_role(u.username, DEFAULT_USER)

            i.accept()          # Update invitaion accept time.

            if is_mpg_user:
                for backend in get_backends():
                    u.backend = "%s.%s" % (backend.__module__, backend.__class__.__name__)
                auth_login(request, u)

            # send signal to notify inviter
            accept_guest_invitation_successful.send(
               sender=None, invitation_obj=i)

            # send email to notify admin
            if NOTIFY_ADMIN_AFTER_REGISTRATION:
               notify_admins_on_register_complete(u.email)


            return HttpResponseRedirect(SITE_ROOT if is_mpg_user else '/accounts/register/complete/')

    return render(request, 'invitations/token_view.html', {
        'iv': i,
    })
