import uuid
import pytest
from time import sleep
import tempfile
from seaserv import seafile_api, get_repo
from seafobj import commit_mgr, fs_mgr
import cdc.cdc_manager
from cdc.cdc_manager import quote_arg, get_user_name, CDC_PDF_PREFIX
from default_library_manager import copy_keeper_default_library, get_keeper_default_library
from seahub.settings import SERVER_EMAIL, ARCHIVE_METADATA_TARGET




def test_quote_arg():
    assert quote_arg('aaa') == "\"aaa\""

@pytest.mark.skip
def test_get_user_name():
    assert get_user_name('vlamak868@gmail.com') == 'Vladislav'

def test_cdc_completely(monkeypatch):
    """TODO: Docstring for function.
    """

    REPO_NAME = "CDC_TEST_REPO-" + str(uuid.uuid4())
    repo_id = seafile_api.create_repo(REPO_NAME, "This is Description", 'vlamak868@gmail.com', passwd=None)
    repo = seafile_api.get_repo(repo_id)

    # seafile_api does not fire up a libevent, thus the direct call of
    # copy_keeper_default_library should be used

    # check def_lib files avialable
    kdl = get_keeper_default_library()
    if kdl:
        check_set = set([d.obj_name for d in kdl['dirents']])
    else:
        pytest.fail(msg="Default Library is empty!")

    # copy files to lib
    copy_keeper_default_library(repo_id)
    sleep(2)

    # get copied files
    commits = seafile_api.get_commit_list(repo.id, 0, 1)
    commit = commit_mgr.load_commit(repo.id, repo.version, commits[0].id)
    dir = fs_mgr.load_seafdir(repo.id, repo.version, commit.root_id)

    # check copied files
    for fn in check_set:
        if not dir.lookup(fn):
            pytest.fail("Cannot find %s!" % fn)

    # add one new file
    f = tempfile.NamedTemporaryFile()
    f.write('Text')
    f.flush()

    seafile_api.post_file(repo.id, f.name, "/", "some_file.txt", SERVER_EMAIL)
    f.close()

    f = tempfile.NamedTemporaryFile()
    f.write("""##Title
Title

## Author
Lastname, Firstname; Affiliation1

## Description
Description

## Year
2010
""")
    f.flush()

    seafile_api.put_file(repo.id, f.name, "/", ARCHIVE_METADATA_TARGET, SERVER_EMAIL, None)
    f.close()


    sleep(5)
    # check cdc pdf exists

    commits = seafile_api.get_commit_list(repo.id, 0, 1)
    commit = commit_mgr.load_commit(repo.id, repo.version, commits[0].id)
    dir = fs_mgr.load_seafdir(repo.id, repo.version, commit.root_id)
    file_names = [f.name for f in dir.get_files_list()]
    if not any(file_name.startswith(CDC_PDF_PREFIX) and file_name.endswith('.pdf') for file_name in file_names):
        print file_names
        pytest.fail("Cannot find cdc pdf in repo %s!" % REPO_NAME)


    print seafile_api.remove_repo(repo.id)

