#!/usr/bin/env python

from seaserv import get_commits, get_commit, get_repo_owner, seafile_api
from seafobj import fs_mgr
from seahub.settings import ARCHIVE_METADATA_TARGET

from keeper.cdc.cdc_manager import is_certified_by_repo_id, parse_markdown, get_user_name   

import json

MAX_INT = 2147483647

err_list = []
catalog = []

###### START
repos_all = seafile_api.get_repo_list(0, MAX_INT)

#repos_all = [seafile_api.get_repo('bf955175-a089-4e2b-878b-2d237ad363a6')]

def trim_by_len(str, max_len, suffix="..."):
    if str:
        str = str.strip()
        if str and len(str) > max_len:
            str = str[0:max_len] + suffix
    return str

for repo in repos_all:

    try:
        proj = {}
        proj["id"] = repo.id
        proj["name"] = repo.name
        email = get_repo_owner(repo.id)
        proj["contact_email"] = email
        name = get_user_name(email)
        if name != email:
            proj["contact_name"] = name 

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
                    a = a.strip()
                    a_list = a.split('\n')
                    if len(a_list) > 5:
                        a_list = a_list[:5]
                        a_list.append("...")
                    a = "\n".join(a_list)    
                    if a:
                        proj["Author"] = a

                # Description
                d = trim_by_len(md.get("Description"), 200)
                if d:
                    proj["Description"] = unicode(d, "utf-8")

                # Comments
                c = trim_by_len(md.get("Comments"), 100)
                if c:
                    proj["Comments"] = c

                #Title
                t = trim_by_len(md.get("Title"), 200)
                if t:
                    proj["Title"] = t
                else: 
                    proj["in_progress"] = True
                
                proj["is_certified"] = is_certified_by_repo_id(repo.id)

        else:
            proj["in_progress"] = True
            print "No %s for repo %s found" % (ARCHIVE_METADATA_TARGET, repo.name)
        catalog.append(proj)    

    except Exception as err:
        print err
        err_list.append({'name:':repo.name, 'id':repo.id, 'err':str(err)})


#print "Errors:", err_list
print json.dumps(catalog, indent=4, separators=(',', ': '))


exit(0)
