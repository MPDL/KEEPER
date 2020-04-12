import pytest
import unittest

import django
django.setup()

import os

from keeper.models import CDC, Catalog
from seahub.profile.models import Profile

from seaserv import seafile_api
from seahub.settings import SERVER_EMAIL

from .keepertestbase import create_tmp_user, create_tmp_repo

from keeper.utils import query_keeper_archiving_status,\
        add_keeper_archiving_task, check_keeper_repo_archiving_status
from time import sleep


#@pytest.mark.skip

class TestKeeperArchiving(unittest.TestCase):

    def setUp(self):
        self.user = next(create_tmp_user())
        # print("CREATED USER: " + self.user)
        self.repo = next(create_tmp_repo(self.user))
        # print("CREATED REPO: " + self.repo.id)
        with open("data/archive-metadata.md", 'r') as f:
            seafile_api.post_file(self.repo.id, os.path.abspath(f.name), "/", "archive-metadata.md", self.user)
        with open("data/sample.png", 'r') as f:
            seafile_api.post_file(self.repo.id, os.path.abspath(f.name), "/", "sample.png", self.user)
        sleep(5)

    def tearDown(self):
        CDC.objects.delete_by_repo_id(self.repo.id)
        Catalog.objects.delete_by_repo_id(self.repo.id)
        Profile.objects.delete_profile_by_user(self.user)
        seafile_api.remove_repo(self.repo.id)
        # print("REMOVED USER: " + self.user)
        # print("REMOVED REPO: " + self.repo.id)
        #TODO: clean __LOCAL_STORAGE__


    # @pytest.mark.skip
    def test_add_keeper_archiving_task(self):
        """TODO: Docstring.
        """
        repo_id = self.repo.id
        owner = self.user

        resp = add_keeper_archiving_task(repo_id, owner)
        print(resp)
        ver = resp['version']

        # wait till end of archiving
        while True:
            sleep(0.1)
            resp = query_keeper_archiving_status(repo_id, owner, ver)
            print(resp)
            assert resp.get('status') in ('PROCESSING', 'NOT_FOUND', 'DONE', 'RESTART', 'ERROR'), 'Wrong task status, %s' % resp
            if resp.get('status') == 'DONE':
                break;


    # @pytest.mark.skip
    def test_check_keeper_repo_archiving_status(self):
        """TODO: Docstring for test_archiving.
        """
        repo_id = self.repo.id
        owner = self.user

        # 1. wrong params
        # bad repo_id
        resp = check_keeper_repo_archiving_status('fake_repo_id', owner, 'is_snapshot_archived')
        print(resp)
        assert 'ERROR' == resp.get('status')
        assert 'Message: invalid repo id' in resp.get('msg')

        # wrong repo_id
        resp = check_keeper_repo_archiving_status('ffffffff-ffff-ffff-ffff-ffffffffffff', owner, 'is_snapshot_archived')
        print(resp)
        assert 'ERROR' == resp.get('status')
        assert 'Cannot get library.' == resp.get('error')

        # wrong action
        action = 'some_fake_action'
        resp = check_keeper_repo_archiving_status(repo_id, owner, action)
        print(resp)
        assert 'ERROR' == resp.get('status')
        assert 'Unknown action: ' + action == resp.get('error')


        # 2. not yet archived
        # is_snapshot_archived
        resp = check_keeper_repo_archiving_status(repo_id, owner, 'is_snapshot_archived')
        assert resp.get('action') == 'is_snapshot_archived'
        assert resp.get('is_snapshot_archived') == 'false'

        # get_quota
        resp = check_keeper_repo_archiving_status(repo_id, owner, 'get_quota')
        print(resp)
        assert resp.get('curr_ver') == 0
        assert resp.get('remains') == 5

        # is_repo_too_big
        resp = check_keeper_repo_archiving_status(repo_id, owner, 'is_repo_too_big')
        print(resp)
        assert resp.get('is_repo_too_big') == 'false'


        # 3. after archiving
        resp = add_keeper_archiving_task(repo_id, owner)
        print(resp)
        ver = resp.get('version')

        # wait till end of archiving
        while True:
            sleep(1)
            resp = query_keeper_archiving_status(repo_id, owner, ver)
            print(resp)
            if resp.get('status') == 'DONE':
                break;

        # is_snapshot_archived
        resp = check_keeper_repo_archiving_status(repo_id, owner, 'is_snapshot_archived')
        assert resp.get('is_snapshot_archived') == 'true', 'Check response: %s' % resp

        # get_quota
        resp = check_keeper_repo_archiving_status(repo_id, owner, 'get_quota')
        print(resp)
        assert resp.get('curr_ver') == 1
        assert resp.get('remains') == 4

        # is_repo_too_big
        resp = check_keeper_repo_archiving_status(repo_id, owner, 'is_repo_too_big')
        print(resp)
        assert resp.get('is_repo_too_big') == 'false'