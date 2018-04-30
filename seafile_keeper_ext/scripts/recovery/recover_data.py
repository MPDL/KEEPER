# -*- coding: utf-8 -*-
#!/usr/bin/env python

import sys
import os
import json

from seaserv import get_repo, get_commit, seafserv_threaded_rpc, seafile_api
from seafobj import commit_mgr, fs_mgr
from seahub.utils import get_file_update_events
from seahub.utils.timeutils import utc_to_local

import seafevents
from seahub.utils import SeafEventsSession
from seafevents.events.models import FileUpdate
from sqlalchemy import desc

from collections import defaultdict

def get_root_dir(repo):
    """
    Get root commit dir
    """
    commits = seafile_api.get_commit_list(repo.id, 0, 1)
    commit = commit_mgr.load_commit(repo.id, repo.version, commits[0].id)
    return fs_mgr.load_seafdir(repo.id, repo.version, commit.root_id)


def get_diff(repo_id, arg1, arg2):
    """
    Get diffs classified by modification type
    """
    lists = {'new': [], 'removed': [], 'renamed': [], 'modified': [],
             'newdir': [], 'deldir': []}

    diff_result = seafserv_threaded_rpc.get_diff(repo_id, arg1, arg2)
    if not diff_result:
        return lists

    for d in diff_result:
        if d.status == "add":
            lists['new'].append(d.name)
        elif d.status == "del":
            lists['removed'].append(d.name)
        elif d.status == "mov":
            lists['renamed'].append(d.name + " ==> " + d.new_name)
        elif d.status == "mod":
            lists['modified'].append(d.name)
        elif d.status == "newdir":
            lists['newdir'].append(d.name)
        elif d.status == "deldir":
            lists['deldir'].append(d.name)

    # clean empty lists
    lists = dict([(vkey, vdata) for vkey, vdata in lists.iteritems() if (vdata)])

    return lists


def copy_file(dir, fn, path):
    """
    Copies the files from Object Storage to local filesystem
    dir - SeafDir object
    fn - file name to be copied
    path - path in local file system where fn should be saved
    """

    dirname = os.path.dirname(fn)
    # if fn is has diraneme, travers throgh subdirs in SeafDir
    if dirname:
        d = dir;
        for sub_dir in dirname.split('/'):
            d = d.lookup(sub_dir)
        copy_file(d, os.path.basename(fn), path + "/" + dirname)

    else:
        file = dir.lookup(fn)
        if file:
            # create path in local filesystem
            if not os.path.exists(path):
                os.makedirs(path)

            #write file
            with open(path + "/" + fn, "w") as f:
                f.write(file.get_content())
                f.close()
                print(u"File: {} is found in path:{} and copied.".format(fn, path))
        else:
            print(u"File: {} is not found in path: {}".format(fn, path))




def recover_data():

    # open DB session
    session = SeafEventsSession()
    # QUERY CONDITIONS
    # Searc in FileUpdate Table
    # timestamp between '2018-02-02 05:05' and '2018-02-02 16:00'
    # q = session.query(FileUpdate).filter(FileUpdate.timestamp.between('2018-02-02 05:05','2018-02-02 16:00'))
    q = session.query(FileUpdate).filter(FileUpdate.timestamp.between('2018-03-31 05:05:08','2018-03-31 05:05:42'))
    # order by creation, desc
    q = q.order_by(desc(FileUpdate.eid))
    events = q.all()

    # Generate common data structure as dict, will be used later
    # by reports, tasks ,etc.
    users = defaultdict(list)
    if events:
        for ev in events:
            ev.repo = get_repo(ev.repo_id)
            ev.local_time = utc_to_local(ev.timestamp)
            ev.time = int(ev.local_time.strftime('%s'))
            changes = get_diff(ev.repo.repo_id, '', ev.commit_id)
            c = get_commit(ev.repo.repo_id, ev.repo.version, ev.commit_id)
            # number of changes in event
            c_num = 0
            for k in changes:
                c_num += len(changes[k])

            if c.parent_id is None:
                # A commit is a first commit only if it's parent id is None.
                changes['cmt_desc'] = repo.desc
            elif c.second_parent_id is None:
                # Normal commit only has one parent.
                if c.desc.startswith('Changed library'):
                    changes['cmt_desc'] = 'Changed library name or description'
            else:
                # A commit is a merge only if it has two parents.
                changes['cmt_desc'] = 'No conflict in the merge.'

            changes['date_time'] = str(c.ctime)

            # ev.repo is saved in the dict to make seafobj manipulation possible
            users[ev.user].append({
                'event' : { 'repo' : ev.repo, 'time' : str(ev.local_time), 'library' : ev.repo.name, 'encrypted' : ev.repo.encrypted,  'file_oper' : ev.file_oper },
                'details' : changes,
                'changes_num' : c_num
            })


    changed_files = defaultdict(dict)
    # for the moment we save modified and new files in separate dirs
    change = 'modified'
    # change = 'new'

    for key, events in users.iteritems():

        for e in events:
            if change in e['details']:
                ev = e['event']
                # encrypted libs will not be recovered
                if not ev['encrypted']:
                    lib = ev['library']
                    if not lib in changed_files[key]:
                        changed_files[key].update( { lib : { 'repo' : ev['repo'],  'files' : set(e['details'][change]) } } )
                    else:
                        changed_files[key][lib]['files'].update(e['details'][change])


        # convert sets to lists to be serialized in json
        for u in changed_files:
            for l in changed_files[u]:
                changed_files[u][l]['files'] = list(changed_files[u][l]['files'])




    # path in filesystem where the recovered files will be stored
    STORAGE_PATH = '/keeper/tmp/recovery/' + change + '/'
    # gnerate packages of changed files
    for u in changed_files:
        path = STORAGE_PATH + u
        for lib in changed_files[u]:
            dir = get_root_dir(changed_files[u][lib]['repo'])
            dest_path = path + "/" + lib
            for fn in changed_files[u][lib]['files']:
                copy_file(dir, fn, dest_path)



if __name__ == "__main__":
    recover_data()

