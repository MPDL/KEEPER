import os
import sys

import logging

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "seahub.settings") 

from seaserv import seafile_api
from seahub.settings import SERVER_EMAIL, KEEPER_DEFAUIL_LIBRARY

DEBUG = False 

if DEBUG:
    logging.basicConfig(level=logging.INFO)

def get_keeper_default_library():
    try:
        from_repos = seafile_api.get_owned_repo_list(SERVER_EMAIL)
        from_repos = [r for r in from_repos if r.name == KEEPER_DEFAUIL_LIBRARY]
        if from_repos:
            from_repo_id = from_repos[0].id
            return { 'repo_id': from_repo_id, 'dirents': seafile_api.list_dir_by_path(from_repo_id, '/') }
        else:
            raise Exception("Cannot find KEEPER_DEFAULT_LIBRARY repo in admin libraries, please install!")
    except Exception as err:
        logging.error("Cannot find KEEPER_DEFAUIL_LIBRARY dirents, err: " + str(err))
        return None

 

def copy_keeper_default_library(to_repo_id):
    logging.info("Add KEEPER_DEFAUIL_LIBRARY files to the repo %s..." % to_repo_id)

    try:
        kdl = get_keeper_default_library()
        if kdl:
            for e in kdl['dirents']:
                obj_name = e.obj_name
                seafile_api.copy_file(kdl['repo_id'], '/', obj_name, to_repo_id, '/',
                                  obj_name, SERVER_EMAIL, 0, 0)
            logging.info("KEEPER_DEFAULT_LIBRARY has been successfully copied to repo: " + to_repo_id)
    except Exception as err:
        logging.error("Cannot copy KEEPER_DEFAUIL_LIBRARY, err: " + str(err))


if DEBUG: 
    copy_keeper_default_library('d1fe0133-25f2-4ce3-b5c1-055f1ec9716d') 
