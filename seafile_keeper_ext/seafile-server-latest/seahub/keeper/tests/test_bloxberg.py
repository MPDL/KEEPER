import pytest

import seahub.base
import django
django.setup()

import json
#
from seahub.test_utils import BaseTestCase

from urllib import quote

import seahub.api2.views_keeper
from mock_server_request_handler import get_free_port, start_mock_server
import mock
import json


# Following email will receive a notification email if certify successful
# notice: file link will not work and bloxberg link always link to a hard-coded transaction 
EMAIL = 'paipaibear90@gmail.com'

class BloxbergTest(BaseTestCase):

  @classmethod
  def setup_class(cls):
      cls.mock_server_port = get_free_port()
      start_mock_server(cls.mock_server_port)

  def setUp(self):
    self.user = self.create_user(EMAIL)

  def tearDown(self):
    self.remove_user(self.user.username)

  def test_certify_succeed(self): 

    """Test certify api
    """
    self.login_as(self.user)        

    print('user: {0}'.format(self.user.username))
    print('repo_id: {0}'.format(self.repo.repo_id))
    print('file_path: {0}'.format(self.file))

    mock_users_url = 'http://localhost:{port}/certifyData'.format(port=self.mock_server_port)

    # Patch URL so that the service uses the mock server URL instead of the real URL.
    with mock.patch.dict('seahub.api2.views_keeper.__dict__', {'URL': mock_users_url}):
      self.endpoint = '/api2/ajax/certify/'
      resp = self.client.get(
        self.endpoint, {
          'repo_id': self.repo.repo_id,
          'path': self.file
        })
      self.assertEqual(200, resp.status_code)
      
      json_resp = json.loads(resp.content)
      self.assertEqual("Transaction succeeded", json_resp['msg'])
      print(json_resp['msg'])
      self.assertTrue(json_resp['txReceipt']['transactionHash'] is not None)
      print('transaction_hash: {0}'.format(json_resp['txReceipt']['transactionHash']))


