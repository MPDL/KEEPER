#!/usr/bin/env python

from seaserv import seafile_api
from seafobj import commit_mgr, fs_mgr
import logging
import django
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "seahub.settings")
django.setup()

HEADER = "ID,Name,Owner,Encrypted,# of files,# of commits,Size"
FORMATTER = "{},{},{},{},{},{},{}"

logger = logging.getLogger(__name__)
logger.addHandler(logging.FileHandler("file_size.log"))


def get_commit(repo):
    """
    Get commit
    """
    try:
        commits = seafile_api.get_commit_list(repo.id, 0, 1)
        commit = commit_mgr.load_commit(repo.id, repo.version, commits[0].id)
        return commit
    except Exception as e:
        logger.error(e)


def _load_seafdir(repo, obj_id):
    return fs_mgr.load_seafdir(repo.id, repo.version, obj_id)


def get_repo_files(repo):
    """Docstring for copy_repo_into_tmp_dir.
    """

    seaf_dir = _load_seafdir(repo, get_commit(repo).root_id)

    def read_dirent(obj, repo):
        """
        """
        if obj.is_dir():
            d = _load_seafdir(repo, obj.id)
            for _, dobj in list(d.dirents.items()):
                read_dirent(dobj, repo)
        elif obj.is_file():
            seaf = fs_mgr.load_seafile(repo.id, repo.version, obj.id)
            print(f'"{repo.id}","{obj.name}",{obj.size}')
        else:
            logger.warning(f'Wrong seafile object: {obj}')

    # start traversing repo
    for name, obj in list(seaf_dir.dirents.items()):
        read_dirent(obj, repo)


def get_stats_repo_list():
    '''
    Get stats for complete list of keeper repos
    Sorted by number of commits, desc
    '''

    try:
        repo_list = seafile_api.get_repo_list(0, -1)
    except Exception as e:
        logger.error(e)
        return

    # print("KEEPER repos #: {} ".format(len(repo_list)))
    print('"repo_id","file_name",file_size')

    for r in repo_list:
        try:
            get_repo_files(r)
        except Exception as e:
            logger.error(f"Cannot travers repo id: {r.id}, name: {r.name}", e)


if __name__ == "__main__":
    get_stats_repo_list()
