import logging
from seahub.api2.utils import json_response
from seahub import settings

from seafobj import commit_mgr, fs_mgr
from seaserv import seafile_api, get_repo

from time import sleep
from datetime import datetime
import os
import tarfile

import threading
import Queue

from keeper.common import get_logger
# from keeper.models import BCertificate
# from seahub.notifications.models import UserNotification
# from seahub.utils import send_html_email, get_site_name
# from django.utils.translation import ugettext as _

MSG_TYPE_KEEPER_ARCHIVING_MSG = 'archiving_msg'

STORAGE_PATH = '/srv/web/seafile/tmp/hpss'

ARCH_LOG = settings.KEEPER_LOG_DIR + '/keeper.archiving.log'

logger = get_logger('keeper.archiving', ARCH_LOG)

BUF_SIZE = 5120000  # 5MB chunks

class Job:

    """Docstring for Job. """

    def __init__(self, repo_id):
        self.repo_id = repo_id
        print("New archiving job for repo {}".format(repo_id))
        return


arch_queue = Queue.Queue()

def process_job(q):
    while True:
        next_job = q.get()
        msg = 'Processing job for repo {}'.format(next_job.repo_id)
        print(msg)
        logger.info(msg)
        sleep(10)
        q.task_done()

workers = [
    threading.Thread(target=process_job, args=(arch_queue,)),
]


for w in workers:
    w.setDaemon(True)
    w.start()


def get_root_dir(repo):
    """
    Get root commit dir
    """
    commits = seafile_api.get_commit_list(repo.id, 0, 1)
    commit = commit_mgr.load_commit(repo.id, repo.version, commits[0].id)
    return fs_mgr.load_seafdir(repo.id, repo.version, commit.root_id)


# def copy_file(dir, fn, path):
def copy_dirent(obj, repo, owner, path):
    """
    Copies the files from Object Storage to local filesystem
    dir - SeafDir object
    fn - file name to be copied
    path - path in local file system where fn should be saved
    """

    if obj.is_dir():
        # print(obj.get_files_list())
        # print(fs_mgr.obj_store.__dict__)
        dpath = path + os.sep + obj.name
        d = fs_mgr.load_seafdir(repo.id, repo.version, obj.id)
        for dname, dobj in d.dirents.items():
            copy_dirent(dobj, repo, owner, dpath)
        # for sub_dir in d.get_subdirs_list():
            # print(sub_dir)
            # # copy_dirent(sub_dir)
        # for file in obj.get_files_list():
            # # copy_dirent(file)

    elif obj.is_file():
        plist = [p for p in path.split(os.sep) if p]
        absdirpath = os.path.join(STORAGE_PATH, owner, repo.id, *plist)
        if not os.path.exists(absdirpath):
            os.makedirs(absdirpath)
        seaf = fs_mgr.load_seafile(repo.id, repo.version, obj.id)
        to_path = os.path.join(absdirpath, obj.name)
        write_seaf_to_path(seaf, to_path)
        print(u"File: {} copied to {}".format(obj.name, to_path))

    else:
        print(u"Wrong object: {}".format(obj))


def write_seaf_to_path(seaf, to_path):
    """TODO:
    """
    stream = seaf.get_stream()

    with open(to_path, "a") as target:
        while True:
            data = stream.read(BUF_SIZE)
            if not data:
                break
            target.write(data)

        target.close()


def get_archive_path(owner, repo_id, ver):
    """TODO: Docstring for get_archive_path.
    :returns: TODO
    """
    return os.path.join(STORAGE_PATH, owner, "{}_ver{}.tar.gz".format(repo_id, ver))

def archive_repo(repo):
    """TODO: Docstring for function.

    :arg1: TODO
    :returns: TODO

    """
    seaf_dir = get_root_dir(repo)
    owner = seafile_api.get_repo_owner(repo.id)
    for name, obj in seaf_dir.dirents.items():
        copy_dirent(obj, repo, owner, '')

    #create tar.gz
    src_path = os.path.join(STORAGE_PATH, owner, repo.id)
    with tarfile.open(get_archive_path(owner, repo.id, 1), mode='w:gz', format=tarfile.PAX_FORMAT) as archive:
        archive.add(src_path, '')
        archive.close()


def get_file_by_path(repo_id, path):
    repo = seafile_api.get_repo(repo_id)
    dir = fs_mgr.load_seafdir(repo.id, repo.version, get_commit_root_id(repo_id))
    paths = filter(None, path.split("/"))
    for path in paths:
        dir = dir.lookup(path)
    return dir

def get_commit_id(repo_id):
    repo = seafile_api.get_repo(repo_id)
    commits = seafile_api.get_commit_list(repo.id, 0, 1)
    return commits[0].id

def get_commit_root_id(repo_id):
    repo = seafile_api.get_repo(repo_id)
    commits = seafile_api.get_commit_list(repo.id, 0, 1)
    commit = commit_mgr.load_commit(repo.id, repo.version, commits[0].id)
    return commit.root_id


