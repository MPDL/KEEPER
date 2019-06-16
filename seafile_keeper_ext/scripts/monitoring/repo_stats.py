#!/usr/bin/env python

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "seahub.settings")
import django
django.setup()

from seaserv import seafile_api, ccnet_api

HEADER = "ID,Name,Owner,Encrypted,# of files,# of commits,Size"
FORMATTER = "{},{},{},{},{},{},{}"

def get_stats_repo(repo_id):
    '''
    Get single repo stats
    '''

    try:
        repo = seafile_api.get_repo(repo_id)
    except Exception as e:
        print ('Error: {}'.format(e))
        return

    # print(repo.__dict__)
    # group_ids = seafile_api.get_shared_group_ids_by_repo(repo_id)
    # group = ccnet_api.get_group(int(group_ids[0]))
    # print(
        # ccnet_api.get_group(int(group_ids[0])).group_name
    # )
    # return

    print(HEADER)
    print(FORMATTER.format(
        repo_id,
        repo.name.encode('utf-8'),
        seafile_api.get_repo_owner(repo_id),
        repo.encrypted,
        repo.file_count,
        len(seafile_api.get_commit_list(repo_id, 0, -1)),
        repo.size,
    ))


def get_stats_repo_list():
    '''
    Get stats for complete list of keeper repos
    Sorted by number of commits, desc
    '''

    try:
        repo_list = seafile_api.get_repo_list(0, -1)
    except Exception as e:
        print ('Error: {}'.format(e))
        return

    # print("KEEPER repos #: {} ".format(len(repo_list)))

    repos = []
    for r in repo_list:
        repos.append({"repo": r,
                      "owner": seafile_api.get_repo_owner(r.id),
                      "commits_num": len(seafile_api.get_commit_list(r.id, 0, -1)),
                      } )


    repos_sorted_commits_num = sorted(repos, key = lambda i: i['commits_num'],reverse=True)

    # print(repos_sorted_commits_num)

    print(HEADER)
    for r in repos_sorted_commits_num:
        rr = r['repo']
        # print(vars(rr))
        print(FORMATTER.format(
            rr.id,
            rr.name.encode('utf-8'),
            r['owner'],
            rr.encrypted,
            rr.file_count,
            r['commits_num'],
            rr.size,
        ))



if __name__ == "__main__":
    # get_stats_repo_list()
    # get_stats_repo('12cb8b36-8d6c-45bb-8a4f-e9196ad45260')

