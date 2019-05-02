#!/usr/bin/env python

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "seahub.settings")
import django
django.setup()

from seaserv import seafile_api


def get_commits_per_repo():
    '''
    Get sorted by number of commits list of repos, desc
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
                      "commits_num": len(seafile_api.get_commit_list(r.id, 0, -1)) } )


    repos_sorted_commits_num = sorted(repos, key = lambda i: i['commits_num'],reverse=True)

    # HEADER
    print("repo ID,name,owner,# of files,# of commits")
    for r in repos_sorted_commits_num:
        rr = r['repo']
        # print(vars(rr))
        print("{},{},{},{},{} ".format(
            rr.id, rr.name.encode('utf-8'), r['owner'], rr.file_count, r['commits_num']))



if __name__ == "__main__":
    get_commits_per_repo()
