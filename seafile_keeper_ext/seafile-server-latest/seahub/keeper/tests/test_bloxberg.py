import pytest

import seahub.base
import django
django.setup()

import json
#
from seahub.test_utils import BaseTestCase

from urllib import quote

import seahub.api2.views_keeper as views_keeper
import keeper.bloxberg.bloxberg_manager as bloxberg_manager
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
    
  def test_request_bloxberg_succeed(self):

    certify_payload = {
      'certifyVariables': {
        'checksum': 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855', 
        'authorName': 'paipaibear90', 
        'timestampString': '1551692787.55'
      }
    }

    mock_users_url = 'http://localhost:{port}/certifyData'.format(port=self.mock_server_port)

    # Patch URL so that the service uses the mock server URL instead of the real URL.
    with mock.patch.dict('seahub.api2.views_keeper.__dict__', {'URL': mock_users_url}):
      resp = views_keeper.request_bloxberg(certify_payload)
      json_resp = resp.json()
      self.assertEqual(200, resp.status_code)
      self.assertEqual("Transaction succeeded", json_resp['msg'])
      print(json_resp['msg'])
      self.assertTrue(json_resp['txReceipt']['transactionHash'] is not None)
      print('transaction_hash: {0}'.format(json_resp['txReceipt']['transactionHash']))      


  def test_request_bloxberg_failed(self):

    certify_payload = {
    }

    mock_users_url = 'http://localhost:{port}/certifyData'.format(port=self.mock_server_port)

    # Patch URL so that the service uses the mock server URL instead of the real URL.
    with mock.patch.dict('seahub.api2.views_keeper.__dict__', {'URL': mock_users_url}):
      resp = views_keeper.request_bloxberg(certify_payload)
      self.assertTrue(resp is None)  
  

  def test_hash_file_succeed(self):
    try:
      file_hash = bloxberg_manager.hash_file(self.repo, self.file)
      print('file_hash: {0}'.format(file_hash))
    except AttributeError as e:
      print(str(e))

  def test_hash_file_failed(self):
    try:
      file_hash = bloxberg_manager.hash_file(self.repo, self.file)
      print('file_hash: {0}'.format(file_hash))
    except AttributeError as e:
      print(str(e))
      self.assertTrue("'NoneType' object has no attribute 'get_stream'" in str(e))

  def test_commit_id(self):
    self.login_as(self.user)
    commit_id = bloxberg_manager.get_commit_root_id(self.repo.repo_id)
    print(commit_id)
    self.assertTrue(commit_id)

  def test_get_file_by_path(self):
    self.login_as(self.user) 
    try:
      file_dir = bloxberg_manager.hash_file(self.repo.repo_id, self.file, EMAIL)
      print(file_dir) 
    except Exception as e:
      print(str(e))


