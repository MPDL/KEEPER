#!/usr/bin/env python

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "seahub.settings")
import django
django.setup()

from seaserv import seafile_api
from keeper.models import Catalog
# from keeper.models import DoiRepo
from seafevents.keeper_archiving.db_oper import DBOper


def update_catalog_repo_name():
    '''
    Update Catalog.repo_name

    '''
    try:
        for c in Catalog.objects.get_all():
            r = seafile_api.get_repo(c.repo_id)
            # print(c.repo_id)
            if r is not None:
                print(u"ObjectStorage repo_name: {}".format(r.name))
                Catalog.objects.add_or_update_by_repo_id(c.repo_id, c.owner, c.md, r.name)
            else:
                # dois = DoiRepo.objects.get_doi_repos_by_repo_id(c.repo_id)
                # if dois is not None and len(dois) > 0:
                    # dois = sorted(dois, key = lambda d: d['created'], reverse=True)
                    # Catalog.objects.add_or_update_by_repo_id(c.repo_id, c.owner, c.md, dois[0].repo_name)
                # else:
                db = DBOper()
                a = db.get_latest_archive(c.repo_id)
                if a is not None and a.repo_name:
                    print(u"KeeperArchive repo_name: {}".format(a.repo_name))
                    Catalog.objects.add_or_update_by_repo_id(c.repo_id, c.owner, c.md, a.repo_name)
                else:
                    print("Cannot populate repo_name for {}: the repo has been deleted before being archived".format(c.repo_id))


    except Exception as e:
        print ('Error: {}'.format(e))


if __name__ == "__main__":
    update_catalog_repo_name()

