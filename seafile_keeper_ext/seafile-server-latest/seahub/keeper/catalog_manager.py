#!/usr/bin/env python

from seaserv import get_commits, get_commit, get_repo_owner, seafile_api
from seafobj import fs_mgr
from seahub.settings import ARCHIVE_METADATA_TARGET

from keeper.cdc.cdc_manager import is_certified_by_repo_id, parse_markdown, get_user_name   

import logging
import json

DEBUG = False

MAX_INT = 2147483647

def trim_by_len(str, max_len, suffix="..."):
    if str:
        str = str.strip()
        if str and len(str) > max_len:
            str = str[0:max_len] + suffix
        str = unicode(str, "utf-8")
    return str 

def strip_uni(str):
    if str:
        str = unicode(str.strip(), "utf-8")
    return str 



def get_catalog():

    catalog = []

    repos_all = seafile_api.get_repo_list(0, MAX_INT)
    #repos_all = [seafile_api.get_repo('a6d4ae75-b063-40bf-a3d9-dde74623bb2c')]

    for repo in repos_all:

        try:
            proj = {}
            proj["id"] = repo.id
            proj["name"] = repo.name
            email = get_repo_owner(repo.id)
            proj["owner"] = email
            user_name = get_user_name(email)
            if user_name != email:
                proj["owner_name"] = user_name 
            proj["in_progress"] = True

            commits = get_commits(repo.id, 0, 1)
            commit = get_commit(repo.id, repo.version, commits[0].id)
            dir = fs_mgr.load_seafdir(repo.id, repo.version, commit.root_id)
            file = dir.lookup(ARCHIVE_METADATA_TARGET)
            if file:
                md = parse_markdown(file.get_content())
                if md:
                    # Author
                    a = md.get("Author")
                    if a:
                        a_list = strip_uni(a.strip()).split('\n')
                        authors = []
                        for _ in a_list:
                            author = {}
                            aa = _.split(';')
                            author['name'] = aa[0]
                            if len(aa) > 1 and aa[1].strip():
                                author['affs'] = [x.strip() for x in aa[1].split('|')]
                                author['affs'] = [x for x in author['affs'] if x ]
                            authors.append(author)
                        if a:
                            proj["authors"] = authors

                    # Description
                    d = strip_uni(md.get("Description"))
                    if d:
                        proj["description"] = d

                    # Comments
                    c = strip_uni(md.get("Comments"))
                    if c:
                        proj["comments"] = c

                    #Title
                    t = strip_uni(md.get("Title"))
                    if t:
                        proj["title"] = t
                        del proj["in_progress"]
                    
                    proj["is_certified"] = is_certified_by_repo_id(repo.id)
            else:
                if DEBUG:
                    print "No %s for repo %s found" % (ARCHIVE_METADATA_TARGET, repo.name)
            catalog.append(proj)    

        except Exception as err:
            msg = "repo_name: %s, id: %s, err: %s" % ( repo.name, repo.id, str(err) ) 
            logging.error (msg)
            if DEBUG:
                print msg

    return catalog


if DEBUG:
    print json.dumps(get_catalog(), indent=4, sort_keys=True, separators=(',', ': '))
