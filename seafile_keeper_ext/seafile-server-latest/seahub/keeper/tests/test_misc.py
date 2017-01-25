import pytest
import mock
from pytest_mock import mocker
# from mock import patch

import seahub.base
import django
django.setup()

from seahub.views.sysadmin import send_user_add_mail
from seahub.utils import send_html_email
from seahub.settings import SERVER_EMAIL
from seahub.base.accounts import User
from seahub.profile.models import Profile
from uuid import uuid4
# @pytest.mark.skip

INVITER_NICK = 'Random User'

@pytest.fixture(scope='function')
def create_tmp_user_with_profile():
    """Create new random user"""
    email = uuid4().hex + '@test.com'
    kwargs = {
        'email': email,
        'is_staff': False,
        'is_active': True
    }
    user = User.objects.create_user(password='secret', **kwargs)
    Profile.objects.add_or_update(email, INVITER_NICK)
    yield email
    # teardown code
    Profile.objects.delete_profile_by_user(email)
    User.objects.get(email).delete()

def test_nickename_in_invite_email(create_tmp_user_with_profile, mocker):
    """Test enchancement https://github.com/MPDL/KEEPER/issues/113:
        Besser Einladungsemail
    """
    # send_mail_mock = mocker.patch('seahub.views.sysadmin.send_html_email')
    send_mail_mock = mocker.patch('seahub.utils.EmailMessage')

    fake_request = type("", (), { 'user' : type("", (), dict(username=create_tmp_user_with_profile, org=None))  })
    send_user_add_mail(fake_request, 'user@invited.to.keeper.de', 'FAKE_PASSWORD')

    args, kwargs = send_mail_mock.call_args
    assert INVITER_NICK in args[1]

