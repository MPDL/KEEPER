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



def test_archiving_queue():

    # import logging
    # logger = logging.getLogger()
    # logger.setLevel(logging.DEBUG)
    # fh = logging.FileHandler('arch.log')
    # fh.setLevel(logging.DEBUG)
    # logger.addHandler(fh)

    # logger.debug("HERE!!!!")
    # q.join()
    from keeper.archiving.archiving_manager import Job
    q = arch_mgr.arch_queue

    q.put(Job("1"))
    q.put(Job("2"))
    q.put(Job("3"))

    # q.join()

    q.put(Job("4"))
    q.put(Job("5"))
    q.put(Job("6"))

    # q.join()
