#!/usr/bin/env python

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "seahub.settings")
import django
django.setup()

import json

from seaserv import seafile_api, ccnet_api
from seahub.utils.timeutils import timestamp_to_isoformat_timestr
from seahub.utils.file_revisions import get_file_revisions_after_renamed, get_file_revisions_within_limit
from pysearpc import SearpcError, SearpcObjEncoder
from seahub.base.templatetags.seahub_tags import email2nickname
from seahub.profile.models import Profile, DetailedProfile
from seahub.api2.endpoints.file_history import get_file_history_info

def get_file_history(repo_id, path, commit_id):
    '''
    Get file revisions history via get_file_revisions_within_limit method
    '''
    if not commit_id:
        repo = seafile_api.get_repo(repo_id)
        commit_id = repo.head_cmmt_id

    file_revisions, next_start_commit = get_file_revisions_within_limit(
        repo_id, path, commit_id, -1)

    result = []
    for commit in file_revisions:
        info = get_file_history_info(commit, 32)
        info['path'] = path
        result.append(info)

    print(json.dumps({"data": result, "next_start_commit": next_start_commit},
        cls=SearpcObjEncoder, indent=2))

    if next_start_commit:
        # get_file_history(repo_id, path, next_start_commit)
        get_file_history(repo_id, file_revisions[-1].rev_renamed_old_path or path, next_start_commit)


def get_file_full_history(repo_id, path):
    '''
    Get file revisions history via get_file_revisions_after_renamed method
    '''

    commits = get_file_revisions_after_renamed(repo_id, path)

    for commit in commits:
        creator_name = commit.creator_name

        user_info = {}
        user_info['email'] = creator_name
        user_info['name'] = email2nickname(creator_name)
        user_info['contact_email'] = Profile.objects.get_contact_email_by_user(creator_name)
        commit._dict['ctime_iso'] = timestamp_to_isoformat_timestr(commit.ctime)

        commit._dict['user_info'] = user_info

    print('############### get_file_revisions_after_renamed ###>')
    print(json.dumps({"commits": commits},
        cls=SearpcObjEncoder, indent=2))

    print('############### get_file_revisions ###>')
    get_file_history(repo_id, path, None)


if __name__ == "__main__":
    # get_file_full_history('01e838bb-d44e-4544-a700-921cc8e79927', 'WS5 Publishing Full Gold/Gold Existing WOA Accounts/Germany Wiley Open Access Accounts_Shared.xlsx')
    get_file_full_history('01e838bb-d44e-4544-a700-921cc8e79927', '/WS5 Publishing- Full Gold/Gold_APC_Price_List/Wiley_Open_Access_APC_List_20190217.xls')
    # get_file_full_history('01e838bb-d44e-4544-a700-921cc8e79927', '/WS5 Publishing Full Gold/Gold APC Price List/Wiley_Open_Access_APC_List_20190217.xlsx')
    # get_file_full_history('12cb8b36-8d6c-45bb-8a4f-e9196ad45260', '/Fehlende Einrichtungen12/DEAL_Missing_Institution.xlsx')
    # get_file_full_history('a0b4567a-8f72-4680-8a76-6100b6ebbc3e', '/Keeper Debugging/2019-05-02_Inga/analyse.md')

