# -*- coding: utf-8 -*-
import pytest
from time import sleep
import tempfile
import json
from seaserv import seafile_api, get_repo
from seafobj import commit_mgr, fs_mgr
import cdc.cdc_manager
from cdc.cdc_manager import quote_arg, get_user_name, validate_institute, CDC_PDF_PREFIX
from default_library_manager import copy_keeper_default_library, get_keeper_default_library
from seahub.settings import SERVER_EMAIL, ARCHIVE_METADATA_TARGET

from seahub.base.accounts import User
from seahub.profile.models import Profile
from uuid import uuid4

import django
django.setup()


def test_quote_arg():
    assert quote_arg('aaa') == "\"aaa\""

@pytest.fixture(scope='function')
def create_tmp_user(request):
    """Create new random user"""
    email = uuid4().hex + '@test.com'
    kwargs = {
        'email': email,
        'is_staff': False,
        'is_active': True
    }
    user = User.objects.create_user(password='secret', **kwargs)
    yield email
    # teardown code
    User.objects.get(email).delete()

@pytest.fixture(scope='function')
def create_tmp_repo(create_tmp_user):
    """Create new random library"""
    REPO_NAME = "CDC_TEST_REPO-" + uuid4().hex
    repo_id = seafile_api.create_repo(REPO_NAME, "This is Description", create_tmp_user, passwd=None)
    repo = seafile_api.get_repo(repo_id)
    yield repo
    # teardown code
    if repo and repo.id:
        seafile_api.remove_repo(repo.id)


def test_get_user_name(create_tmp_user):
    """Test get user/profile with unicode
    """

    email = create_tmp_user
    print email
    assert email == Profile.objects.get_contact_email_by_user(email)

    nick = u"Vlad Влад Üäß 金属と金属の掛け合わせ"
    p = Profile.objects.add_or_update(email, nick)
    assert p.nickname == nick

    nick_from_db = get_user_name(email)
    assert nick == nick_from_db

    Profile.objects.delete_profile_by_user(email)

    print json.dumps([nick_from_db], ensure_ascii = False, indent=4, sort_keys=True, separators=(',', ': '))


def test_validate_institute():
    assert validate_institute("MPG; MPE; Name, FirstName")
    assert validate_institute("Institute;Department;Name,F."), "no spaces"
    assert not validate_institute("Institute Department Name,F."), "No semicolon"


def test_cdc_completely(create_tmp_repo):
    """Test CDC generation, complete workflow
    """

    repo = create_tmp_repo

    # TEST DEFAULT LIBRARY
    """check default library files are avialable"""
    kdl = get_keeper_default_library()
    if kdl:
        check_set = set([d.obj_name for d in kdl['dirents']])
    else:
        pytest.fail(msg="Default Library is empty!")

    """copy library default files to lib"""
    copy_keeper_default_library(repo.id)
    sleep(2)

    # get copied files
    commits = seafile_api.get_commit_list(repo.id, 0, 1)
    commit = commit_mgr.load_commit(repo.id, repo.version, commits[0].id)
    dir = fs_mgr.load_seafdir(repo.id, repo.version, commit.root_id)

    # check copied files
    for fn in check_set:
        if not dir.lookup(fn):
            pytest.fail("Cannot find %s!" % fn)

    # TEST CDC GENERATION
    """add some txt file"""
    f = tempfile.NamedTemporaryFile()
    f.write('Text')
    f.flush()

    seafile_api.post_file(repo.id, f.name, "/", "some_file.txt", SERVER_EMAIL)
    f.close()

    """update md file with correct fields"""
    f = tempfile.NamedTemporaryFile()
    f.write("""##Title
Title

## Author
Lastname, Firstname; Affiliation1

## Description
Description

## Year
2010

## Institute
INS; Department; Name, Fname
""")
    f.flush()

    seafile_api.put_file(repo.id, f.name, "/", ARCHIVE_METADATA_TARGET, SERVER_EMAIL, None)
    f.close()

    sleep(5)


    """check cdc pdf exists"""
    commits = seafile_api.get_commit_list(repo.id, 0, 1)
    commit = commit_mgr.load_commit(repo.id, repo.version, commits[0].id)
    dir = fs_mgr.load_seafdir(repo.id, repo.version, commit.root_id)
    file_names = [f.name for f in dir.get_files_list()]
    if not any(file_name.startswith(CDC_PDF_PREFIX) and file_name.endswith('.pdf') for file_name in file_names):
        print file_names
        pytest.fail("Cannot find cdc pdf in repo %s!" % REPO_NAME)
