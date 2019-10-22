import pytest
import mock
from pytest_mock import mocker
import traceback
# from mock import patch

import seahub.base
import django
django.setup()

from seahub.views.sysadmin import send_user_add_mail
from seahub.utils import send_html_email
from seahub.settings import SERVER_EMAIL, SERVICE_URL
from seahub.base.accounts import User
from seahub.profile.models import Profile

from keepertestbase import create_tmp_user_with_profile, create_tmp_user

from seahub.base.accounts import RegistrationBackend
from django.core.cache import cache

from keeper.utils import get_domain_list, is_in_mpg_domain_list, KEEPER_DOMAINS_LAST_FETCHED_KEY, \
    KEEPER_DOMAINS_KEY, KEEPER_DOMAINS_TS_KEY, EMAIL_LIST_TIMESTAMP


def test_nickename_in_invite_email(create_tmp_user_with_profile, mocker):
    """Test enchancement https://github.com/MPDL/KEEPER/issues/113:
        Besser Einladungsemail
    """

    send_mail_mock = mocker.patch('seahub.utils.EmailMessage')

    inviter_email = create_tmp_user_with_profile
    fake_request = type("", (), { 'user' : type("", (), dict(username=inviter_email, org=None))  })
    send_user_add_mail(fake_request, 'user@invited.to.keeper.de', 'FAKE_PASSWORD')

    args, kwargs = send_mail_mock.call_args
    assert Profile.objects.get_profile_by_user(inviter_email).nickname in args[1]

#@pytest.mark.skip
def test_account_auto_activation(mocker):
    """ Test auto activation for MPG signed up users,
        see https://github.com/MPDL/KEEPER/issues/133
        NOTES:
            'allow new user registrations'checkbox in admin panel should be checked
            'activate after registration' should be unchecked
            'send activation email' should be unchecked
    """

    # create mocks to go tests through
    request_mock = mocker.patch('django.http.request.HttpRequest')
    login_mock = mocker.patch('seahub.base.accounts.login')

    reg = RegistrationBackend()

    for EMAIL in ('test_email_for_mpg_domain@mpdl.mpg.de','some@rzg.mpg.de','another@biblhertz.it',):
        try:
            send_mail_mock = mocker.patch('seahub.utils.EmailMessage')
            new_user = reg.register(request_mock, email=EMAIL, password1='FAKE_PASSWORD')
            assert send_mail_mock.called, 'email should be sent'
            args, kwargs = send_mail_mock.call_args
            assert args[-1][0]==EMAIL
            assert not new_user.is_active, 'user should not be active'
        except:
            pytest.fail(msg="Bad account: %s,\nmessage: %s" % (EMAIL, traceback.format_exc()) )
        finally:
            User.objects.get(EMAIL).delete()

    EMAIL = 'test_email_for_non_mpg_domain@no_mpg_domain.com'
    try:
        send_mail_mock = mocker.patch('seahub.utils.EmailMessage')
        new_user = reg.register(request_mock, email=EMAIL, password1='FAKE_PASSWORD')
        assert not send_mail_mock.called, 'email should NOT be sent, \'Send activation Email after user registration.\' in {}/sys/settings should be unchecked!'.format(SERVICE_URL)
        assert not new_user.is_active, 'user should NOT be active'
    finally:
        User.objects.get(EMAIL).delete()

#@pytest.mark.skip
def test_mpg_domain_list():
    """Test  MPG domain list from rena service: fetch & push into cache
    """
    pfx = '_TEST'
    def clean_cache():
        cache.delete(KEEPER_DOMAINS_LAST_FETCHED_KEY + pfx)
        cache.delete(KEEPER_DOMAINS_KEY + pfx)
        cache.delete(KEEPER_DOMAINS_TS_KEY + pfx)


    with mock.patch.dict('keeper.utils.__dict__', {
        'KEEPER_DOMAINS_LAST_FETCHED_KEY': KEEPER_DOMAINS_LAST_FETCHED_KEY + pfx,
        'KEEPER_DOMAINS_KEY': KEEPER_DOMAINS_KEY + pfx,
        'KEEPER_DOMAINS_TS_KEY': KEEPER_DOMAINS_TS_KEY + pfx,
    }):

        clean_cache()

        dls = get_domain_list()
        print("\nKEEPER_DOMAINS_LAST_FETCHED: {}\nKEEPER_DOMAINS_TS: {}\n".format(cache.get(KEEPER_DOMAINS_LAST_FETCHED_KEY + pfx), cache.get(KEEPER_DOMAINS_TS_KEY + pfx)))
        assert dls, 'MPG domain list should be not empty'
        assert cache.get(KEEPER_DOMAINS_TS_KEY + pfx), 'MPG domain list timestamp should not be empty'
        assert is_in_mpg_domain_list('someone@mpdl.mpg.de'), 'MPDL should be in domain list!!!'

        clean_cache()

        # CASE: wrong domain or rena is not accessible
        with mock.patch.dict('keeper.utils.__dict__', {'KEEPER_DOMAINS_URL': 'https://wrong_url.de/iplists/keeperx_domains.json'}):
            dls = get_domain_list()
            assert cache.get(KEEPER_DOMAINS_TS_KEY + pfx) == EMAIL_LIST_TIMESTAMP

        clean_cache()
