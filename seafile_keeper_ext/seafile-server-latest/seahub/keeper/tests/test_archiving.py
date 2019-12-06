import pytest

import seahub.base
import django
django.setup()

import mock

import os
import shutil
import tempfile

from seaserv import seafile_api
from seahub.settings import SERVER_EMAIL

from keepertestbase import create_tmp_user_with_profile, create_tmp_user, create_tmp_repo

import keeper.archiving.archiving_manager as arch_mgr

from datetime import datetime

from seafevents.keeper_archiving import KeeperArchiving
from seafevents.keeper_archiving.task_manager import task_manager, Worker
from seafevents.keeper_archiving.config import get_keeper_archiving_conf
from seafevents.utils import get_config
from keeper.utils import query_keeper_archiving_status,\
        add_keeper_archiving_task, get_keeper_archiving_quota
from time import sleep

import json
from seahub.notifications.models import UserNotification

from seafevents.keeper_archiving import task_manager as arch_task_mgr

@pytest.mark.skip
def test_tmp_repo_archiving(create_tmp_repo):
    """TODO: Docstring for test_archiving.

    :create_tmp_repo: TODO
    :returns: TODO

    """
    repo = create_tmp_repo
    assert not repo is None

    f = tempfile.NamedTemporaryFile()
    f.write('Text')
    f.flush()
    # os.chmod(f.name, 0666)

    seafile_api.post_file(repo.id, f.name, "/", "some_file_in_root.txt", SERVER_EMAIL)
    f.close()


    seafile_api.post_dir(repo.id, "/", "sub_dir1", SERVER_EMAIL)
    seafile_api.post_dir(repo.id, "/", "sub_dir2", SERVER_EMAIL)
    seafile_api.post_dir(repo.id, "/sub_dir1", "sub_sub_dir3", SERVER_EMAIL)

    f = tempfile.NamedTemporaryFile()
    f.write('Text2')
    f.flush()

    seafile_api.post_file(repo.id, f.name, "/sub_dir1", "file_in_dir1.txt", SERVER_EMAIL)
    f.close()

    f = tempfile.NamedTemporaryFile()
    f.write('Text3')
    f.flush()

    seafile_api.post_file(repo.id, f.name, "/sub_dir2", "file_in_dir2.txt", SERVER_EMAIL)
    f.close()

    f = tempfile.NamedTemporaryFile()
    f.write('Text4')
    f.flush()
    # os.chmod(f.name, 0666)

    seafile_api.post_file(repo.id, f.name, "/sub_dir1/sub_sub_dir3", "file_in_dir3.txt", SERVER_EMAIL)
    f.close()

    arch_mgr.archive_repo(repo)

    path = arch_mgr.get_archive_path(seafile_api.get_repo_owner(repo.id), repo.id, 1)


    assert os.path.isfile(path)
    assert os.path.getsize(path) > 0L

    #clean up
    # os.remove(path)
    # shutil.rmtree(os.path.dirname(path))



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
    assert os.path.getsize(path) > 0L


# @pytest.mark.skip
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


