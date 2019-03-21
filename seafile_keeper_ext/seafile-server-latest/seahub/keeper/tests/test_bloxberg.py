import pytest

import seahub.base
import django
django.setup()

from seahub.test_utils import BaseTestCase

from urllib import quote

import seahub.api2.views_keeper as views_keeper
import keeper.bloxberg.bloxberg_manager as bloxberg_manager
from seafobj.fs import SeafFile  
import mock
import json
import datetime
from django.core import mail

from seahub.notifications.models import UserNotification
from seahub.base.models import CommandsLastCheck

"""
Following email will receive a notification email if the certify process is successful, 
file link will not work since the test user is destoried after running the test.

!!!IMPORTANT: NEVER use an email which already exists in the system!!!
"""
EMAIL = 'test@mpdl.mpg.de'

class BloxbergTest(BaseTestCase):

  def setUp(self):
    self.user = self.create_user(EMAIL)

  def tearDown(self):
    self.remove_user(self.user.username)

  '''
  unit tests in bloxberg_manager
  '''

  # @pytest.mark.skip
  def test_get_commit_root_id(self):
    self.login_as(self.user)
    commit_root_id = bloxberg_manager.get_commit_root_id(self.repo.repo_id)
    self.assertEqual(40, len(commit_root_id))
    print(commit_root_id)

  # @pytest.mark.skip
  def test_get_file_by_path(self):
    self.login_as(self.user)
    file_dir = bloxberg_manager.get_file_by_path(self.repo.repo_id, self.file)
    self.assertTrue(isinstance(file_dir, SeafFile))
    print('type: {0}'.format(type(file_dir)))

  # @pytest.mark.skip
  def test_hash_file_succeed(self):
    file_hash_json = bloxberg_manager.hash_file(self.repo.repo_id, self.file, EMAIL)
    file_hash = file_hash_json['certifyVariables']['checksum']
    self.assertEqual(64, len(file_hash))
    print('file_hash: {0}'.format(file_hash))

  # @pytest.mark.skip
  def test_create_bloxberg_certificate(self):
    self.login_as(self.user)
    transaction_id = '0xdeb2a269c9cd01a343f1c0ad25e48409f3b81c7e2b01c65e5a8ee87b2a8bff6f'
    created_time = datetime.datetime.now()
    checksum = 'cacf8d391aa4443765424e73bb0f168b1783bb9e5787067ffd04cb35fe14b3bb'
    obj_id = bloxberg_manager.create_bloxberg_certificate(self.repo.repo_id, self.file, transaction_id, created_time, checksum, EMAIL);
    self.assertTrue(type(obj_id) is long)
    print(obj_id)

  # @pytest.mark.skip
  def test_send_notification(self):
    self.login_as(self.user)
    timestamp = datetime.datetime.now()
    transaction_id = '0xdeb2a269c9cd01a343f1c0ad25e48409f3b81c7e2b01c65e5a8ee87b2a8bff6f'
    bloxberg_manager.send_notification(self.repo.repo_id, self.file, transaction_id, timestamp, EMAIL)
    label = "notifications_send_notices"
    cmd_last_check = CommandsLastCheck.objects.get(command_type=label)
    unseen_notices = UserNotification.objects.get_all_notifications(
        seen=False, time_since=cmd_last_check.last_check)

    self.assertEqual(1, len(unseen_notices))
    print('unread notification: {0}'.format(len(unseen_notices)))
    print(unseen_notices[0])

  # @pytest.mark.skip
  def test_request_bloxberg_succeed(self):
    """
    Unit Test: test
    """  
    certify_payload = {
      'certifyVariables': {
        'checksum': 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855', 
        'authorName': 'tester No.1', 
        'timestampString': '1551692787.55'
      }
    }

    mock_users_url = 'http://10.0.2.2:5000/certifyData'

    # Patch URL so that the service uses the mock server URL instead of the real URL.
    with mock.patch.dict('seahub.api2.views_keeper.__dict__', {'URL': mock_users_url}):
      resp = views_keeper.request_bloxberg(certify_payload)
      json_resp = resp.json()
      self.assertEqual(200, resp.status_code)
      self.assertEqual("Transaction succeeded", json_resp['msg'])
      print(json_resp['msg'])
      self.assertTrue(json_resp['txReceipt']['transactionHash'] is not None)
      print('transaction_hash: {0}'.format(json_resp['txReceipt']['transactionHash']))

  #@pytest.mark.skip
  def test_request_bloxberg_failed(self):

    certify_payload = {}

    mock_users_url = 'http://10.0.2.2:5000/certifyData'

    # Patch URL so that the service uses the mock server URL instead of the real URL.
    with mock.patch.dict('seahub.api2.views_keeper.__dict__', {'URL': mock_users_url}):
      resp = views_keeper.request_bloxberg(certify_payload)
      self.assertEqual(500, resp.status_code)

  # @pytest.mark.skip
  def test_certify_succeed(self):

    """
    Integration Test: Test certify a file on KEEPER
    """
    self.login_as(self.user)

    print('user: {0}'.format(self.user.username))
    print('repo_id: {0}'.format(self.repo.repo_id))
    print('file_path: {0}'.format(self.file))

    mock_users_url = 'http://10.0.2.2:5000/certifyData'

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

      label = "notifications_send_notices"
      cmd_last_check = CommandsLastCheck.objects.get(command_type=label)
      unseen_notices = UserNotification.objects.get_all_notifications(
        seen=False, time_since=cmd_last_check.last_check)
  
      self.assertEqual(1, len(unseen_notices))
      print('unread notification: {0}'.format(len(unseen_notices)))
      print(unseen_notices[0])