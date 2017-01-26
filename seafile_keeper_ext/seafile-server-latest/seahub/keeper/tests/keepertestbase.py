# -*- coding: utf-8 -*-
import pytest

from seahub.base.accounts import User
from seahub.profile.models import Profile
from uuid import uuid4

from seaserv import seafile_api

@pytest.fixture(scope='function')
def create_tmp_user():
    """Create new random user"""
    email = uuid4().hex + '@test.com'
    kwargs = {
        'email': email,
        'is_staff': False,
        'is_active': True
    }
    User.objects.create_user(password='secret', **kwargs)
    yield email
    # teardown code
    User.objects.get(email).delete()

@pytest.fixture(scope='function')
def create_tmp_user_with_profile(create_tmp_user):
    """Create tmp user with profile"""
    Profile.objects.add_or_update(create_tmp_user, 'Random Nick ' + uuid4().hex)
    yield create_tmp_user
    # teardown code
    Profile.objects.delete_profile_by_user(create_tmp_user)

@pytest.fixture(scope='function')
def create_tmp_repo(create_tmp_user):
    """Create new random library"""
    REPO_NAME = "TEST_TMP_REPO-" + uuid4().hex
    repo_id = seafile_api.create_repo(REPO_NAME, "Tmp description", create_tmp_user, passwd=None)
    repo = seafile_api.get_repo(repo_id)
    yield repo
    # teardown code
    if repo and repo.id:
        seafile_api.remove_repo(repo.id)
