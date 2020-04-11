import pytest
import unittest

import seahub.base
import django
django.setup()

import mock

import os
import shutil
import tempfile

from keeper.models import CDC, Catalog
from seahub.profile.models import Profile

from seaserv import seafile_api
from seahub.settings import SERVER_EMAIL

from http import HTTPStatus

from .keepertestbase import create_tmp_user_with_profile, create_tmp_user, create_tmp_repo

from datetime import datetime

# from seafevents.keeper_archiving import KeeperArchiving
# from seafevents.keeper_archiving.task_manager import task_manager, Worker
# from seafevents.keeper_archiving.config import get_keeper_archiving_conf
# from seafevents.utils import get_config
from keeper.utils import query_keeper_archiving_status,\
        add_keeper_archiving_task, check_keeper_repo_archiving_status
from time import sleep

import json
from seahub.notifications.models import UserNotification

from seafevents.keeper_archiving import task_manager as arch_task_mgr

#@pytest.mark.skip

class TestKeeperArchiving(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.user = next(create_tmp_user())
        cls.repo = next(create_tmp_repo(cls.user))
        with open("data/archive-metadata.md", 'r') as f:
            seafile_api.post_file(cls.repo.id, os.path.abspath(f.name), "/", "archive-metadata.md", cls.user)
        with open("data/sample.png", 'r') as f:
            seafile_api.post_file(cls.repo.id, os.path.abspath(f.name), "/", "sample.png", cls.user)
        sleep(5)

    @classmethod
    def tearDownClass(cls):
        seafile_api.remove_repo(cls.repo.id)
        CDC.objects.delete_by_repo_id(cls.repo.id)
        Catalog.objects.delete_by_repo_id(cls.repo.id)
        Profile.objects.delete_profile_by_user(cls.user)

    def test_check_keeper_repo_archiving_status(self):
        """TODO: Docstring for test_archiving.
        """

        repo_id = self.repo.id

        # not yet archived
        # is_snapshot_archived
        resp = check_keeper_repo_archiving_status(repo_id, self.user, 'is_snapshot_archived')
        assert resp['action'] == 'is_snapshot_archived'
        assert resp['is_snapshot_archived'] == 'false'

        # get_quota
        resp = check_keeper_repo_archiving_status(repo_id, self.user, 'get_quota')
        print(resp)
        assert resp['curr_ver'] == 0
        assert resp['remains'] == 5

        # is_repo_too_big
        resp = check_keeper_repo_archiving_status(repo_id, self.user, 'is_repo_too_big')
        print(resp)
        assert resp['is_repo_too_big'] == 'false'


        # after archiving
        resp = add_keeper_archiving_task(repo_id, self.user)
        print(resp)
        ver = resp['version']

        # wait till end of archiving
        while True:
            sleep(1)
            resp = query_keeper_archiving_status(repo_id, self.user, ver)
            print(resp)
            if resp.get('status') == 'DONE':
                break;

        # is_snapshot_archived
        resp = check_keeper_repo_archiving_status(repo_id, self.user, 'is_snapshot_archived')
        assert 'is_snapshot_archived' in resp and resp['is_snapshot_archived'] == 'true', 'Check response: %s' % resp

        # get_quota
        resp = check_keeper_repo_archiving_status(repo_id, self.user, 'get_quota')
        print(resp)
        assert resp.get('curr_ver') == 1
        assert resp.get('remains') == 4

        # is_repo_too_big
        resp = check_keeper_repo_archiving_status(repo_id, self.user, 'is_repo_too_big')
        print(resp)
        assert resp.get('is_repo_too_big') == 'false'

    @pytest.mark.skip
    def test_tmp_repo_archiving(create_tmp_repo):
        """TODO: Docstring for test_archiving.

        :create_tmp_repo: TODO
        :returns: TODO

        """
        repo = create_tmp_repo
        assert not repo is None

        f = tempfile.NamedTemporaryFile()
        os.chmod(f.name, 0o777)
        f.write(b'Text')
        f.flush()
        seafile_api.post_file(repo.id, f.name, "/", "some_file_in_root.txt", SERVER_EMAIL)
        f.close()

        seafile_api.post_dir(repo.id, "/", "sub_dir1", SERVER_EMAIL)
        seafile_api.post_dir(repo.id, "/", "sub_dir2", SERVER_EMAIL)
        seafile_api.post_dir(repo.id, "/sub_dir1", "sub_sub_dir3", SERVER_EMAIL)

        f = tempfile.NamedTemporaryFile()
        os.chmod(f.name, 0o777)
        f.write(b'Text2')
        f.flush()

        seafile_api.post_file(repo.id, f.name, "/sub_dir1", "file_in_dir1.txt", SERVER_EMAIL)
        f.close()

        f = tempfile.NamedTemporaryFile()
        os.chmod(f.name, 0o777)
        f.write(b'Text3')
        f.flush()

        seafile_api.post_file(repo.id, f.name, "/sub_dir2", "file_in_dir2.txt", SERVER_EMAIL)
        f.close()

        f = tempfile.NamedTemporaryFile()
        os.chmod(f.name, 0o777)
        f.write(b'Text4')
        f.flush()
        # os.chmod(f.name, 0666)

        seafile_api.post_file(repo.id, f.name, "/sub_dir1/sub_sub_dir3", "file_in_dir3.txt", SERVER_EMAIL)
        f.close()

        resp = check_keeper_repo_archiving_status(repo.id, SERVER_EMAIL, 'is_snapshot_archived')
        print(resp)
        assert 'Cannot check archiving status of the snapshot.' == resp['error']

        # resp = check_keeper_repo_archiving_status(repo.id, SERVER_EMAIL, 'get_quota')
        # print(resp)
        # assert 'Cannot get archiving quota.' in resp['error']


        # arch_mgr.archive_repo(repo)
        #
        # path = arch_mgr.get_archive_path(seafile_api.get_repo_owner(repo.id), repo.id, 1)


        # assert os.path.isfile(path)
        # assert os.path.getsize(path)>0

        #clean up
        # os.remove(path)
        # shutil.rmtree(os.path.dirname(path))
        sleep(5)

    @pytest.mark.skip
    def test_huge_repo_archiving():
        """TODO: test_huge_repo_archiving

        """
        repo_id = '8c8752f3-7f00-45ef-af9c-8f4bf29c1662'
        repo = seafile_api.get_repo(repo_id)
        assert not repo is None

        start = datetime.now()

        arch_mgr.archive_repo(repo)

        print(datetime.now() - start)

        path = arch_mgr.get_archive_path(seafile_api.get_repo_owner(repo.id), repo.id, 1)

        assert os.path.isfile(path)
        assert os.path.getsize(path)>0

    @pytest.mark.skip
    def test_new_archiving(mocker):

        try:
            # config_file = get_config(os.path.join(os.environ['SEAFILE_CENTRAL_CONF_DIR'], 'seafevents.conf'))
            # keeper_config = get_keeper_archiving_conf(config_file)
            # for key in ('enabled', 'workers', 'archiving_storage', 'archive-max-size', 'archives-per-library',):
                # assert key in keeper_config

            # keeper_archiving = KeeperArchiving(keeper_config)

            # if keeper_archiving and keeper_archiving.is_enabled():
                # keeper_archiving.start()

            # keeper_archiving.start()

            # send_mail_mock = mocker.patch('django.core.mail.message.EmailMessage.send')
            # with mock.patch('django.core.mail.message.EmailMessage') as mocked_email:
            # with mock.patch('seahub.utils.EmailMessage') as mocked_email:
            # with mock.patch('post_office.models.EmailMessage') as mocked_email:
            # with mock.patch('django.core.mail.EmailMessage') as mocked_email:
            with mock.patch('seafevents.tasks.seahub_email_sender.SendSeahubEmailTimer') as mocked_email:

                repo_id = '1c13f29b-f4bc-45d6-bfbb-6974320f04ec'
                owner = 'makarenko@mpdl.mpg.de'
                # owner = 'vlamak868@gmail.com'

                resp1 = add_keeper_archiving_task(repo_id, owner)
                print(resp1.__dict__)
                # sleep(10)

                # repo_id = 'bdca5491-e60f-413a-af5f-33003bca2292'
                # resp2 = add_keeper_archiving_task(repo_id, owner)
                # print(resp2.__dict__)


                sleep(5)
                # resp1 = query_keeper_archiving_status(resp1.repo_id, resp1.version)
                # print(resp1.__dict__)


                resp = get_keeper_archiving_quota(repo_id, owner)
                print(resp.__dict__)


                # sleep(5)
                # resp2 = query_keeper_archiving_status(resp2.repo_id, resp2.version)
                # print(resp2.__dict__)

                # mocked_email.send_seahub_email.assert_called()
            # print(query_keeper_archiving_status(task2.repo_id, task2.version))
            # sleep(10)

            # keeper_archiving.stop()
            # ret = query_keeper_archiving_status(repo_id)
            # print(ret)

            # print(threading.enumerate())

        finally:
            pass


