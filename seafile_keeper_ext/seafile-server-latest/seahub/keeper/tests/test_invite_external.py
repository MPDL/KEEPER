import pytest

import seahub.base
import django
django.setup()

import json

from seahub.invitations.models import Invitation
from seahub.test_utils import BaseTestCase

INTERNAL_EMAIL = 'test@mpdl.mpg.de'
EXTERNAL_EMAIL = '1@1.com'

class InvitationsTest(BaseTestCase):
    def setUp(self):

        self.inviter = self.create_user(INTERNAL_EMAIL)
        self.accepter = self.create_user(EXTERNAL_EMAIL)

    def tearDown(self):
		self.remove_user(self.inviter.username)
		self.remove_user(self.accepter.username)

    def test_mpg_internal_can_invite(self):

        self.login_as(self.inviter)
        self.i = Invitation.objects.add(inviter=self.inviter.username,
                                        accepter=self.accepter.username)
        self.endpoint = '/api/v2.1/invitations/' + self.i.token + '/'
        assert Invitation.objects.get(inviter=self.inviter.username) is not None

        resp = self.client.get(self.endpoint)
        self.assertEqual(200, resp.status_code)

        json_resp = json.loads(resp.content)
        assert json_resp['inviter'] == self.inviter.username
        assert json_resp['accepter'] == self.accepter.username

    def test_mpg_external_cannot_invite(self):

        self.login_as(self.accepter)
        self.i = Invitation.objects.add(inviter=self.accepter.username,
                                        accepter=self.inviter.username)
        self.endpoint = '/api/v2.1/invitations/' + self.i.token + '/'
        assert Invitation.objects.get(inviter=self.accepter.username) is not None

        resp = self.client.get(self.endpoint)
        self.assertEqual(403, resp.status_code)

